"""
Google Cloud Secret Manager Client

This module provides an async-compatible interface for Google Cloud Secret Manager operations
including secret creation, retrieval, and management for the HTX trading platform.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any

from google.cloud import secretmanager
from google.auth.exceptions import DefaultCredentialsError
from google.api_core import exceptions as gcp_exceptions
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class SecretManagerError(Exception):
    """Custom exception for Secret Manager errors"""
    pass


class SecretManagerClient:
    """
    Async-compatible Google Cloud Secret Manager client for the HTX trading platform.
    
    Provides methods for:
    - Creating and managing secrets
    - Retrieving secret values securely
    - Updating secret versions
    - Managing secret metadata
    """
    
    def __init__(self, settings: Any):
        """
        Initialize the Secret Manager Client with configuration settings.
        
        Args:
            settings: Application settings containing GCP configuration
        """
        self.settings = settings
        self.project_id = settings.GCP_PROJECT_ID
        self._client: Optional[secretmanager.SecretManagerServiceClient] = None
        self._executor = ThreadPoolExecutor(max_workers=5)
        
        # Initialize client if credentials are available
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Google Cloud Secret Manager client"""
        try:
            if self.settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Use service account credentials
                self._client = secretmanager.SecretManagerServiceClient.from_service_account_json(
                    self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                # Use default credentials
                self._client = secretmanager.SecretManagerServiceClient()
            
            logger.info("Initialized Secret Manager client successfully")
            
        except DefaultCredentialsError:
            logger.warning("GCP credentials not found. Secret Manager client will be disabled.")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize Secret Manager client: {e}")
            raise SecretManagerError(f"Failed to initialize Secret Manager client: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if the Secret Manager client is properly configured and available"""
        return self._client is not None
    
    def _get_secret_path(self, secret_name: str) -> str:
        """Get the full secret path"""
        return f"projects/{self.project_id}/secrets/{secret_name}"
    
    def _get_secret_version_path(self, secret_name: str, version: str = "latest") -> str:
        """Get the full secret version path"""
        return f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_secret(
        self,
        secret_name: str,
        secret_value: str,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create a new secret with an initial value.
        
        Args:
            secret_name: Name of the secret to create
            secret_value: Initial value for the secret
            labels: Optional labels for the secret
            
        Returns:
            The full secret path
            
        Raises:
            SecretManagerError: If secret creation fails
        """
        if not self.is_available:
            raise SecretManagerError("Secret Manager client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            secret_path = await loop.run_in_executor(
                self._executor,
                self._create_secret_sync,
                secret_name,
                secret_value,
                labels or {}
            )
            
            logger.info(f"Created secret: {secret_path}")
            return secret_path
            
        except Exception as e:
            logger.error(f"Failed to create secret {secret_name}: {e}")
            raise SecretManagerError(f"Secret creation failed: {e}")
    
    def _create_secret_sync(
        self,
        secret_name: str,
        secret_value: str,
        labels: Dict[str, str]
    ) -> str:
        """Synchronous secret creation implementation"""
        parent = f"projects/{self.project_id}"
        
        # Create the secret
        secret = {
            "replication": {"automatic": {}},
            "labels": labels
        }
        
        try:
            response = self._client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_name,
                    "secret": secret
                }
            )
            secret_path = response.name
        except gcp_exceptions.AlreadyExists:
            # Secret already exists, get its path
            secret_path = self._get_secret_path(secret_name)
        
        # Add the secret version with the actual value
        self._client.add_secret_version(
            request={
                "parent": secret_path,
                "payload": {"data": secret_value.encode("UTF-8")}
            }
        )
        
        return secret_path
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_secret(
        self,
        secret_name: str,
        version: str = "latest"
    ) -> Optional[str]:
        """
        Retrieve a secret value.
        
        Args:
            secret_name: Name of the secret to retrieve
            version: Version of the secret (default: "latest")
            
        Returns:
            The secret value as a string, or None if not found
            
        Raises:
            SecretManagerError: If secret retrieval fails
        """
        if not self.is_available:
            raise SecretManagerError("Secret Manager client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            secret_value = await loop.run_in_executor(
                self._executor,
                self._get_secret_sync,
                secret_name,
                version
            )
            
            logger.info(f"Retrieved secret: {secret_name}")
            return secret_value
            
        except gcp_exceptions.NotFound:
            logger.warning(f"Secret {secret_name} not found")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise SecretManagerError(f"Secret retrieval failed: {e}")
    
    def _get_secret_sync(self, secret_name: str, version: str) -> str:
        """Synchronous secret retrieval implementation"""
        version_path = self._get_secret_version_path(secret_name, version)
        
        response = self._client.access_secret_version(
            request={"name": version_path}
        )
        
        return response.payload.data.decode("UTF-8")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def update_secret(
        self,
        secret_name: str,
        secret_value: str
    ) -> str:
        """
        Update a secret with a new value (creates a new version).
        
        Args:
            secret_name: Name of the secret to update
            secret_value: New value for the secret
            
        Returns:
            The new version path
            
        Raises:
            SecretManagerError: If secret update fails
        """
        if not self.is_available:
            raise SecretManagerError("Secret Manager client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            version_path = await loop.run_in_executor(
                self._executor,
                self._update_secret_sync,
                secret_name,
                secret_value
            )
            
            logger.info(f"Updated secret: {secret_name}")
            return version_path
            
        except Exception as e:
            logger.error(f"Failed to update secret {secret_name}: {e}")
            raise SecretManagerError(f"Secret update failed: {e}")
    
    def _update_secret_sync(self, secret_name: str, secret_value: str) -> str:
        """Synchronous secret update implementation"""
        secret_path = self._get_secret_path(secret_name)
        
        response = self._client.add_secret_version(
            request={
                "parent": secret_path,
                "payload": {"data": secret_value.encode("UTF-8")}
            }
        )
        
        return response.name
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def delete_secret(self, secret_name: str) -> bool:
        """
        Delete a secret and all its versions.
        
        Args:
            secret_name: Name of the secret to delete
            
        Returns:
            True if deletion successful, False if secret not found
            
        Raises:
            SecretManagerError: If secret deletion fails
        """
        if not self.is_available:
            raise SecretManagerError("Secret Manager client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self._delete_secret_sync,
                secret_name
            )
            
            logger.info(f"Deleted secret: {secret_name}")
            return True
            
        except gcp_exceptions.NotFound:
            logger.warning(f"Secret {secret_name} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_name}: {e}")
            raise SecretManagerError(f"Secret deletion failed: {e}")
    
    def _delete_secret_sync(self, secret_name: str) -> None:
        """Synchronous secret deletion implementation"""
        secret_path = self._get_secret_path(secret_name)
        
        self._client.delete_secret(request={"name": secret_path})
    
    async def list_secrets(self) -> Dict[str, Dict[str, Any]]:
        """
        List all secrets in the project.
        
        Returns:
            Dictionary mapping secret names to their metadata
            
        Raises:
            SecretManagerError: If listing fails
        """
        if not self.is_available:
            raise SecretManagerError("Secret Manager client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            secrets_data = await loop.run_in_executor(
                self._executor,
                self._list_secrets_sync
            )
            
            logger.info(f"Found {len(secrets_data)} secrets")
            return secrets_data
            
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            raise SecretManagerError(f"Secret listing failed: {e}")
    
    def _list_secrets_sync(self) -> Dict[str, Dict[str, Any]]:
        """Synchronous secret listing implementation"""
        parent = f"projects/{self.project_id}"
        
        secrets_data = {}
        for secret in self._client.list_secrets(request={"parent": parent}):
            secret_name = secret.name.split('/')[-1]
            secrets_data[secret_name] = {
                "name": secret.name,
                "create_time": secret.create_time,
                "labels": dict(secret.labels) if secret.labels else {},
                "replication": str(secret.replication)
            }
        
        return secrets_data
    
    async def get_or_create_secret(
        self,
        secret_name: str,
        default_value: str,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Get a secret value, creating it with a default value if it doesn't exist.
        
        Args:
            secret_name: Name of the secret
            default_value: Default value to use if secret doesn't exist
            labels: Optional labels for the secret (only used if creating)
            
        Returns:
            The secret value
            
        Raises:
            SecretManagerError: If operations fail
        """
        try:
            # Try to get existing secret
            secret_value = await self.get_secret(secret_name)
            if secret_value is not None:
                return secret_value
            
            # Secret doesn't exist, create it
            await self.create_secret(secret_name, default_value, labels)
            return default_value
            
        except Exception as e:
            logger.error(f"Failed to get or create secret {secret_name}: {e}")
            raise SecretManagerError(f"Get or create secret failed: {e}")
    
    async def close(self) -> None:
        """Close the Secret Manager client and cleanup resources"""
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("Secret Manager client resources cleaned up")


# Factory function for easy initialization
def create_secret_manager_client(settings) -> SecretManagerClient:
    """
    Factory function to create a Secret Manager client.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured SecretManagerClient instance
    """
    return SecretManagerClient(settings)


# Utility functions for common secret patterns
async def setup_htx_secrets(client: SecretManagerClient, settings) -> Dict[str, str]:
    """
    Setup HTX API secrets in Secret Manager.
    
    Args:
        client: SecretManagerClient instance
        settings: Application settings
        
    Returns:
        Dictionary of secret names and their current values
    """
    secrets = {}
    
    if settings.HTX_API_KEY:
        await client.get_or_create_secret(
            "htx-api-key",
            settings.HTX_API_KEY,
            {"service": "htx", "type": "api-key"}
        )
        secrets["htx-api-key"] = await client.get_secret("htx-api-key")
    
    if settings.HTX_API_SECRET:
        await client.get_or_create_secret(
            "htx-api-secret",
            settings.HTX_API_SECRET,
            {"service": "htx", "type": "api-secret"}
        )
        secrets["htx-api-secret"] = await client.get_secret("htx-api-secret")
    
    if settings.OPENAI_API_KEY:
        await client.get_or_create_secret(
            "openai-api-key",
            settings.OPENAI_API_KEY,
            {"service": "openai", "type": "api-key"}
        )
        secrets["openai-api-key"] = await client.get_secret("openai-api-key")
    
    return secrets