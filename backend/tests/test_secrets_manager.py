"""
Unit tests for Secret Manager functionality
Tests the Secret Manager core module and services
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, Optional

from app.core.secrets_manager import SecretsManager, get_secrets_manager, reset_secrets_manager
from app.services.secret_manager import SecretManagerService, HTXSecretsManager


class TestSecretsManager:
    """Test cases for the core SecretsManager class"""
    
    def setup_method(self):
        """Setup for each test method"""
        reset_secrets_manager()
    
    def test_secrets_manager_initialization_no_project_id(self):
        """Test SecretsManager initialization without project ID"""
        with patch('app.core.secrets_manager.settings') as mock_settings:
            mock_settings.GCP_PROJECT_ID = None
            
            manager = SecretsManager()
            assert manager.project_id is None
            assert not manager.is_available
    
    def test_secrets_manager_initialization_with_project_id(self):
        """Test SecretsManager initialization with project ID"""
        with patch('app.core.secrets_manager.settings') as mock_settings, \
             patch('app.core.secrets_manager.HTXSecretsManager') as mock_htx, \
             patch('app.core.secrets_manager.SecretManagerService') as mock_service:
            
            mock_settings.GCP_PROJECT_ID = "test-project"
            mock_htx.return_value = Mock()
            mock_service_instance = Mock()
            mock_service_instance.client = Mock()
            mock_service.return_value = mock_service_instance
            
            manager = SecretsManager("test-project")
            assert manager.project_id == "test-project"
            assert manager.is_available
    
    @pytest.mark.asyncio
    async def test_get_secret_not_available(self):
        """Test get_secret when manager is not available"""
        manager = SecretsManager()
        manager.base_service = None
        
        result = await manager.get_secret("test-secret")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_secret_success(self):
        """Test successful secret retrieval"""
        manager = SecretsManager()
        manager.base_service = Mock()
        manager.base_service.client = Mock()
        manager.base_service.get_secret.return_value = "secret-value"
        
        result = await manager.get_secret("test-secret")
        assert result == "secret-value"
        manager.base_service.get_secret.assert_called_once_with("test-secret")
    
    @pytest.mark.asyncio
    async def test_get_secret_exception(self):
        """Test get_secret with exception"""
        manager = SecretsManager()
        manager.base_service = Mock()
        manager.base_service.client = Mock()
        manager.base_service.get_secret.side_effect = Exception("Secret not found")
        
        result = await manager.get_secret("test-secret")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_or_update_secret_success(self):
        """Test successful secret creation/update"""
        manager = SecretsManager()
        manager.base_service = Mock()
        manager.base_service.client = Mock()
        manager.base_service.create_secret.return_value = True
        manager.base_service.store_secret.return_value = True
        
        result = await manager.create_or_update_secret("test-secret", "test-value")
        assert result is True
        manager.base_service.create_secret.assert_called_once()
        manager.base_service.store_secret.assert_called_once_with("test-secret", "test-value")
    
    @pytest.mark.asyncio
    async def test_delete_secret_success(self):
        """Test successful secret deletion"""
        manager = SecretsManager()
        manager.base_service = Mock()
        manager.base_service.client = Mock()
        manager.base_service.delete_secret.return_value = True
        
        result = await manager.delete_secret("test-secret")
        assert result is True
        manager.base_service.delete_secret.assert_called_once_with("test-secret")
    
    @pytest.mark.asyncio
    async def test_list_secrets_success(self):
        """Test successful secrets listing"""
        manager = SecretsManager()
        manager.base_service = Mock()
        manager.base_service.client = Mock()
        expected_secrets = {"secret1": {"name": "secret1"}, "secret2": {"name": "secret2"}}
        manager.base_service.list_secrets.return_value = expected_secrets
        
        result = await manager.list_secrets()
        assert result == expected_secrets
        manager.base_service.list_secrets.assert_called_once()
    
    def test_get_all_htx_secrets_success(self):
        """Test successful HTX secrets retrieval"""
        manager = SecretsManager()
        manager.htx_secrets = Mock()
        manager.base_service = Mock()
        manager.base_service.client = Mock()
        expected_secrets = {"htx-api-key": "test-key", "htx-api-secret": "test-secret"}
        manager.htx_secrets.get_all_secrets.return_value = expected_secrets
        
        result = manager.get_all_htx_secrets()
        assert result == expected_secrets
        manager.htx_secrets.get_all_secrets.assert_called_once()
    
    def test_validate_setup_not_available(self):
        """Test validate_setup when manager is not available"""
        manager = SecretsManager()
        manager.htx_secrets = None
        
        result = manager.validate_setup()
        assert result["secret_manager_available"] is False
        assert "error" in result
    
    def test_validate_setup_success(self):
        """Test successful setup validation"""
        manager = SecretsManager()
        manager.htx_secrets = Mock()
        manager.base_service = Mock()
        manager.base_service.client = Mock()
        expected_validation = {
            "secret_manager_available": True,
            "project_id": "test-project",
            "secrets_found": {"htx-api-key": True},
            "missing_secrets": [],
            "recommendations": []
        }
        manager.htx_secrets.validate_setup.return_value = expected_validation
        
        result = manager.validate_setup()
        assert result == expected_validation
        manager.htx_secrets.validate_setup.assert_called_once()


class TestSecretsManagerDependency:
    """Test cases for dependency injection functions"""
    
    def setup_method(self):
        """Setup for each test method"""
        reset_secrets_manager()
    
    def test_get_secrets_manager_singleton(self):
        """Test that get_secrets_manager returns singleton"""
        with patch('app.core.secrets_manager.SecretsManager') as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance
            
            # First call
            manager1 = get_secrets_manager()
            # Second call
            manager2 = get_secrets_manager()
            
            # Should be the same instance
            assert manager1 is manager2
            # SecretsManager should only be called once
            mock_manager.assert_called_once()
    
    def test_reset_secrets_manager(self):
        """Test reset_secrets_manager function"""
        with patch('app.core.secrets_manager.SecretsManager') as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance
            
            # Get manager
            manager1 = get_secrets_manager()
            
            # Reset
            reset_secrets_manager()
            
            # Get manager again
            manager2 = get_secrets_manager()
            
            # Should be different instances
            assert manager1 is not manager2
            # SecretsManager should be called twice
            assert mock_manager.call_count == 2


class TestSecretManagerService:
    """Test cases for the SecretManagerService class"""
    
    def test_init_no_gcp_client(self):
        """Test initialization without GCP client"""
        with patch('app.services.secret_manager.secretmanager', side_effect=ImportError):
            service = SecretManagerService("test-project")
            assert service.project_id == "test-project"
            assert service.client is None
    
    def test_init_with_gcp_client(self):
        """Test initialization with GCP client"""
        with patch('app.services.secret_manager.secretmanager') as mock_secretmanager:
            mock_client = Mock()
            mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
            
            service = SecretManagerService("test-project")
            assert service.project_id == "test-project"
            assert service.client is mock_client
    
    def test_create_secret_no_client(self):
        """Test create_secret without client"""
        service = SecretManagerService("test-project")
        service.client = None
        
        result = service.create_secret("test-secret", "Test description")
        assert result is False
    
    def test_create_secret_success(self):
        """Test successful secret creation"""
        with patch('app.services.secret_manager.secretmanager') as mock_secretmanager:
            mock_client = Mock()
            mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
            mock_client.create_secret.return_value = Mock()
            
            service = SecretManagerService("test-project")
            result = service.create_secret("test-secret", "Test description")
            assert result is True
            mock_client.create_secret.assert_called_once()
    
    def test_store_secret_success(self):
        """Test successful secret storage"""
        with patch('app.services.secret_manager.secretmanager') as mock_secretmanager:
            mock_client = Mock()
            mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
            mock_client.add_secret_version.return_value = Mock(name="test-version")
            
            service = SecretManagerService("test-project")
            result = service.store_secret("test-secret", "test-value")
            assert result is True
            mock_client.add_secret_version.assert_called_once()
    
    def test_get_secret_success(self):
        """Test successful secret retrieval"""
        with patch('app.services.secret_manager.secretmanager') as mock_secretmanager:
            mock_client = Mock()
            mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
            mock_response = Mock()
            mock_response.payload.data = b"secret-value"
            mock_client.access_secret_version.return_value = mock_response
            
            service = SecretManagerService("test-project")
            result = service.get_secret("test-secret")
            assert result == "secret-value"
            mock_client.access_secret_version.assert_called_once()


class TestHTXSecretsManager:
    """Test cases for the HTXSecretsManager class"""
    
    def test_init(self):
        """Test HTXSecretsManager initialization"""
        with patch('app.services.secret_manager.SecretManagerService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            htx_manager = HTXSecretsManager("test-project")
            assert htx_manager.project_id == "test-project"
            assert htx_manager.secret_manager is mock_service_instance
            mock_service.assert_called_once_with("test-project")
    
    def test_setup_all_secrets(self):
        """Test setup_all_secrets method"""
        with patch('app.services.secret_manager.SecretManagerService') as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.create_secret.return_value = True
            mock_service.return_value = mock_service_instance
            
            htx_manager = HTXSecretsManager("test-project")
            result = htx_manager.setup_all_secrets()
            
            # Should have results for all secrets in SECRET_MAPPING
            assert len(result) == len(htx_manager.SECRET_MAPPING)
            assert all(value is True for value in result.values())
    
    def test_store_api_keys(self):
        """Test store_api_keys method"""
        with patch('app.services.secret_manager.SecretManagerService') as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.store_secret.return_value = True
            mock_service.return_value = mock_service_instance
            
            htx_manager = HTXSecretsManager("test-project")
            api_keys = {
                "HTX_API_KEY": "test-htx-key",
                "OPENAI_API_KEY": "test-openai-key"
            }
            result = htx_manager.store_api_keys(api_keys)
            
            assert "htx-api-key" in result
            assert "openai-api-key" in result
            assert result["htx-api-key"] is True
            assert result["openai-api-key"] is True
    
    def test_get_all_secrets(self):
        """Test get_all_secrets method"""
        with patch('app.services.secret_manager.SecretManagerService') as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.get_secret.side_effect = lambda x: f"value-for-{x}"
            mock_service.return_value = mock_service_instance
            
            htx_manager = HTXSecretsManager("test-project")
            result = htx_manager.get_all_secrets()
            
            # Should have all secrets from SECRET_MAPPING
            assert len(result) == len(htx_manager.SECRET_MAPPING)
            for secret_id in htx_manager.SECRET_MAPPING.keys():
                assert result[secret_id] == f"value-for-{secret_id}"
    
    def test_validate_setup_not_available(self):
        """Test validate_setup when Secret Manager is not available"""
        with patch('app.services.secret_manager.SecretManagerService') as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.client = None
            mock_service.return_value = mock_service_instance
            
            htx_manager = HTXSecretsManager("test-project")
            result = htx_manager.validate_setup()
            
            assert result["secret_manager_available"] is False
            assert "Install google-cloud-secret-manager library" in result["recommendations"]
    
    def test_validate_setup_missing_secrets(self):
        """Test validate_setup with missing secrets"""
        with patch('app.services.secret_manager.SecretManagerService') as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.client = Mock()
            mock_service_instance.get_secret.return_value = None  # All secrets missing
            mock_service.return_value = mock_service_instance
            
            htx_manager = HTXSecretsManager("test-project")
            result = htx_manager.validate_setup()
            
            assert result["secret_manager_available"] is True
            assert len(result["missing_secrets"]) == len(htx_manager.SECRET_MAPPING)
            assert any("Set up missing secrets" in rec for rec in result["recommendations"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])