"""
Google Cloud Platform (GCP) Services Integration Module

This module provides integration with various Google Cloud services including:
- Cloud Storage for file management
- Pub/Sub for event-driven communication
- Secret Manager for secure credential management
- Cloud Scheduler for periodic tasks
- Vertex AI for machine learning workflows
- BigQuery for data warehousing
- Dataflow for ETL pipelines

All GCP services are configured through the Settings class and require
proper authentication via service account credentials.
"""

import logging
from typing import Optional

# Import all GCP clients with error handling
try:
    from .storage_client import StorageClient, create_storage_client
except ImportError:
    StorageClient = None
    create_storage_client = None

try:
    from .pubsub_client import PubSubClient, create_pubsub_client
except ImportError:
    PubSubClient = None
    create_pubsub_client = None

try:
    from .secret_manager import SecretManagerClient, create_secret_manager_client
except ImportError:
    SecretManagerClient = None
    create_secret_manager_client = None

try:
    from .vertex_ai_client import VertexAIClient, create_vertex_ai_client
except ImportError:
    VertexAIClient = None
    create_vertex_ai_client = None

try:
    from .scheduler_client import SchedulerClient, create_scheduler_client
except ImportError:
    SchedulerClient = None
    create_scheduler_client = None

logger = logging.getLogger(__name__)

__all__ = [
    'StorageClient', 'create_storage_client',
    'PubSubClient', 'create_pubsub_client', 
    'SecretManagerClient', 'create_secret_manager_client',
    'VertexAIClient', 'create_vertex_ai_client',
    'SchedulerClient', 'create_scheduler_client',
    'GCPServices', 'setup_gcp_services'
]

# Service factory for lazy initialization
class GCPServices:
    """Factory class for GCP services with lazy initialization"""
    
    def __init__(self, settings):
        self.settings = settings
        self._storage_client: Optional[StorageClient] = None
        self._pubsub_client: Optional[PubSubClient] = None
        self._secret_manager_client: Optional[SecretManagerClient] = None
        self._vertex_ai_client: Optional[VertexAIClient] = None
        self._scheduler_client: Optional[SchedulerClient] = None
    
    @property
    def storage(self) -> StorageClient:
        """Get or create StorageClient instance"""
        if StorageClient is None:
            raise ImportError("GCP Storage dependencies not installed. Run: pip install google-cloud-storage")
        
        if not self._storage_client:
            self._storage_client = create_storage_client(self.settings)
        return self._storage_client
    
    @property
    def pubsub(self) -> PubSubClient:
        """Get or create PubSubClient instance"""
        if PubSubClient is None:
            raise ImportError("GCP Pub/Sub dependencies not installed. Run: pip install google-cloud-pubsub")
        
        if not self._pubsub_client:
            self._pubsub_client = create_pubsub_client(self.settings)
        return self._pubsub_client
    
    @property
    def secret_manager(self) -> SecretManagerClient:
        """Get or create SecretManagerClient instance"""
        if SecretManagerClient is None:
            raise ImportError("GCP Secret Manager dependencies not installed. Run: pip install google-cloud-secret-manager")
        
        if not self._secret_manager_client:
            self._secret_manager_client = create_secret_manager_client(self.settings)
        return self._secret_manager_client
    
    @property
    def vertex_ai(self) -> VertexAIClient:
        """Get or create VertexAIClient instance"""
        if VertexAIClient is None:
            raise ImportError("GCP Vertex AI dependencies not installed. Run: pip install google-cloud-aiplatform")
        
        if not self._vertex_ai_client:
            self._vertex_ai_client = create_vertex_ai_client(self.settings)
        return self._vertex_ai_client
    
    @property
    def scheduler(self) -> SchedulerClient:
        """Get or create SchedulerClient instance"""
        if SchedulerClient is None:
            raise ImportError("GCP Scheduler dependencies not installed. Run: pip install google-cloud-scheduler")
        
        if not self._scheduler_client:
            self._scheduler_client = create_scheduler_client(self.settings)
        return self._scheduler_client
    
    @property
    def is_configured(self) -> bool:
        """Check if GCP services are properly configured"""
        return bool(
            self.settings.GCP_PROJECT_ID and 
            (self.settings.GOOGLE_APPLICATION_CREDENTIALS or self.settings.GCP_USE_DEFAULT_CREDENTIALS)
        )
    
    async def close_all(self):
        """Close all GCP service clients and cleanup resources"""
        try:
            if self._pubsub_client:
                await self._pubsub_client.close()
            if self._secret_manager_client:
                await self._secret_manager_client.close()
            if self._vertex_ai_client:
                await self._vertex_ai_client.close()
            if self._scheduler_client:
                await self._scheduler_client.close()
            logger.info("All GCP service clients closed successfully")
        except Exception as e:
            logger.error(f"Error closing GCP service clients: {e}")


# Convenience function to setup all GCP services
async def setup_gcp_services(settings) -> GCPServices:
    """Setup and initialize all GCP services"""
    gcp_services = GCPServices(settings)
    
    if gcp_services.is_configured:
        logger.info("GCP services are properly configured")
        
        # Test connections to ensure all services are working
        try:
            # Test storage if available
            if StorageClient and gcp_services.storage.is_available:
                logger.info("GCP Storage client initialized successfully")
            
            # Test other services if available
            if PubSubClient and gcp_services.pubsub.is_available:
                logger.info("GCP Pub/Sub client initialized successfully")
            
            if SecretManagerClient and gcp_services.secret_manager.is_available:
                logger.info("GCP Secret Manager client initialized successfully")
            
            if VertexAIClient and gcp_services.vertex_ai.is_available:
                logger.info("GCP Vertex AI client initialized successfully")
            
            if SchedulerClient and gcp_services.scheduler.is_available:
                logger.info("GCP Scheduler client initialized successfully")
                
        except Exception as e:
            logger.warning(f"Some GCP services may not be fully available: {e}")
    else:
        logger.warning("GCP services are not properly configured. Check GCP_PROJECT_ID and credentials.")
    
    return gcp_services


# Global instance (will be initialized by main app)
gcp_services: Optional[GCPServices] = None