"""
OpenAI Client Service
Provides integration with OpenAI API for:
- JSON mode responses for structured data
- Batch labeling operations  
- Text embeddings generation
- ML experiment planning via GPT models
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import openai
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIConfig(BaseModel):
    """OpenAI API Configuration"""
    api_key: str
    model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout: int = 30


class BatchLabelRequest(BaseModel):
    """Request for batch labeling operation"""
    items: List[Dict[str, Any]]
    labels: List[str]
    context: Optional[str] = None
    confidence_threshold: float = 0.8


class EmbeddingRequest(BaseModel):
    """Request for text embedding generation"""
    texts: List[str]
    model: Optional[str] = None
    dimensions: Optional[int] = None


class JSONModeRequest(BaseModel):
    """Request for JSON mode completion"""
    prompt: str
    schema: Optional[Dict[str, Any]] = None
    context: Optional[str] = None


class OpenAIClient:
    """OpenAI API Client with specialized methods for trading analytics"""
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        """Initialize OpenAI client"""
        self.config = config or OpenAIConfig(
            api_key=settings.OPENAI_API_KEY,
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
            embedding_model=getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        )
        
        self.client = AsyncOpenAI(
            api_key=self.config.api_key,
            timeout=self.config.timeout
        )
        
    async def json_mode(
        self,
        request: JSONModeRequest,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get structured JSON response from OpenAI using JSON mode
        
        Args:
            request: JSON mode request with prompt and optional schema
            model: Override default model
            
        Returns:
            Parsed JSON response from the model
        """
        try:
            model = model or self.config.model
            
            # Construct system message for JSON mode
            system_message = "You are a helpful assistant that responds in valid JSON format."
            if request.schema:
                system_message += f"\n\nYour response must follow this JSON schema:\n{json.dumps(request.schema, indent=2)}"
            
            messages = [
                {"role": "system", "content": system_message},
            ]
            
            if request.context:
                messages.append({"role": "user", "content": f"Context: {request.context}"})
            
            messages.append({"role": "user", "content": request.prompt})
            
            response = None
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            logger.info(f"JSON mode response generated using {model}")
            return {
                "success": True,
                "data": result,
                "model": model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "success": False,
                "error": "Invalid JSON response from model",
                "raw_content": response.choices[0].message.content if response and response.choices else None
            }
        except Exception as e:
            logger.error(f"JSON mode request failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def batch_label(
        self,
        request: BatchLabelRequest,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform batch labeling of trading data items
        
        Args:
            request: Batch labeling request with items and labels
            model: Override default model
            
        Returns:
            Labeled items with confidence scores
        """
        try:
            model = model or self.config.model
            
            # Prepare labeling prompt
            labels_str = ", ".join(request.labels)
            context_str = f"\nContext: {request.context}" if request.context else ""
            
            prompt = f"""
            Label each of the following trading data items with one of these labels: {labels_str}
            
            For each item, provide:
            1. The assigned label
            2. Confidence score (0.0 to 1.0)
            3. Brief reasoning
            
            {context_str}
            
            Items to label:
            {json.dumps(request.items, indent=2)}
            
            Return your response as a JSON array where each element has:
            - "item_index": index of the original item
            - "label": assigned label
            - "confidence": confidence score
            - "reasoning": brief explanation
            """
            
            json_request = JSONModeRequest(
                prompt=prompt,
                schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_index": {"type": "integer"},
                            "label": {"type": "string"},
                            "confidence": {"type": "number"},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["item_index", "label", "confidence", "reasoning"]
                    }
                }
            )
            
            response = await self.json_mode(json_request, model)
            
            if not response["success"]:
                return response
            
            labeled_items = response["data"]
            
            # Filter by confidence threshold
            high_confidence_items = [
                item for item in labeled_items 
                if item["confidence"] >= request.confidence_threshold
            ]
            
            result = {
                "success": True,
                "total_items": len(request.items),
                "labeled_items": len(labeled_items),
                "high_confidence_items": len(high_confidence_items),
                "confidence_threshold": request.confidence_threshold,
                "labels": labeled_items,
                "high_confidence_labels": high_confidence_items,
                "model": model,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Batch labeled {len(labeled_items)} items with {len(high_confidence_items)} high-confidence labels")
            return result
            
        except Exception as e:
            logger.error(f"Batch labeling failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def embed_texts(
        self,
        request: EmbeddingRequest
    ) -> Dict[str, Any]:
        """
        Generate embeddings for list of texts
        
        Args:
            request: Embedding request with texts and optional model
            
        Returns:
            Embeddings and metadata
        """
        try:
            model = request.model or self.config.embedding_model
            
            # Handle large batches by chunking
            chunk_size = 100  # OpenAI recommends max 100 texts per request
            all_embeddings = []
            
            for i in range(0, len(request.texts), chunk_size):
                chunk = request.texts[i:i + chunk_size]
                
                embedding_params = {
                    "model": model,
                    "input": chunk
                }
                
                # Add dimensions if specified for newer embedding models
                if request.dimensions and "text-embedding-3" in model:
                    embedding_params["dimensions"] = request.dimensions
                
                response = await self.client.embeddings.create(**embedding_params)
                
                chunk_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(chunk_embeddings)
                
                # Small delay between chunks to respect rate limits
                if i + chunk_size < len(request.texts):
                    await asyncio.sleep(0.1)
            
            result = {
                "success": True,
                "embeddings": all_embeddings,
                "model": model,
                "dimensions": len(all_embeddings[0]) if all_embeddings else 0,
                "total_texts": len(request.texts),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated embeddings for {len(request.texts)} texts using {model}")
            return result
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def plan_ml_experiment(
        self,
        experiment_description: str,
        available_data: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use OpenAI to plan ML experiments based on available data
        
        Args:
            experiment_description: What the experiment should accomplish
            available_data: Description of available data and features
            constraints: Resource and time constraints
            
        Returns:
            Structured experiment plan
        """
        try:
            constraints_str = json.dumps(constraints, indent=2) if constraints else "None specified"
            
            prompt = f"""
            Plan a machine learning experiment for trading analytics.
            
            Goal: {experiment_description}
            
            Available Data:
            {json.dumps(available_data, indent=2)}
            
            Constraints:
            {constraints_str}
            
            Create a detailed experiment plan with:
            1. Problem type (classification, regression, clustering, etc.)
            2. Recommended algorithms and why
            3. Feature engineering suggestions
            4. Data preprocessing steps
            5. Evaluation metrics
            6. Expected timeline
            7. Success criteria
            8. Risk assessment
            """
            
            schema = {
                "type": "object",
                "properties": {
                    "experiment_name": {"type": "string"},
                    "problem_type": {"type": "string"},
                    "algorithms": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "rationale": {"type": "string"},
                                "priority": {"type": "integer"}
                            }
                        }
                    },
                    "feature_engineering": {"type": "array", "items": {"type": "string"}},
                    "preprocessing_steps": {"type": "array", "items": {"type": "string"}},
                    "evaluation_metrics": {"type": "array", "items": {"type": "string"}},
                    "timeline_weeks": {"type": "integer"},
                    "success_criteria": {"type": "array", "items": {"type": "string"}},
                    "risks": {"type": "array", "items": {"type": "string"}},
                    "next_steps": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["experiment_name", "problem_type", "algorithms", "evaluation_metrics"]
            }
            
            json_request = JSONModeRequest(
                prompt=prompt,
                schema=schema,
                context="This is for a cryptocurrency trading analytics platform"
            )
            
            response = await self.json_mode(json_request)
            
            if response["success"]:
                response["data"]["planned_at"] = datetime.utcnow().isoformat()
                response["data"]["experiment_id"] = f"exp_{int(datetime.utcnow().timestamp())}"
            
            return response
            
        except Exception as e:
            logger.error(f"ML experiment planning failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity and model availability"""
        try:
            # Simple test request to verify connectivity
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {
                "status": "healthy",
                "model": self.config.model,
                "embedding_model": self.config.embedding_model,
                "api_accessible": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_accessible": False,
                "timestamp": datetime.utcnow().isoformat()
            }


# Global client instance (initialized when needed)
_openai_client: Optional[OpenAIClient] = None


async def get_openai_client() -> OpenAIClient:
    """Get or create OpenAI client instance"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client