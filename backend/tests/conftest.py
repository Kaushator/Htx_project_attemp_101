"""
Pytest configuration and fixtures for HTX Project tests.

This file provides shared fixtures and mocks to avoid hitting external services during testing.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

import pandas as pd
from fastapi.testclient import TestClient


# ============================================
# Core Application Fixtures
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    class MockSettings:
        def __init__(self):
            # Database
            self.DATABASE_URL = "sqlite:///./test.db"
            self.DATABASE_ECHO = False
            
            # HTX API
            self.HTX_API_KEY = "test_api_key"
            self.HTX_SECRET_KEY = "test_secret_key"
            self.HTX_BASE_URL = "https://api.huobi.pro"
            
            # GCP Configuration
            self.GCP_PROJECT_ID = "test-project"
            self.GCP_STORAGE_BUCKET = "test-bucket"
            self.GOOGLE_APPLICATION_CREDENTIALS = "/tmp/test-credentials.json"
            self.GCP_USE_DEFAULT_CREDENTIALS = False
            
            # ML/AI Configuration
            self.OPENAI_API_KEY = "test_openai_key"
            self.VERTEX_AI_PROJECT = "test-vertex-project"
            self.VERTEX_AI_LOCATION = "us-central1"
            
            # Application
            self.DEBUG = True
            self.LOG_LEVEL = "INFO"
            self.CACHE_TTL = 300
            
        @property
        def gcp_enabled(self) -> bool:
            return bool(self.GCP_PROJECT_ID and self.GOOGLE_APPLICATION_CREDENTIALS)
            
        @property
        def gcp_storage_enabled(self) -> bool:
            return self.gcp_enabled and bool(self.GCP_STORAGE_BUCKET)
    
    return MockSettings()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_trades_data():
    """Sample trades data for testing"""
    return pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='1H'),
        'symbol': ['BTC/USDT', 'ETH/USDT'] * 50,
        'side': ['buy', 'sell'] * 50,
        'amount': [0.1, 0.5, 1.0, 2.0] * 25,
        'price': [45000, 46000, 3000, 3100] * 25,
        'fee': [0.001, 0.002] * 50,
        'pnl': [100, -50, 200, -75] * 25
    })


# ============================================
# GCP Service Mocks
# ============================================

@pytest.fixture
def mock_gcp_storage():
    """Mock Google Cloud Storage"""
    with patch('google.cloud.storage.Client') as mock_client:
        # Mock client instance
        client_instance = Mock()
        mock_client.from_service_account_json.return_value = client_instance
        mock_client.return_value = client_instance
        
        # Mock bucket
        bucket = Mock()
        bucket.name = 'test-bucket'
        client_instance.bucket.return_value = bucket
        
        # Mock blob
        blob = Mock()
        blob.name = 'test-file.csv'
        blob.size = 1024
        blob.content_type = 'text/csv'
        blob.time_created = datetime.utcnow()
        blob.updated = datetime.utcnow()
        blob.exists.return_value = True
        blob.upload_from_file = Mock()
        blob.download_to_file = Mock()
        blob.delete = Mock()
        blob.generate_signed_url.return_value = "https://storage.googleapis.com/signed-url"
        bucket.blob.return_value = blob
        bucket.list_blobs.return_value = [blob]
        
        yield {
            'client': mock_client,
            'client_instance': client_instance,
            'bucket': bucket,
            'blob': blob
        }


@pytest.fixture
def mock_gcp_secrets():
    """Mock Google Cloud Secret Manager"""
    with patch('google.cloud.secretmanager.SecretManagerServiceClient') as mock_client:
        client_instance = Mock()
        mock_client.return_value = client_instance
        
        # Mock secret operations
        client_instance.access_secret_version.return_value.payload.data = b'{"test": "secret"}'
        client_instance.create_secret.return_value = Mock(name='projects/test/secrets/test-secret')
        client_instance.add_secret_version.return_value = Mock()
        client_instance.delete_secret.return_value = Mock()
        client_instance.list_secrets.return_value = [
            Mock(name='projects/test/secrets/secret1'),
            Mock(name='projects/test/secrets/secret2')
        ]
        
        yield client_instance


@pytest.fixture
def mock_vertex_ai():
    """Mock Google Cloud Vertex AI"""
    with patch('google.cloud.aiplatform.gapic.JobServiceClient') as mock_job_client, \
         patch('google.cloud.aiplatform.CustomTrainingJob') as mock_training_job:
        
        job_client_instance = Mock()
        mock_job_client.return_value = job_client_instance
        
        training_job_instance = Mock()
        training_job_instance.run.return_value = Mock(resource_name='test-job')
        mock_training_job.return_value = training_job_instance
        
        yield {
            'job_client': job_client_instance,
            'training_job': training_job_instance
        }


# ============================================
# Database Mocks
# ============================================

@pytest.fixture
def mock_database():
    """Mock database session"""
    with patch('app.db.session.get_async_session') as mock_session:
        session = AsyncMock()
        session.execute.return_value.scalars.return_value.all.return_value = []
        session.commit.return_value = None
        session.rollback.return_value = None
        session.close.return_value = None
        mock_session.return_value = session
        yield session


# ============================================
# External API Mocks
# ============================================

@pytest.fixture
def mock_htx_api():
    """Mock HTX API client"""
    with patch('aiohttp.ClientSession') as mock_session:
        session_instance = AsyncMock()
        mock_session.return_value.__aenter__.return_value = session_instance
        
        # Mock successful responses
        response = AsyncMock()
        response.status = 200
        response.json.return_value = {
            'status': 'ok',
            'data': {'balance': [{'currency': 'btc', 'balance': '1.0'}]}
        }
        session_instance.get.return_value.__aenter__.return_value = response
        session_instance.post.return_value.__aenter__.return_value = response
        
        yield session_instance


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    with patch('openai.OpenAI') as mock_client:
        client_instance = Mock()
        mock_client.return_value = client_instance
        
        # Mock completion response
        completion = Mock()
        completion.choices = [Mock(message=Mock(content="Test AI response"))]
        client_instance.chat.completions.create.return_value = completion
        
        yield client_instance


# ============================================
# WebSocket Mocks
# ============================================

@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    websocket = AsyncMock()
    websocket.closed = False
    websocket.send.return_value = None
    websocket.recv.return_value = '{"test": "message"}'
    websocket.close.return_value = None
    return websocket


# ============================================
# Test Client
# ============================================

@pytest.fixture
def test_client(mock_settings, mock_database, mock_gcp_storage):
    """Create test client with mocked dependencies"""
    # Import here to avoid circular imports
    from app.main import app
    
    with patch('app.core.config.settings', mock_settings):
        client = TestClient(app)
        yield client


# ============================================
# Auto-use fixtures for common mocks
# ============================================

@pytest.fixture(autouse=True)
def mock_external_services(mock_gcp_storage, mock_gcp_secrets, mock_htx_api):
    """Automatically mock external services for all tests"""
    pass


# ============================================
# Utility Functions
# ============================================

def create_mock_file(content: str = "test,data\n1,2", filename: str = "test.csv"):
    """Create a mock file-like object"""
    from io import StringIO
    file_obj = StringIO(content)
    file_obj.name = filename
    return file_obj


def create_mock_binary_file(content: bytes = b"test,data\n1,2", filename: str = "test.csv"):
    """Create a mock binary file-like object"""
    from io import BytesIO
    file_obj = BytesIO(content)
    file_obj.name = filename
    return file_obj