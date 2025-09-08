"""
Core Secrets Manager Module
Provides Secret Manager integration for the HTX Project
"""

import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.services.secret_manager import HTXSecretsManager, SecretManagerService

logger = logging.getLogger(__name__)

class SecretsManager:
    """Core secrets manager wrapper for FastAPI dependency injection"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or settings.GCP_PROJECT_ID
        self.htx_secrets = None
        self.base_service = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the secrets manager services"""
        if not self.project_id:
            logger.warning("No GCP project ID provided for Secret Manager")
            return
        
        try:
            self.htx_secrets = HTXSecretsManager(self.project_id)
            self.base_service = SecretManagerService(self.project_id)
            logger.info("Secrets Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Secret Manager: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if Secret Manager is available and configured"""
        return (
            self.htx_secrets is not None and 
            self.base_service is not None and
            self.base_service.client is not None
        )
    
    async def get_secret(self, secret_name: str) -> Optional[str]:
        """Get a secret value by name"""
        if not self.is_available:
            return None
        
        try:
            return self.base_service.get_secret(secret_name)
        except Exception as e:
            logger.error(f"Failed to get secret {secret_name}: {e}")
            return None
    
    async def create_or_update_secret(self, secret_name: str, secret_value: str) -> bool:
        """Create or update a secret"""
        if not self.is_available:
            return False
        
        try:
            # First try to create the secret
            self.base_service.create_secret(secret_name, f"Secret for {secret_name}")
            # Then store the value
            return self.base_service.store_secret(secret_name, secret_value)
        except Exception as e:
            logger.error(f"Failed to create/update secret {secret_name}: {e}")
            return False
    
    async def delete_secret(self, secret_name: str) -> bool:
        """Delete a secret"""
        if not self.is_available:
            return False
        
        try:
            return self.base_service.delete_secret(secret_name)
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            return False
    
    async def list_secrets(self) -> Dict[str, Any]:
        """List all secrets in the project"""
        if not self.is_available:
            return {}
        
        try:
            return self.base_service.list_secrets()
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return {}
    
    def get_all_htx_secrets(self) -> Dict[str, Optional[str]]:
        """Get all HTX-related secrets"""
        if not self.is_available:
            return {}
        
        try:
            return self.htx_secrets.get_all_secrets()
        except Exception as e:
            logger.error(f"Failed to get HTX secrets: {e}")
            return {}
    
    def validate_setup(self) -> Dict[str, Any]:
        """Validate Secret Manager setup"""
        if not self.is_available:
            return {
                "secret_manager_available": False,
                "error": "Secret Manager not available",
                "project_id": self.project_id
            }
        
        try:
            return self.htx_secrets.validate_setup()
        except Exception as e:
            logger.error(f"Failed to validate setup: {e}")
            return {
                "secret_manager_available": False,
                "error": str(e),
                "project_id": self.project_id
            }


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None

def get_secrets_manager() -> SecretsManager:
    """Dependency injection function for FastAPI"""
    global _secrets_manager
    
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    
    return _secrets_manager

def reset_secrets_manager():
    """Reset the global secrets manager instance (for testing)"""
    global _secrets_manager
    _secrets_manager = None