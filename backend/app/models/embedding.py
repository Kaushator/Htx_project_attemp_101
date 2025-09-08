"""
Database model for embeddings and vector search
Supports pgvector for PostgreSQL or fallback to JSON storage for SQLite
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from app.models.base import BaseModel

try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False


class Embedding(BaseModel):
    """Embedding model for vector storage and similarity search"""
    
    __tablename__ = "embeddings"
    
    # Basic information
    content_id = Column(String(100), nullable=False, index=True)  # Reference to original content
    content_type = Column(String(50), nullable=False, index=True)  # "trade", "log", "transaction"
    content_text = Column(Text, nullable=False)  # Original text content
    content_hash = Column(String(64), unique=True, index=True)  # Content hash for deduplication
    
    # Embedding data
    model_name = Column(String(100), nullable=False)  # Model used to generate embedding
    embedding_version = Column(String(20), default="1.0")  # Version for embedding compatibility
    dimensions = Column(Integer, nullable=False)  # Embedding dimensions
    
    # Vector storage - use pgvector if available, otherwise JSON
    if PGVECTOR_AVAILABLE:
        embedding_vector = Column(Vector(1536))  # Default dimensions for text-embedding-3-small
    else:
        embedding_vector = Column(JSON)  # Fallback to JSON array for SQLite
    
    # Metadata
    source_table = Column(String(50))  # Source table name
    source_id = Column(Integer)  # Source record ID
    
    # Content metadata
    symbol = Column(String(20))  # Trading symbol if applicable
    timestamp = Column(DateTime)  # Content timestamp
    category = Column(String(50))  # Content category
    tags = Column(JSON)  # List of tags
    
    # Processing metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    processed_by = Column(String(100))  # Who/what processed this embedding
    
    # Quality metrics
    text_length = Column(Integer)  # Original text length
    confidence_score = Column(Float)  # Confidence in embedding quality
    similarity_threshold = Column(Float, default=0.7)  # Threshold for similarity matching
    
    # Search optimization
    search_enabled = Column(Boolean, default=True)  # Whether to include in searches
    priority = Column(Integer, default=1)  # Search priority weight
    
    def __repr__(self):
        return f"<Embedding(id={self.id}, content_type={self.content_type}, model={self.model_name})>"
    
    @property
    def vector_norm(self) -> float:
        """Calculate L2 norm of the embedding vector"""
        if not self.embedding_vector:
            return 0.0
        
        if isinstance(self.embedding_vector, list):
            return sum(x * x for x in self.embedding_vector) ** 0.5
        return 0.0
    
    @property
    def is_normalized(self) -> bool:
        """Check if embedding vector is normalized"""
        norm = self.vector_norm
        return 0.99 <= norm <= 1.01  # Allow small floating point errors


# Create indexes for efficient similarity search
if PGVECTOR_AVAILABLE:
    # Create HNSW index for fast similarity search (PostgreSQL with pgvector)
    embedding_hnsw_index = Index(
        'embedding_hnsw_idx',
        Embedding.embedding_vector,
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'embedding_vector': 'vector_cosine_ops'}
    )
else:
    # Create regular indexes for SQLite fallback
    content_type_index = Index('idx_embedding_content_type', Embedding.content_type)
    timestamp_index = Index('idx_embedding_timestamp', Embedding.timestamp)
    symbol_index = Index('idx_embedding_symbol', Embedding.symbol)


class EmbeddingCluster(BaseModel):
    """Clusters of similar embeddings for improved search performance"""
    
    __tablename__ = "embedding_clusters"
    
    # Cluster identification
    cluster_id = Column(String(100), unique=True, nullable=False, index=True)
    cluster_name = Column(String(200))
    content_type = Column(String(50), nullable=False)
    
    # Cluster statistics
    embedding_count = Column(Integer, default=0)
    min_similarity = Column(Float)  # Minimum similarity within cluster
    max_similarity = Column(Float)  # Maximum similarity within cluster
    avg_similarity = Column(Float)  # Average similarity within cluster
    
    # Cluster centroid
    if PGVECTOR_AVAILABLE:
        centroid_vector = Column(Vector(1536))
    else:
        centroid_vector = Column(JSON)
    
    centroid_model = Column(String(100))  # Model used for centroid
    
    # Cluster metadata
    description = Column(Text)  # Description of what this cluster represents
    keywords = Column(JSON)  # Representative keywords
    sample_texts = Column(JSON)  # Sample texts from this cluster
    
    # Cluster quality metrics
    cohesion_score = Column(Float)  # How tightly grouped the cluster is
    separation_score = Column(Float)  # How distinct from other clusters
    quality_score = Column(Float)  # Overall cluster quality
    
    # Management
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    auto_generated = Column(Boolean, default=True)  # Whether cluster was auto-generated
    
    def __repr__(self):
        return f"<EmbeddingCluster(id={self.cluster_id}, name={self.cluster_name}, count={self.embedding_count})>"


class SearchQuery(BaseModel):
    """Log of search queries for analytics and optimization"""
    
    __tablename__ = "search_queries"
    
    # Query information
    query_id = Column(String(100), unique=True, nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_hash = Column(String(64), index=True)  # For deduplication
    
    # Search parameters
    search_type = Column(String(50), nullable=False)  # "trades", "logs", "general"
    top_k = Column(Integer, default=10)
    similarity_threshold = Column(Float, default=0.7)
    filters = Column(JSON)  # Search filters applied
    
    # Query embedding
    query_model = Column(String(100))
    if PGVECTOR_AVAILABLE:
        query_vector = Column(Vector(1536))
    else:
        query_vector = Column(JSON)
    
    # Results metadata
    total_results = Column(Integer)
    returned_results = Column(Integer)
    highest_similarity = Column(Float)
    lowest_similarity = Column(Float)
    avg_similarity = Column(Float)
    
    # Performance metrics
    search_time_ms = Column(Float)
    embedding_time_ms = Column(Float)
    total_time_ms = Column(Float)
    cache_hit = Column(Boolean, default=False)
    
    # User interaction
    user_id = Column(String(100))  # User who made the query
    session_id = Column(String(100))  # Session identifier
    clicked_results = Column(JSON)  # Which results were clicked
    user_feedback = Column(String(20))  # "helpful", "not_helpful", etc.
    
    # Analytics
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<SearchQuery(id={self.query_id}, type={self.search_type}, results={self.returned_results})>"
    
    @property
    def click_through_rate(self) -> float:
        """Calculate click-through rate"""
        if not self.clicked_results or self.returned_results == 0:
            return 0.0
        return len(self.clicked_results) / self.returned_results
    
    @property
    def search_effectiveness(self) -> float:
        """Calculate search effectiveness score"""
        # Combine multiple factors: result count, similarity scores, user interaction
        factors = []
        
        # Results factor (more results = better, up to a point)
        if self.returned_results:
            results_factor = min(self.returned_results / self.top_k, 1.0)
            factors.append(results_factor)
        
        # Similarity factor (higher average similarity = better)
        if self.avg_similarity:
            factors.append(self.avg_similarity)
        
        # User interaction factor
        if self.user_feedback == "helpful":
            factors.append(1.0)
        elif self.user_feedback == "not_helpful":
            factors.append(0.0)
        elif self.clicked_results:
            factors.append(self.click_through_rate)
        
        return sum(factors) / len(factors) if factors else 0.0