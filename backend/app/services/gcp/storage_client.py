"""
Google Cloud Storage Client

This module provides an async-compatible interface for Google Cloud Storage operations
including file upload, download, listing, and URL generation for the HTX trading platform.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Union, BinaryIO
from io import BytesIO
import mimetypes

from google.cloud import storage
from google.cloud.storage import Blob
from google.auth.exceptions import DefaultCredentialsError
from google.api_core import exceptions as gcp_exceptions
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class StorageClientError(Exception):
    """Custom exception for Storage Client errors"""
    pass


class StorageClient:
    """
    Async-compatible Google Cloud Storage client for the HTX trading platform.
    
    Provides methods for:
    - Uploading files (CSV, Excel, JSON)
    - Downloading files
    - Listing files with filtering
    - Generating signed URLs for secure access
    - Managing file metadata
    """
    
    def __init__(self, settings):
        """
        Initialize the Storage Client with configuration settings.
        
        Args:
            settings: Application settings containing GCP configuration
        """
        self.settings = settings
        self.project_id = settings.GCP_PROJECT_ID
        self.bucket_name = settings.GCP_STORAGE_BUCKET
        self._client: Optional[storage.Client] = None
        self._bucket: Optional[storage.Bucket] = None
        
        # Initialize client if credentials are available
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Google Cloud Storage client"""
        try:
            if self.settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Use service account credentials
                self._client = storage.Client.from_service_account_json(
                    self.settings.GOOGLE_APPLICATION_CREDENTIALS,
                    project=self.project_id
                )
            else:
                # Use default credentials (useful for GCP environments)
                self._client = storage.Client(project=self.project_id)
            
            self._bucket = self._client.bucket(self.bucket_name)
            logger.info(f"Initialized GCS client for bucket: {self.bucket_name}")
            
        except DefaultCredentialsError:
            logger.warning("GCP credentials not found. Storage client will be disabled.")
            self._client = None
            self._bucket = None
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise StorageClientError(f"Failed to initialize Storage client: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if the storage client is properly configured and available"""
        return self._client is not None and self._bucket is not None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def upload_file(
        self,
        file_path: Union[str, Path, BinaryIO],
        blob_name: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload a file to Google Cloud Storage.
        
        Args:
            file_path: Local file path, Path object, or file-like object
            blob_name: Name for the blob in GCS (can include folders like 'uploads/file.csv')
            content_type: MIME type of the file (auto-detected if not provided)
            metadata: Additional metadata to store with the file
            
        Returns:
            The GCS URI of the uploaded file (gs://bucket/blob_name)
            
        Raises:
            StorageClientError: If upload fails
        """
        if not self.is_available:
            raise StorageClientError("Storage client is not available")
        
        try:
            # Run the blocking GCS operation in a thread pool
            loop = asyncio.get_event_loop()
            gs_uri = await loop.run_in_executor(
                None, 
                self._upload_file_sync, 
                file_path, blob_name, content_type, metadata
            )
            
            logger.info(f"Successfully uploaded file to {gs_uri}")
            return gs_uri
            
        except Exception as e:
            logger.error(f"Failed to upload file {blob_name}: {e}")
            raise StorageClientError(f"Upload failed: {e}")
    
    def _upload_file_sync(
        self,
        file_path: Union[str, Path, BinaryIO],
        blob_name: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """Synchronous file upload implementation"""
        blob = self._bucket.blob(blob_name)
        
        # Set metadata
        if metadata:
            blob.metadata = metadata
        
        # Auto-detect content type if not provided
        if not content_type:
            if hasattr(file_path, 'read'):
                # For file-like objects, try to get name
                content_type = getattr(file_path, 'content_type', None)
                if not content_type and hasattr(file_path, 'name'):
                    content_type, _ = mimetypes.guess_type(file_path.name)
            else:
                content_type, _ = mimetypes.guess_type(str(file_path))
            
            # Default to binary if can't determine
            content_type = content_type or 'application/octet-stream'
        
        blob.content_type = content_type
        
        # Upload file
        if hasattr(file_path, 'read'):
            # File-like object
            blob.upload_from_file(file_path, rewind=True)
        else:
            # File path
            blob.upload_from_filename(str(file_path))
        
        return f"gs://{self.bucket_name}/{blob_name}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def download_file(
        self,
        blob_name: str,
        destination: Union[str, Path, BinaryIO]
    ) -> bool:
        """
        Download a file from Google Cloud Storage.
        
        Args:
            blob_name: Name of the blob in GCS
            destination: Local file path or file-like object to write to
            
        Returns:
            True if download successful, False otherwise
            
        Raises:
            StorageClientError: If download fails
        """
        if not self.is_available:
            raise StorageClientError("Storage client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._download_file_sync,
                blob_name, destination
            )
            
            if success:
                logger.info(f"Successfully downloaded {blob_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to download file {blob_name}: {e}")
            raise StorageClientError(f"Download failed: {e}")
    
    def _download_file_sync(
        self,
        blob_name: str,
        destination: Union[str, Path, BinaryIO]
    ) -> bool:
        """Synchronous file download implementation"""
        try:
            blob = self._bucket.blob(blob_name)
            
            if not blob.exists():
                logger.warning(f"Blob {blob_name} does not exist")
                return False
            
            if hasattr(destination, 'write'):
                # File-like object
                blob.download_to_file(destination)
            else:
                # File path
                blob.download_to_filename(str(destination))
            
            return True
            
        except gcp_exceptions.NotFound:
            logger.warning(f"Blob {blob_name} not found")
            return False
    
    async def list_files(
        self,
        prefix: Optional[str] = None,
        max_results: Optional[int] = 1000
    ) -> List[dict]:
        """
        List files in the storage bucket.
        
        Args:
            prefix: Filter files by prefix (e.g., 'uploads/' for files in uploads folder)
            max_results: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        if not self.is_available:
            raise StorageClientError("Storage client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            files = await loop.run_in_executor(
                None,
                self._list_files_sync,
                prefix, max_results
            )
            
            logger.info(f"Listed {len(files)} files with prefix '{prefix or 'all'}'")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise StorageClientError(f"List files failed: {e}")
    
    def _list_files_sync(self, prefix: Optional[str], max_results: Optional[int]) -> List[dict]:
        """Synchronous file listing implementation"""
        blobs = self._bucket.list_blobs(prefix=prefix, max_results=max_results)
        
        files = []
        for blob in blobs:
            files.append({
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'md5_hash': blob.md5_hash,
                'gs_uri': f"gs://{self.bucket_name}/{blob.name}",
                'metadata': blob.metadata or {}
            })
        
        return files
    
    async def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from Google Cloud Storage.
        
        Args:
            blob_name: Name of the blob to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.is_available:
            raise StorageClientError("Storage client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._delete_file_sync,
                blob_name
            )
            
            if success:
                logger.info(f"Successfully deleted {blob_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete file {blob_name}: {e}")
            raise StorageClientError(f"Delete failed: {e}")
    
    def _delete_file_sync(self, blob_name: str) -> bool:
        """Synchronous file deletion implementation"""
        try:
            blob = self._bucket.blob(blob_name)
            
            if not blob.exists():
                logger.warning(f"Blob {blob_name} does not exist")
                return False
            
            blob.delete()
            return True
            
        except gcp_exceptions.NotFound:
            logger.warning(f"Blob {blob_name} not found")
            return False
    
    async def generate_signed_url(
        self,
        blob_name: str,
        expiration_minutes: int = 60,
        method: str = 'GET'
    ) -> str:
        """
        Generate a signed URL for secure file access.
        
        Args:
            blob_name: Name of the blob
            expiration_minutes: URL expiration time in minutes
            method: HTTP method ('GET', 'PUT', 'POST')
            
        Returns:
            Signed URL string
        """
        if not self.is_available:
            raise StorageClientError("Storage client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            signed_url = await loop.run_in_executor(
                None,
                self._generate_signed_url_sync,
                blob_name, expiration_minutes, method
            )
            
            logger.info(f"Generated signed URL for {blob_name} (expires in {expiration_minutes}m)")
            return signed_url
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
            raise StorageClientError(f"Signed URL generation failed: {e}")
    
    def _generate_signed_url_sync(
        self,
        blob_name: str,
        expiration_minutes: int,
        method: str
    ) -> str:
        """Synchronous signed URL generation implementation"""
        blob = self._bucket.blob(blob_name)
        
        expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        
        signed_url = blob.generate_signed_url(
            expiration=expiration,
            method=method,
            version='v4'
        )
        
        return signed_url
    
    async def file_exists(self, blob_name: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            blob_name: Name of the blob to check
            
        Returns:
            True if file exists, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            exists = await loop.run_in_executor(
                None,
                self._file_exists_sync,
                blob_name
            )
            return exists
            
        except Exception as e:
            logger.error(f"Failed to check if file exists {blob_name}: {e}")
            return False
    
    def _file_exists_sync(self, blob_name: str) -> bool:
        """Synchronous file existence check implementation"""
        blob = self._bucket.blob(blob_name)
        return blob.exists()
    
    async def get_file_metadata(self, blob_name: str) -> Optional[dict]:
        """
        Get metadata for a file in storage.
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            File metadata dictionary or None if file doesn't exist
        """
        if not self.is_available:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            metadata = await loop.run_in_executor(
                None,
                self._get_file_metadata_sync,
                blob_name
            )
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for {blob_name}: {e}")
            return None
    
    def _get_file_metadata_sync(self, blob_name: str) -> Optional[dict]:
        """Synchronous file metadata retrieval implementation"""
        try:
            blob = self._bucket.blob(blob_name)
            
            if not blob.exists():
                return None
            
            # Reload to get latest metadata
            blob.reload()
            
            return {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'md5_hash': blob.md5_hash,
                'etag': blob.etag,
                'gs_uri': f"gs://{self.bucket_name}/{blob.name}",
                'metadata': blob.metadata or {}
            }
            
        except gcp_exceptions.NotFound:
            return None