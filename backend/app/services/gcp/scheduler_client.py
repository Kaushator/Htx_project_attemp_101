"""
Google Cloud Scheduler Client

This module provides an async-compatible interface for Google Cloud Scheduler operations
including job creation, management, and monitoring for the HTX trading platform.
"""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from google.cloud import scheduler
from google.cloud.scheduler_v1 import Job
from google.auth.exceptions import DefaultCredentialsError
from google.api_core import exceptions as gcp_exceptions
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class SchedulerClientError(Exception):
    """Custom exception for Scheduler Client errors"""
    pass


class SchedulerClient:
    """
    Async-compatible Google Cloud Scheduler client for the HTX trading platform.
    
    Provides methods for:
    - Creating and managing scheduled jobs
    - HTTP and Pub/Sub target configurations
    - Job lifecycle management (pause/resume/delete)
    - Monitoring job status and execution
    """
    
    def __init__(self, settings):
        """
        Initialize the Scheduler Client with configuration settings.
        
        Args:
            settings: Application settings containing GCP configuration
        """
        self.settings = settings
        self.project_id = settings.GCP_PROJECT_ID
        self.location = settings.SCHEDULER_LOCATION
        self.time_zone = settings.SCHEDULER_TIME_ZONE
        self._client: Optional[scheduler.CloudSchedulerClient] = None
        self._executor = ThreadPoolExecutor(max_workers=5)
        
        # Initialize client if credentials are available
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Google Cloud Scheduler client"""
        try:
            if self.settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Use service account credentials
                self._client = scheduler.CloudSchedulerClient.from_service_account_json(
                    self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                # Use default credentials
                self._client = scheduler.CloudSchedulerClient()
            
            logger.info("Initialized Cloud Scheduler client successfully")
            
        except DefaultCredentialsError:
            logger.warning("GCP credentials not found. Scheduler client will be disabled.")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize Scheduler client: {e}")
            raise SchedulerClientError(f"Failed to initialize Scheduler client: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if the Scheduler client is properly configured and available"""
        return self._client is not None
    
    def _get_parent_path(self) -> str:
        """Get the parent path for the location"""
        return f"projects/{self.project_id}/locations/{self.location}"
    
    def _get_job_path(self, job_name: str) -> str:
        """Get the full job path"""
        return f"projects/{self.project_id}/locations/{self.location}/jobs/{job_name}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_http_job(
        self,
        job_name: str,
        schedule: str,
        target_uri: str,
        http_method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[str, Dict[str, Any]]] = None,
        description: str = None,
        time_zone: str = None
    ) -> str:
        """
        Create a scheduled job with HTTP target.
        
        Args:
            job_name: Name of the job to create
            schedule: Cron schedule expression
            target_uri: HTTP endpoint URL to call
            http_method: HTTP method (GET, POST, PUT, DELETE)
            headers: Optional HTTP headers
            body: Optional request body (string or dict that will be JSON serialized)
            description: Optional job description
            time_zone: Optional time zone (defaults to UTC)
            
        Returns:
            The full job path
            
        Raises:
            SchedulerClientError: If job creation fails
        """
        if not self.is_available:
            raise SchedulerClientError("Scheduler client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            job_path = await loop.run_in_executor(
                self._executor,
                self._create_http_job_sync,
                job_name,
                schedule,
                target_uri,
                http_method,
                headers or {},
                body,
                description,
                time_zone or self.time_zone
            )
            
            logger.info(f"Created HTTP job: {job_path}")
            return job_path
            
        except Exception as e:
            logger.error(f"Failed to create HTTP job {job_name}: {e}")
            raise SchedulerClientError(f"HTTP job creation failed: {e}")
    
    def _create_http_job_sync(
        self,
        job_name: str,
        schedule: str,
        target_uri: str,
        http_method: str,
        headers: Dict[str, str],
        body: Optional[Union[str, Dict[str, Any]]],
        description: Optional[str],
        time_zone: str
    ) -> str:
        """Synchronous HTTP job creation implementation"""
        parent = self._get_parent_path()
        
        # Prepare request body
        request_body = None
        if body:
            if isinstance(body, dict):
                request_body = json.dumps(body).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            else:
                request_body = body.encode('utf-8')
        
        # Create HTTP target
        http_target = {
            "uri": target_uri,
            "http_method": getattr(scheduler.HttpMethod, http_method.upper()),
            "headers": headers
        }
        
        if request_body:
            http_target["body"] = request_body
        
        # Create job configuration
        job = {
            "name": self._get_job_path(job_name),
            "description": description or f"HTTP job for {target_uri}",
            "schedule": schedule,
            "time_zone": time_zone,
            "http_target": http_target
        }
        
        # Create the job
        try:
            response = self._client.create_job(parent=parent, job=job)
            return response.name
        except gcp_exceptions.AlreadyExists:
            # Job already exists, return its path
            return self._get_job_path(job_name)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_pubsub_job(
        self,
        job_name: str,
        schedule: str,
        topic_name: str,
        data: Optional[Dict[str, Any]] = None,
        attributes: Optional[Dict[str, str]] = None,
        description: str = None,
        time_zone: str = None
    ) -> str:
        """
        Create a scheduled job with Pub/Sub target.
        
        Args:
            job_name: Name of the job to create
            schedule: Cron schedule expression
            topic_name: Pub/Sub topic name to publish to
            data: Optional message data (will be JSON serialized)
            attributes: Optional message attributes
            description: Optional job description
            time_zone: Optional time zone (defaults to UTC)
            
        Returns:
            The full job path
            
        Raises:
            SchedulerClientError: If job creation fails
        """
        if not self.is_available:
            raise SchedulerClientError("Scheduler client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            job_path = await loop.run_in_executor(
                self._executor,
                self._create_pubsub_job_sync,
                job_name,
                schedule,
                topic_name,
                data,
                attributes or {},
                description,
                time_zone or self.time_zone
            )
            
            logger.info(f"Created Pub/Sub job: {job_path}")
            return job_path
            
        except Exception as e:
            logger.error(f"Failed to create Pub/Sub job {job_name}: {e}")
            raise SchedulerClientError(f"Pub/Sub job creation failed: {e}")
    
    def _create_pubsub_job_sync(
        self,
        job_name: str,
        schedule: str,
        topic_name: str,
        data: Optional[Dict[str, Any]],
        attributes: Dict[str, str],
        description: Optional[str],
        time_zone: str
    ) -> str:
        """Synchronous Pub/Sub job creation implementation"""
        parent = self._get_parent_path()
        
        # Create topic path
        topic_path = f"projects/{self.project_id}/topics/{topic_name}"
        
        # Prepare message data
        message_data = None
        if data:
            message_data = json.dumps(data, default=str).encode('utf-8')
        
        # Add default attributes
        attributes.update({
            "source": "cloud-scheduler",
            "job_name": job_name,
            "created_at": datetime.utcnow().isoformat()
        })
        
        # Create Pub/Sub target
        pubsub_target = {
            "topic_name": topic_path,
            "attributes": attributes
        }
        
        if message_data:
            pubsub_target["data"] = message_data
        
        # Create job configuration
        job = {
            "name": self._get_job_path(job_name),
            "description": description or f"Pub/Sub job for topic {topic_name}",
            "schedule": schedule,
            "time_zone": time_zone,
            "pubsub_target": pubsub_target
        }
        
        # Create the job
        try:
            response = self._client.create_job(parent=parent, job=job)
            return response.name
        except gcp_exceptions.AlreadyExists:
            # Job already exists, return its path
            return self._get_job_path(job_name)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def pause_job(self, job_name: str) -> bool:
        """
        Pause a scheduled job.
        
        Args:
            job_name: Name of the job to pause
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            SchedulerClientError: If pausing fails
        """
        if not self.is_available:
            raise SchedulerClientError("Scheduler client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self._executor,
                self._pause_job_sync,
                job_name
            )
            
            logger.info(f"Paused job: {job_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to pause job {job_name}: {e}")
            raise SchedulerClientError(f"Job pause failed: {e}")
    
    def _pause_job_sync(self, job_name: str) -> bool:
        """Synchronous job pause implementation"""
        job_path = self._get_job_path(job_name)
        
        try:
            self._client.pause_job(name=job_path)
            return True
        except gcp_exceptions.NotFound:
            logger.warning(f"Job {job_name} not found")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def resume_job(self, job_name: str) -> bool:
        """
        Resume a paused job.
        
        Args:
            job_name: Name of the job to resume
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            SchedulerClientError: If resuming fails
        """
        if not self.is_available:
            raise SchedulerClientError("Scheduler client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self._executor,
                self._resume_job_sync,
                job_name
            )
            
            logger.info(f"Resumed job: {job_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to resume job {job_name}: {e}")
            raise SchedulerClientError(f"Job resume failed: {e}")
    
    def _resume_job_sync(self, job_name: str) -> bool:
        """Synchronous job resume implementation"""
        job_path = self._get_job_path(job_name)
        
        try:
            self._client.resume_job(name=job_path)
            return True
        except gcp_exceptions.NotFound:
            logger.warning(f"Job {job_name} not found")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def delete_job(self, job_name: str) -> bool:
        """
        Delete a scheduled job.
        
        Args:
            job_name: Name of the job to delete
            
        Returns:
            True if successful, False if job not found
            
        Raises:
            SchedulerClientError: If deletion fails
        """
        if not self.is_available:
            raise SchedulerClientError("Scheduler client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self._executor,
                self._delete_job_sync,
                job_name
            )
            
            logger.info(f"Deleted job: {job_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete job {job_name}: {e}")
            raise SchedulerClientError(f"Job deletion failed: {e}")
    
    def _delete_job_sync(self, job_name: str) -> bool:
        """Synchronous job deletion implementation"""
        job_path = self._get_job_path(job_name)
        
        try:
            self._client.delete_job(name=job_path)
            return True
        except gcp_exceptions.NotFound:
            logger.warning(f"Job {job_name} not found")
            return False
    
    async def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all scheduled jobs in the location.
        
        Returns:
            List of job information dictionaries
            
        Raises:
            SchedulerClientError: If listing fails
        """
        if not self.is_available:
            raise SchedulerClientError("Scheduler client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            jobs = await loop.run_in_executor(
                self._executor,
                self._list_jobs_sync
            )
            
            logger.info(f"Found {len(jobs)} scheduled jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            raise SchedulerClientError(f"Job listing failed: {e}")
    
    def _list_jobs_sync(self) -> List[Dict[str, Any]]:
        """Synchronous job listing implementation"""
        parent = self._get_parent_path()
        
        jobs = []
        for job in self._client.list_jobs(parent=parent):
            job_info = {
                "name": job.name.split('/')[-1],  # Extract just the job name
                "full_name": job.name,
                "description": job.description,
                "schedule": job.schedule,
                "time_zone": job.time_zone,
                "state": job.state.name,
                "last_attempt_time": job.last_attempt_time,
                "user_update_time": job.user_update_time
            }
            
            # Add target-specific information
            if job.http_target:
                job_info.update({
                    "target_type": "http",
                    "target_uri": job.http_target.uri,
                    "http_method": job.http_target.http_method.name
                })
            elif job.pubsub_target:
                job_info.update({
                    "target_type": "pubsub",
                    "topic_name": job.pubsub_target.topic_name.split('/')[-1]
                })
            
            jobs.append(job_info)
        
        return jobs
    
    async def get_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific job.
        
        Args:
            job_name: Name of the job to retrieve
            
        Returns:
            Job information dictionary, or None if not found
            
        Raises:
            SchedulerClientError: If retrieval fails
        """
        if not self.is_available:
            raise SchedulerClientError("Scheduler client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            job_info = await loop.run_in_executor(
                self._executor,
                self._get_job_sync,
                job_name
            )
            
            if job_info:
                logger.info(f"Retrieved job: {job_name}")
            return job_info
            
        except Exception as e:
            logger.error(f"Failed to get job {job_name}: {e}")
            raise SchedulerClientError(f"Job retrieval failed: {e}")
    
    def _get_job_sync(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Synchronous job retrieval implementation"""
        job_path = self._get_job_path(job_name)
        
        try:
            job = self._client.get_job(name=job_path)
            
            job_info = {
                "name": job.name.split('/')[-1],
                "full_name": job.name,
                "description": job.description,
                "schedule": job.schedule,
                "time_zone": job.time_zone,
                "state": job.state.name,
                "last_attempt_time": job.last_attempt_time,
                "user_update_time": job.user_update_time,
                "schedule_time": job.schedule_time
            }
            
            # Add target-specific information
            if job.http_target:
                job_info.update({
                    "target_type": "http",
                    "target_uri": job.http_target.uri,
                    "http_method": job.http_target.http_method.name,
                    "headers": dict(job.http_target.headers),
                    "body": job.http_target.body.decode('utf-8') if job.http_target.body else None
                })
            elif job.pubsub_target:
                job_info.update({
                    "target_type": "pubsub",
                    "topic_name": job.pubsub_target.topic_name.split('/')[-1],
                    "attributes": dict(job.pubsub_target.attributes),
                    "data": job.pubsub_target.data.decode('utf-8') if job.pubsub_target.data else None
                })
            
            return job_info
            
        except gcp_exceptions.NotFound:
            return None
    
    async def run_job_now(self, job_name: str) -> bool:
        """
        Trigger a job to run immediately.
        
        Args:
            job_name: Name of the job to run
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            SchedulerClientError: If job execution fails
        """
        if not self.is_available:
            raise SchedulerClientError("Scheduler client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self._executor,
                self._run_job_now_sync,
                job_name
            )
            
            logger.info(f"Triggered job: {job_name}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to run job {job_name}: {e}")
            raise SchedulerClientError(f"Job execution failed: {e}")
    
    def _run_job_now_sync(self, job_name: str) -> bool:
        """Synchronous job execution implementation"""
        job_path = self._get_job_path(job_name)
        
        try:
            self._client.run_job(name=job_path)
            return True
        except gcp_exceptions.NotFound:
            logger.warning(f"Job {job_name} not found")
            return False
    
    async def close(self) -> None:
        """Close the Scheduler client and cleanup resources"""
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("Scheduler client resources cleaned up")


# Factory function for easy initialization
def create_scheduler_client(settings) -> SchedulerClient:
    """
    Factory function to create a Scheduler client.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured SchedulerClient instance
    """
    return SchedulerClient(settings)


# Utility functions for common scheduling patterns
async def setup_htx_sync_jobs(client: SchedulerClient, settings) -> List[str]:
    """
    Setup standard HTX synchronization jobs.
    
    Args:
        client: SchedulerClient instance
        settings: Application settings
        
    Returns:
        List of created job names
    """
    jobs = []
    
    # Hourly HTX sync
    if hasattr(settings, 'API_HOST') and hasattr(settings, 'API_PORT'):
        sync_url = f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1/htx/sync"
        htx_sync_job = await client.create_http_job(
            job_name="htx-hourly-sync",
            schedule=settings.SCHEDULER_HTX_SYNC_SCHEDULE,
            target_uri=sync_url,
            description="Hourly HTX API synchronization"
        )
        jobs.append(htx_sync_job.split('/')[-1])
    
    # Daily data processing
    daily_processing_job = await client.create_pubsub_job(
        job_name="daily-data-processing",
        schedule=settings.SCHEDULER_DATAFLOW_SCHEDULE,
        topic_name="dataflow-trigger",
        data={"type": "daily_processing", "source": "scheduler"},
        description="Daily data processing trigger"
    )
    jobs.append(daily_processing_job.split('/')[-1])
    
    # Weekly model retraining
    model_retrain_job = await client.create_pubsub_job(
        job_name="weekly-model-retrain",
        schedule=settings.SCHEDULER_MODEL_RETRAIN_SCHEDULE,
        topic_name="model-retrain",
        data={"type": "model_retrain", "frequency": "weekly"},
        description="Weekly ML model retraining"
    )
    jobs.append(model_retrain_job.split('/')[-1])
    
    return jobs