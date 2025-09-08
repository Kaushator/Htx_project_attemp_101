"""
Google Cloud Vertex AI Client

This module provides an async-compatible interface for Google Cloud Vertex AI operations
including model training, deployment, and inference for the HTX trading platform.
"""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from google.cloud import aiplatform
from google.cloud.aiplatform import gapic
from google.auth.exceptions import DefaultCredentialsError
from google.api_core import exceptions as gcp_exceptions
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class VertexAIError(Exception):
    """Custom exception for Vertex AI errors"""
    pass


class VertexAIClient:
    """
    Async-compatible Google Cloud Vertex AI client for the HTX trading platform.
    
    Provides methods for:
    - Creating and managing custom training jobs
    - Deploying models to endpoints
    - Online and batch predictions
    - Model management and versioning
    """
    
    def __init__(self, settings):
        """
        Initialize the Vertex AI Client with configuration settings.
        
        Args:
            settings: Application settings containing GCP configuration
        """
        self.settings = settings
        self.project_id = settings.GCP_PROJECT_ID
        self.location = settings.VERTEX_AI_LOCATION
        self.staging_bucket = settings.VERTEX_AI_STAGING_BUCKET
        
        # Initialize Vertex AI
        self._initialize_vertex_ai()
        
        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=5)
        
        # Client instances
        self._job_client: Optional[gapic.JobServiceClient] = None
        self._model_client: Optional[gapic.ModelServiceClient] = None
        self._endpoint_client: Optional[gapic.EndpointServiceClient] = None
        self._prediction_client: Optional[gapic.PredictionServiceClient] = None
        
        # Initialize clients
        self._initialize_clients()
    
    def _initialize_vertex_ai(self) -> None:
        """Initialize Vertex AI with project and location"""
        try:
            if self.settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Use service account credentials
                aiplatform.init(
                    project=self.project_id,
                    location=self.location,
                    staging_bucket=self.staging_bucket,
                    credentials=self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                # Use default credentials
                aiplatform.init(
                    project=self.project_id,
                    location=self.location,
                    staging_bucket=self.staging_bucket
                )
            
            logger.info(f"Initialized Vertex AI for project {self.project_id} in {self.location}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise VertexAIError(f"Failed to initialize Vertex AI: {e}")
    
    def _initialize_clients(self) -> None:
        """Initialize Vertex AI service clients"""
        try:
            if self.settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Use service account credentials
                client_options = {"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
                
                self._job_client = gapic.JobServiceClient(
                    client_options=client_options,
                    credentials=self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
                self._model_client = gapic.ModelServiceClient(
                    client_options=client_options,
                    credentials=self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
                self._endpoint_client = gapic.EndpointServiceClient(
                    client_options=client_options,
                    credentials=self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
                self._prediction_client = gapic.PredictionServiceClient(
                    client_options=client_options,
                    credentials=self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                # Use default credentials
                client_options = {"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
                
                self._job_client = gapic.JobServiceClient(client_options=client_options)
                self._model_client = gapic.ModelServiceClient(client_options=client_options)
                self._endpoint_client = gapic.EndpointServiceClient(client_options=client_options)
                self._prediction_client = gapic.PredictionServiceClient(client_options=client_options)
            
            logger.info("Initialized Vertex AI service clients successfully")
            
        except DefaultCredentialsError:
            logger.warning("GCP credentials not found. Vertex AI client will be disabled.")
            self._job_client = None
            self._model_client = None
            self._endpoint_client = None
            self._prediction_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI clients: {e}")
            raise VertexAIError(f"Failed to initialize Vertex AI clients: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if the Vertex AI clients are properly configured and available"""
        return all([
            self._job_client is not None,
            self._model_client is not None,
            self._endpoint_client is not None,
            self._prediction_client is not None
        ])
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_training_job(
        self,
        display_name: str,
        container_image_uri: str,
        model_serving_container_image_uri: str,
        args: List[str] = None,
        environment_variables: Dict[str, str] = None,
        machine_type: str = "n1-standard-4",
        replica_count: int = 1,
        accelerator_type: str = None,
        accelerator_count: int = 0
    ) -> str:
        """
        Create a custom training job in Vertex AI.
        
        Args:
            display_name: Display name for the training job
            container_image_uri: URI of the training container image
            model_serving_container_image_uri: URI of the serving container image
            args: Command line arguments for the training script
            environment_variables: Environment variables for the training job
            machine_type: Machine type for training (default: n1-standard-4)
            replica_count: Number of training replicas (default: 1)
            accelerator_type: Type of accelerator (e.g., NVIDIA_TESLA_T4)
            accelerator_count: Number of accelerators
            
        Returns:
            Training job resource name
            
        Raises:
            VertexAIError: If training job creation fails
        """
        if not self.is_available:
            raise VertexAIError("Vertex AI client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            job_name = await loop.run_in_executor(
                self._executor,
                self._create_training_job_sync,
                display_name,
                container_image_uri,
                model_serving_container_image_uri,
                args or [],
                environment_variables or {},
                machine_type,
                replica_count,
                accelerator_type,
                accelerator_count
            )
            
            logger.info(f"Created training job: {job_name}")
            return job_name
            
        except Exception as e:
            logger.error(f"Failed to create training job {display_name}: {e}")
            raise VertexAIError(f"Training job creation failed: {e}")
    
    def _create_training_job_sync(
        self,
        display_name: str,
        container_image_uri: str,
        model_serving_container_image_uri: str,
        args: List[str],
        environment_variables: Dict[str, str],
        machine_type: str,
        replica_count: int,
        accelerator_type: Optional[str],
        accelerator_count: int
    ) -> str:
        """Synchronous training job creation implementation"""
        parent = f"projects/{self.project_id}/locations/{self.location}"
        
        # Configure machine spec
        machine_spec = {
            "machine_type": machine_type,
        }
        
        # Add accelerator if specified
        if accelerator_type and accelerator_count > 0:
            machine_spec["accelerator_type"] = accelerator_type
            machine_spec["accelerator_count"] = accelerator_count
        
        # Configure worker pool
        worker_pool_spec = {
            "machine_spec": machine_spec,
            "replica_count": replica_count,
            "container_spec": {
                "image_uri": container_image_uri,
                "args": args,
                "env": [{"name": k, "value": v} for k, v in environment_variables.items()]
            }
        }
        
        # Create training job configuration
        training_job = {
            "display_name": display_name,
            "training_task_definition": "gs://google-cloud-aiplatform/schema/trainingjob/definition/custom_task_1.0.0.yaml",
            "training_task_inputs": {
                "worker_pool_specs": [worker_pool_spec],
                "base_output_directory": {
                    "output_uri_prefix": f"gs://{self.staging_bucket}/training_outputs"
                }
            },
            "model_to_upload": {
                "display_name": f"{display_name}-model",
                "container_spec": {
                    "image_uri": model_serving_container_image_uri,
                    "predict_route": "/predict",
                    "health_route": "/health"
                }
            }
        }
        
        # Create the training job
        response = self._job_client.create_custom_job(
            parent=parent,
            custom_job=training_job
        )
        
        return response.name
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def deploy_model(
        self,
        model_resource_name: str,
        endpoint_display_name: str,
        deployed_model_display_name: str = None,
        machine_type: str = "n1-standard-2",
        min_replica_count: int = 1,
        max_replica_count: int = 3,
        accelerator_type: str = None,
        accelerator_count: int = 0
    ) -> Dict[str, str]:
        """
        Deploy a model to an endpoint for online predictions.
        
        Args:
            model_resource_name: Resource name of the model to deploy
            endpoint_display_name: Display name for the endpoint
            deployed_model_display_name: Display name for the deployed model
            machine_type: Machine type for serving (default: n1-standard-2)
            min_replica_count: Minimum number of serving replicas (default: 1)
            max_replica_count: Maximum number of serving replicas (default: 3)
            accelerator_type: Type of accelerator for serving
            accelerator_count: Number of accelerators for serving
            
        Returns:
            Dictionary with endpoint and deployed model information
            
        Raises:
            VertexAIError: If model deployment fails
        """
        if not self.is_available:
            raise VertexAIError("Vertex AI client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            deployment_info = await loop.run_in_executor(
                self._executor,
                self._deploy_model_sync,
                model_resource_name,
                endpoint_display_name,
                deployed_model_display_name or f"{endpoint_display_name}-deployment",
                machine_type,
                min_replica_count,
                max_replica_count,
                accelerator_type,
                accelerator_count
            )
            
            logger.info(f"Deployed model to endpoint: {deployment_info['endpoint_name']}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Failed to deploy model {model_resource_name}: {e}")
            raise VertexAIError(f"Model deployment failed: {e}")
    
    def _deploy_model_sync(
        self,
        model_resource_name: str,
        endpoint_display_name: str,
        deployed_model_display_name: str,
        machine_type: str,
        min_replica_count: int,
        max_replica_count: int,
        accelerator_type: Optional[str],
        accelerator_count: int
    ) -> Dict[str, str]:
        """Synchronous model deployment implementation"""
        parent = f"projects/{self.project_id}/locations/{self.location}"
        
        # Create endpoint if it doesn't exist
        endpoint = {
            "display_name": endpoint_display_name
        }
        
        try:
            endpoint_response = self._endpoint_client.create_endpoint(
                parent=parent,
                endpoint=endpoint
            )
            endpoint_name = endpoint_response.result().name
        except gcp_exceptions.AlreadyExists:
            # Find existing endpoint
            endpoints = self._endpoint_client.list_endpoints(parent=parent)
            endpoint_name = None
            for ep in endpoints:
                if ep.display_name == endpoint_display_name:
                    endpoint_name = ep.name
                    break
            
            if not endpoint_name:
                raise VertexAIError(f"Endpoint {endpoint_display_name} not found")
        
        # Configure deployed model
        machine_spec = {
            "machine_type": machine_type
        }
        
        if accelerator_type and accelerator_count > 0:
            machine_spec["accelerator_type"] = accelerator_type
            machine_spec["accelerator_count"] = accelerator_count
        
        deployed_model = {
            "display_name": deployed_model_display_name,
            "model": model_resource_name,
            "dedicated_resources": {
                "machine_spec": machine_spec,
                "min_replica_count": min_replica_count,
                "max_replica_count": max_replica_count
            }
        }
        
        # Deploy model to endpoint
        deploy_response = self._endpoint_client.deploy_model(
            endpoint=endpoint_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100}  # Send 100% traffic to this model
        )
        
        deploy_response.result()  # Wait for deployment to complete
        
        return {
            "endpoint_name": endpoint_name,
            "deployed_model_name": deployed_model_display_name,
            "model_resource_name": model_resource_name
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def predict_online(
        self,
        endpoint_name: str,
        instances: List[Dict[str, Any]],
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make online predictions using a deployed model.
        
        Args:
            endpoint_name: Name of the endpoint to use for prediction
            instances: List of input instances for prediction
            parameters: Optional prediction parameters
            
        Returns:
            Prediction response containing predictions and metadata
            
        Raises:
            VertexAIError: If prediction fails
        """
        if not self.is_available:
            raise VertexAIError("Vertex AI client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            prediction_response = await loop.run_in_executor(
                self._executor,
                self._predict_online_sync,
                endpoint_name,
                instances,
                parameters or {}
            )
            
            logger.info(f"Made online prediction with {len(instances)} instances")
            return prediction_response
            
        except Exception as e:
            logger.error(f"Failed to make online prediction: {e}")
            raise VertexAIError(f"Online prediction failed: {e}")
    
    def _predict_online_sync(
        self,
        endpoint_name: str,
        instances: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synchronous online prediction implementation"""
        response = self._prediction_client.predict(
            endpoint=endpoint_name,
            instances=instances,
            parameters=parameters
        )
        
        return {
            "predictions": list(response.predictions),
            "deployed_model_id": response.deployed_model_id,
            "model_version_id": getattr(response, 'model_version_id', None),
            "model_display_name": getattr(response, 'model_display_name', None)
        }
    
    async def list_training_jobs(self, filter_expression: str = None) -> List[Dict[str, Any]]:
        """
        List training jobs in the project.
        
        Args:
            filter_expression: Optional filter expression
            
        Returns:
            List of training job information
            
        Raises:
            VertexAIError: If listing fails
        """
        if not self.is_available:
            raise VertexAIError("Vertex AI client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            jobs = await loop.run_in_executor(
                self._executor,
                self._list_training_jobs_sync,
                filter_expression
            )
            
            logger.info(f"Found {len(jobs)} training jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to list training jobs: {e}")
            raise VertexAIError(f"Training job listing failed: {e}")
    
    def _list_training_jobs_sync(self, filter_expression: Optional[str]) -> List[Dict[str, Any]]:
        """Synchronous training job listing implementation"""
        parent = f"projects/{self.project_id}/locations/{self.location}"
        
        jobs = []
        for job in self._job_client.list_custom_jobs(
            parent=parent,
            filter=filter_expression
        ):
            jobs.append({
                "name": job.name,
                "display_name": job.display_name,
                "state": job.state.name,
                "create_time": job.create_time,
                "start_time": job.start_time,
                "end_time": job.end_time,
                "error": str(job.error) if job.error else None
            })
        
        return jobs
    
    async def list_models(self, filter_expression: str = None) -> List[Dict[str, Any]]:
        """
        List models in the project.
        
        Args:
            filter_expression: Optional filter expression
            
        Returns:
            List of model information
            
        Raises:
            VertexAIError: If listing fails
        """
        if not self.is_available:
            raise VertexAIError("Vertex AI client is not available")
        
        try:
            loop = asyncio.get_event_loop()
            models = await loop.run_in_executor(
                self._executor,
                self._list_models_sync,
                filter_expression
            )
            
            logger.info(f"Found {len(models)} models")
            return models
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise VertexAIError(f"Model listing failed: {e}")
    
    def _list_models_sync(self, filter_expression: Optional[str]) -> List[Dict[str, Any]]:
        """Synchronous model listing implementation"""
        parent = f"projects/{self.project_id}/locations/{self.location}"
        
        models = []
        for model in self._model_client.list_models(
            parent=parent,
            filter=filter_expression
        ):
            models.append({
                "name": model.name,
                "display_name": model.display_name,
                "description": model.description,
                "create_time": model.create_time,
                "update_time": model.update_time,
                "training_pipeline": getattr(model, 'training_pipeline', None),
                "artifact_uri": getattr(model, 'artifact_uri', None)
            })
        
        return models
    
    async def close(self) -> None:
        """Close the Vertex AI clients and cleanup resources"""
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("Vertex AI client resources cleaned up")


# Factory function for easy initialization
def create_vertex_ai_client(settings) -> VertexAIClient:
    """
    Factory function to create a Vertex AI client.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured VertexAIClient instance
    """
    return VertexAIClient(settings)