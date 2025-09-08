"""
Google Secret Manager Integration for HTX Project
Secure storage and retrieval of API keys and sensitive configuration
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class SecretManagerConfig(BaseModel):
    """Configuration for Secret Manager"""
    project_id: str
    secrets_config: Dict[str, str]


class SecretManagerService:
    """Service for managing secrets with Google Secret Manager"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Secret Manager client"""
        try:
            from google.cloud import secretmanager
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info("Google Secret Manager client initialized successfully")
        except ImportError:
            logger.warning("Google Cloud Secret Manager library not installed")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Secret Manager client: {e}")
            self.client = None
    
    def create_secret(self, secret_id: str, description: str = "") -> bool:
        """Create a new secret in Secret Manager"""
        if not self.client:
            logger.error("Secret Manager client not available")
            return False
        
        try:
            parent = f"projects/{self.project_id}"
            secret = {
                "replication": {"automatic": {}},
                "labels": {"app": "htx-trading", "env": "personal"}
            }
            
            if description:
                secret["annotations"] = {"description": description}
            
            response = self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": secret
                }
            )
            
            logger.info(f"Created secret: {response.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create secret {secret_id}: {e}")
            return False
    
    def store_secret(self, secret_id: str, secret_value: str) -> bool:
        """Store a secret value in Secret Manager"""
        if not self.client:
            logger.error("Secret Manager client not available")
            return False
        
        try:
            parent = f"projects/{self.project_id}/secrets/{secret_id}"
            payload = secret_value.encode("UTF-8")
            
            response = self.client.add_secret_version(
                request={
                    "parent": parent,
                    "payload": {"data": payload}
                }
            )
            
            logger.info(f"Stored secret version: {response.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store secret {secret_id}: {e}")
            return False
    
    def get_secret(self, secret_id: str, version: str = "latest") -> Optional[str]:
        """Retrieve a secret value from Secret Manager"""
        if not self.client:
            logger.warning("Secret Manager client not available, using environment fallback")
            return os.getenv(secret_id.replace('-', '_').upper())
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
            response = self.client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode("UTF-8")
            
            logger.debug(f"Retrieved secret: {secret_id}")
            return secret_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_id}: {e}")
            # Fallback to environment variable
            env_key = secret_id.replace('-', '_').upper()
            return os.getenv(env_key)
    
    def list_secrets(self) -> Dict[str, Any]:
        """List all secrets in the project"""
        if not self.client:
            return {}
        
        try:
            parent = f"projects/{self.project_id}"
            secrets = {}
            
            for secret in self.client.list_secrets(request={"parent": parent}):
                secret_id = secret.name.split("/")[-1]
                secrets[secret_id] = {
                    "name": secret.name,
                    "created": secret.create_time,
                    "labels": dict(secret.labels) if secret.labels else {}
                }
            
            return secrets
            
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return {}
    
    def delete_secret(self, secret_id: str) -> bool:
        """Delete a secret from Secret Manager"""
        if not self.client:
            logger.error("Secret Manager client not available")
            return False
        
        try:
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            self.client.delete_secret(request={"name": name})
            
            logger.info(f"Deleted secret: {secret_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_id}: {e}")
            return False


class HTXSecretsManager:
    """HTX-specific secrets management"""
    
    SECRET_MAPPING = {
        "htx-api-key": "HTX API Key for trading operations",
        "htx-api-secret": "HTX API Secret for signing requests",
        "htx-subuid": "HTX Sub-account UID",
        "openai-api-key": "OpenAI API Key for ML analytics",
        "threecommas-api-key": "3Commas API Key for portfolio sync",
        "threecommas-api-secret": "3Commas API Secret",
        "gcp-service-account-key": "GCP Service Account JSON key",
        "encryption-key": "Local encryption key for sensitive data"
    }
    
    def __init__(self, project_id: str):
        self.secret_manager = SecretManagerService(project_id)
        self.project_id = project_id
    
    def setup_all_secrets(self) -> Dict[str, bool]:
        """Create all required secrets in Secret Manager"""
        results = {}
        
        for secret_id, description in self.SECRET_MAPPING.items():
            success = self.secret_manager.create_secret(secret_id, description)
            results[secret_id] = success
        
        return results
    
    def store_api_keys(self, api_keys: Dict[str, str]) -> Dict[str, bool]:
        """Store multiple API keys at once"""
        results = {}
        
        key_mapping = {
            "HTX_API_KEY": "htx-api-key",
            "HTX_API_SECRET": "htx-api-secret", 
            "HTX_SUBUID": "htx-subuid",
            "OPENAI_API_KEY": "openai-api-key",
            "THREECOMMAS_API_KEY": "threecommas-api-key",
            "THREECOMMAS_API_SECRET": "threecommas-api-secret",
            "ENCRYPTION_KEY": "encryption-key"
        }
        
        for env_key, secret_id in key_mapping.items():
            if env_key in api_keys:
                success = self.secret_manager.store_secret(secret_id, api_keys[env_key])
                results[secret_id] = success
        
        return results
    
    def get_all_secrets(self) -> Dict[str, Optional[str]]:
        """Retrieve all HTX-related secrets"""
        secrets = {}
        
        for secret_id in self.SECRET_MAPPING.keys():
            value = self.secret_manager.get_secret(secret_id)
            secrets[secret_id] = value
        
        return secrets
    
    def generate_env_file(self, output_path: str = ".env") -> bool:
        """Generate .env file from Secret Manager values"""
        try:
            secrets = self.get_all_secrets()
            
            env_mapping = {
                "htx-api-key": "HTX_API_KEY",
                "htx-api-secret": "HTX_API_SECRET",
                "htx-subuid": "HTX_SUBUID", 
                "openai-api-key": "OPENAI_API_KEY",
                "threecommas-api-key": "THREECOMMAS_API_KEY",
                "threecommas-api-secret": "THREECOMMAS_API_SECRET",
                "encryption-key": "ENCRYPTION_KEY"
            }
            
            env_content = [
                "# HTX Project Environment Configuration",
                "# Generated from Google Secret Manager",
                f"# Project ID: {self.project_id}",
                ""
            ]
            
            # GCP Configuration
            env_content.extend([
                "# Google Cloud Platform Configuration",
                f"GCP_PROJECT_ID={self.project_id}",
                "GOOGLE_APPLICATION_CREDENTIALS=./gcp-service-account.json",
                ""
            ])
            
            # API Keys from Secret Manager
            env_content.append("# API Keys (from Google Secret Manager)")
            
            for secret_id, env_key in env_mapping.items():
                value = secrets.get(secret_id)
                if value:
                    env_content.append(f"{env_key}={value}")
                else:
                    env_content.append(f"# {env_key}=<not-set>")
            
            # Write to file
            with open(output_path, 'w') as f:
                f.write('\n'.join(env_content))
            
            logger.info(f"Generated .env file: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate .env file: {e}")
            return False
    
    def validate_setup(self) -> Dict[str, Any]:
        """Validate Secret Manager setup and connectivity"""
        validation_results = {
            "secret_manager_available": self.secret_manager.client is not None,
            "project_id": self.project_id,
            "secrets_found": {},
            "missing_secrets": [],
            "recommendations": []
        }
        
        if not validation_results["secret_manager_available"]:
            validation_results["recommendations"].append(
                "Install google-cloud-secret-manager library"
            )
            return validation_results
        
        # Check each required secret
        for secret_id in self.SECRET_MAPPING.keys():
            value = self.secret_manager.get_secret(secret_id)
            validation_results["secrets_found"][secret_id] = value is not None
            
            if not value:
                validation_results["missing_secrets"].append(secret_id)
        
        # Generate recommendations
        if validation_results["missing_secrets"]:
            validation_results["recommendations"].append(
                f"Set up missing secrets: {', '.join(validation_results['missing_secrets'])}"
            )
        
        return validation_results


def get_secrets_manager(project_id: str) -> HTXSecretsManager:
    """Factory function to get HTX secrets manager"""
    return HTXSecretsManager(project_id)