"""
Embedding Service for vector computation and similarity search
Handles text embeddings, vector storage, and kNN search operations
"""

import logging
import asyncio
import hashlib
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload

from app.models.embedding import Embedding, EmbeddingCluster, SearchQuery
from app.models.trade import Trade
from app.services.openai_client import get_openai_client, EmbeddingRequest
from app.services.cache import CacheService
from app.services.schemas import SimilaritySearchRequest, SimilaritySearchResult, SimilaritySearchResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for computing and managing text embeddings"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.default_model = settings.OPENAI_EMBEDDING_MODEL
        self.default_dimensions = settings.EMBEDDING_DIMENSIONS
        
    async def compute_embedding(
        self,
        text: str,
        model: Optional[str] = None,
        dimensions: Optional[int] = None
    ) -> Optional[List[float]]:
        """
        Compute embedding for a single text
        
        Args:
            text: Text to embed
            model: Embedding model to use
            dimensions: Number of dimensions (for newer models)
            
        Returns:
            Embedding vector or None if failed
        """
        try:
            # Check cache first
            cache_key = self._get_cache_key(text, model or self.default_model, dimensions)
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
            
            openai_client = await get_openai_client()
            
            request = EmbeddingRequest(
                texts=[text],
                model=model,
                dimensions=dimensions
            )
            
            response = await openai_client.embed_texts(request)
            
            if response["success"] and response["embeddings"]:
                embedding = response["embeddings"][0]
                
                # Cache for 24 hours
                await self.cache.set(cache_key, embedding, expire=86400)
                return embedding
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to compute embedding: {e}")
            return None
    
    async def batch_compute_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
        batch_size: int = 100
    ) -> List[Optional[List[float]]]:
        """
        Compute embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
            dimensions: Number of dimensions
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors (None for failed embeddings)
        """
        try:
            all_embeddings = []
            openai_client = await get_openai_client()
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Check cache for each text in batch
                batch_embeddings = []
                uncached_texts = []
                uncached_indices = []
                
                for j, text in enumerate(batch):
                    cache_key = self._get_cache_key(text, model or self.default_model, dimensions)
                    cached = await self.cache.get(cache_key)
                    if cached:
                        batch_embeddings.append(cached)
                    else:
                        batch_embeddings.append(None)
                        uncached_texts.append(text)
                        uncached_indices.append(j)
                
                # Process uncached texts
                if uncached_texts:
                    request = EmbeddingRequest(
                        texts=uncached_texts,
                        model=model,
                        dimensions=dimensions
                    )
                    
                    response = await openai_client.embed_texts(request)
                    
                    if response["success"]:
                        new_embeddings = response["embeddings"]
                        
                        # Update batch results and cache
                        for idx, embedding in zip(uncached_indices, new_embeddings):
                            batch_embeddings[idx] = embedding
                            
                            # Cache the embedding
                            cache_key = self._get_cache_key(
                                uncached_texts[uncached_indices.index(idx)],
                                model or self.default_model,
                                dimensions
                            )
                            await self.cache.set(cache_key, embedding, expire=86400)
                
                all_embeddings.extend(batch_embeddings)
                
                # Small delay between batches
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Computed embeddings for {len(texts)} texts")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding computation failed: {e}")
            return [None] * len(texts)
    
    async def store_embedding(
        self,
        db: AsyncSession,
        content_id: str,
        content_type: str,
        content_text: str,
        embedding_vector: List[float],
        model_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Embedding]:
        """
        Store embedding in database
        
        Args:
            db: Database session
            content_id: Unique content identifier
            content_type: Type of content
            content_text: Original text
            embedding_vector: Computed embedding
            model_name: Model used for embedding
            metadata: Additional metadata
            
        Returns:
            Stored embedding record or None if failed
        """
        try:
            # Create content hash for deduplication
            content_hash = hashlib.sha256(content_text.encode()).hexdigest()
            
            # Check if embedding already exists
            existing = await db.execute(
                select(Embedding).where(Embedding.content_hash == content_hash)
            )
            if existing.scalar_one_or_none():
                logger.info(f"Embedding already exists for content hash {content_hash}")
                return existing.scalar_one()
            
            # Create new embedding
            embedding = Embedding(
                content_id=content_id,
                content_type=content_type,
                content_text=content_text,
                content_hash=content_hash,
                model_name=model_name,
                dimensions=len(embedding_vector),
                embedding_vector=embedding_vector,
                text_length=len(content_text),
                created_at=datetime.utcnow()
            )
            
            # Add metadata if provided
            if metadata:
                embedding.symbol = metadata.get("symbol")
                embedding.timestamp = metadata.get("timestamp")
                embedding.category = metadata.get("category")
                embedding.tags = metadata.get("tags", [])
                embedding.source_table = metadata.get("source_table")
                embedding.source_id = metadata.get("source_id")
            
            db.add(embedding)
            await db.commit()
            await db.refresh(embedding)
            
            logger.info(f"Stored embedding for {content_type} content_id={content_id}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            await db.rollback()
            return None
    
    async def similarity_search(
        self,
        db: AsyncSession,
        request: SimilaritySearchRequest
    ) -> SimilaritySearchResponse:
        """
        Perform similarity search using embeddings
        
        Args:
            db: Database session
            request: Search request parameters
            
        Returns:
            Search response with similar items
        """
        start_time = datetime.utcnow()
        
        try:
            # Generate query embedding
            embedding_start = datetime.utcnow()
            query_embedding = await self.compute_embedding(request.query_text)
            embedding_time = (datetime.utcnow() - embedding_start).total_seconds() * 1000
            
            if not query_embedding:
                return SimilaritySearchResponse(
                    query=request.query_text,
                    total_results=0,
                    results=[],
                    search_time_ms=0,
                    embedding_model=self.default_model,
                    parameters=request.dict(),
                    query_embedding_time_ms=embedding_time
                )
            
            # Build search query
            search_start = datetime.utcnow()
            query = select(Embedding).where(
                and_(
                    Embedding.content_type == request.search_type,
                    Embedding.search_enabled == True
                )
            )
            
            # Apply filters
            if request.symbol_filter:
                query = query.where(Embedding.symbol == request.symbol_filter)
            
            if request.date_range:
                start_date = datetime.fromisoformat(request.date_range["start"])
                end_date = datetime.fromisoformat(request.date_range["end"])
                query = query.where(
                    and_(
                        Embedding.timestamp >= start_date,
                        Embedding.timestamp <= end_date
                    )
                )
            
            # Execute query to get candidate embeddings
            result = await db.execute(query)
            embeddings = result.scalars().all()
            
            # Calculate similarities
            similarities = []
            for emb in embeddings:
                if emb.embedding_vector:
                    similarity = self._cosine_similarity(query_embedding, emb.embedding_vector)
                    if similarity >= request.similarity_threshold:
                        similarities.append((emb, similarity))
            
            # Sort by similarity and take top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_similarities = similarities[:request.top_k]
            
            search_time = (datetime.utcnow() - search_start).total_seconds() * 1000
            
            # Create response
            results = []
            for emb, similarity in top_similarities:
                result = SimilaritySearchResult(
                    item_id=emb.content_id,
                    content=emb.content_text,
                    similarity_score=similarity,
                    item_type=emb.content_type,
                    timestamp=emb.timestamp,
                    metadata={
                        "symbol": emb.symbol,
                        "category": emb.category,
                        "tags": emb.tags,
                        "source_table": emb.source_table,
                        "source_id": emb.source_id
                    }
                )
                
                if request.include_embeddings:
                    result.embedding = emb.embedding_vector
                
                if request.explain_similarity:
                    result.explanation = self._explain_similarity(
                        request.query_text, 
                        emb.content_text, 
                        similarity
                    )
                
                results.append(result)
            
            total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log search query for analytics
            await self._log_search_query(
                db, request, query_embedding, len(results), 
                search_time, embedding_time, total_time
            )
            
            response = SimilaritySearchResponse(
                query=request.query_text,
                total_results=len(similarities),
                results=results,
                search_time_ms=search_time,
                embedding_model=self.default_model,
                parameters=request.dict(),
                query_embedding_time_ms=embedding_time,
                total_items_searched=len(embeddings)
            )
            
            logger.info(f"Similarity search returned {len(results)} results in {total_time:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return SimilaritySearchResponse(
                query=request.query_text,
                total_results=0,
                results=[],
                search_time_ms=0,
                embedding_model=self.default_model,
                parameters=request.dict()
            )
    
    async def embed_trades(
        self,
        db: AsyncSession,
        limit: Optional[int] = None,
        symbol: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate embeddings for trade data
        
        Args:
            db: Database session
            limit: Maximum number of trades to process
            symbol: Optional symbol filter
            
        Returns:
            Processing results
        """
        try:
            # Get trades without embeddings
            query = select(Trade)
            
            if symbol:
                query = query.where(Trade.symbol == symbol)
            
            if limit:
                query = query.limit(limit)
            
            result = await db.execute(query)
            trades = result.scalars().all()
            
            if not trades:
                return {"message": "No trades found to embed", "processed": 0}
            
            # Generate text representations for trades
            trade_texts = []
            for trade in trades:
                text = self._trade_to_text(trade)
                trade_texts.append(text)
            
            # Compute embeddings
            embeddings = await self.batch_compute_embeddings(trade_texts)
            
            # Store embeddings
            stored_count = 0
            for trade, embedding, text in zip(trades, embeddings, trade_texts):
                if embedding:
                    metadata = {
                        "symbol": trade.symbol,
                        "timestamp": trade.time,
                        "category": "trade",
                        "source_table": "trades",
                        "source_id": trade.id
                    }
                    
                    stored = await self.store_embedding(
                        db, str(trade.id), "trades", text, 
                        embedding, self.default_model, metadata
                    )
                    
                    if stored:
                        stored_count += 1
            
            return {
                "message": f"Processed {len(trades)} trades",
                "processed": len(trades),
                "embeddings_computed": len([e for e in embeddings if e]),
                "embeddings_stored": stored_count
            }
            
        except Exception as e:
            logger.error(f"Failed to embed trades: {e}")
            return {"error": str(e)}
    
    def _trade_to_text(self, trade) -> str:
        """Convert trade object to text representation"""
        return (
            f"Trade {trade.symbol} {trade.side} {trade.amount} at {trade.price} "
            f"on {trade.time.isoformat()} with fee {trade.fee}"
        )
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy arrays for efficient computation
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    def _explain_similarity(self, query: str, content: str, similarity: float) -> str:
        """Generate explanation for similarity score"""
        if similarity >= 0.9:
            return "Very high similarity - nearly identical content"
        elif similarity >= 0.8:
            return "High similarity - strong semantic match"
        elif similarity >= 0.7:
            return "Moderate similarity - related concepts"
        elif similarity >= 0.6:
            return "Some similarity - loosely related"
        else:
            return "Low similarity - minimal relationship"
    
    def _get_cache_key(self, text: str, model: str, dimensions: Optional[int]) -> str:
        """Generate cache key for embedding"""
        key_data = f"{text}:{model}:{dimensions or 'default'}"
        return f"embedding:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    async def _log_search_query(
        self,
        db: AsyncSession,
        request: SimilaritySearchRequest,
        query_vector: List[float],
        result_count: int,
        search_time_ms: float,
        embedding_time_ms: float,
        total_time_ms: float
    ):
        """Log search query for analytics"""
        try:
            query_hash = hashlib.sha256(request.query_text.encode()).hexdigest()
            
            search_log = SearchQuery(
                query_id=f"search_{int(datetime.utcnow().timestamp())}_{hash(request.query_text) % 10000}",
                query_text=request.query_text,
                query_hash=query_hash,
                search_type=request.search_type,
                top_k=request.top_k,
                similarity_threshold=request.similarity_threshold,
                filters=request.additional_filters,
                query_model=self.default_model,
                query_vector=query_vector,
                returned_results=result_count,
                search_time_ms=search_time_ms,
                embedding_time_ms=embedding_time_ms,
                total_time_ms=total_time_ms
            )
            
            db.add(search_log)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log search query: {e}")


# Global service instance
_embedding_service: Optional[EmbeddingService] = None


async def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        from app.services.cache import get_cache_service
        cache_service = await get_cache_service()
        _embedding_service = EmbeddingService(cache_service)
    return _embedding_service