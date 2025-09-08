"""
Google Cloud Pub/Sub Client

This module provides an async-compatible interface for Google Cloud Pub/Sub operations
including topic management, message publishing, and subscription handling for the HTX trading platform.
"""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import PubsubMessage
from google.auth.exceptions import DefaultCredentialsError
from google.api_core import exceptions as gcp_exceptions
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class PubSubClientError(Exception):
    """Custom exception for Pub/Sub Client errors"""
    pass


class PubSubClient:
    """
    Async-compatible Google Cloud Pub/Sub client for the HTX trading platform.
    
    Provides methods for:
    - Creating and managing topics
    - Publishing messages with retry logic
    - Creating and managing subscriptions
    - Async message consumption with callbacks
    """
    
    def __init__(self, settings):
        """
        Initialize the Pub/Sub Client with configuration settings.
        
        Args:
            settings: Application settings containing GCP configuration
        """
        self.settings = settings
        self.project_id = settings.GCP_PROJECT_ID
        self._publisher: Optional[pubsub_v1.PublisherClient] = None
        self._subscriber: Optional[pubsub_v1.SubscriberClient] = None
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize clients if credentials are available
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initialize the Google Cloud Pub/Sub clients"""
        try:
            if self.settings.GOOGLE_APPLICATION_CREDENTIALS:
                # Use service account credentials
                self._publisher = pubsub_v1.PublisherClient.from_service_account_json(
                    self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
                self._subscriber = pubsub_v1.SubscriberClient.from_service_account_json(
                    self.settings.GOOGLE_APPLICATION_CREDENTIALS
                )
            else:
                # Use default credentials
                self._publisher = pubsub_v1.PublisherClient()
                self._subscriber = pubsub_v1.SubscriberClient()
            
            logger.info("Initialized Pub/Sub clients successfully")
            
        except DefaultCredentialsError:
            logger.warning("GCP credentials not found. Pub/Sub client will be disabled.")
            self._publisher = None
            self._subscriber = None
        except Exception as e:
            logger.error(f"Failed to initialize Pub/Sub clients: {e}")
            raise PubSubClientError(f"Failed to initialize Pub/Sub clients: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if the Pub/Sub clients are properly configured and available"""
        return self._publisher is not None and self._subscriber is not None
    
    def _get_topic_path(self, topic_name: str) -> str:
        """Get the full topic path"""
        return self._publisher.topic_path(self.project_id, topic_name)
    
    def _get_subscription_path(self, subscription_name: str) -> str:
        """Get the full subscription path"""
        return self._subscriber.subscription_path(self.project_id, subscription_name)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_topic(self, topic_name: str) -> str:
        """
        Create a Pub/Sub topic if it doesn't exist.
        
        Args:
            topic_name: Name of the topic to create
            
        Returns:
            The full topic path
            
        Raises:
            PubSubClientError: If topic creation fails
        """
        if not self.is_available:
            raise PubSubClientError("Pub/Sub client is not available")
        
        try:
            topic_path = self._get_topic_path(topic_name)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self._create_topic_sync,
                topic_path
            )
            
            logger.info(f"Created/verified topic: {topic_path}")
            return topic_path
            
        except Exception as e:
            logger.error(f"Failed to create topic {topic_name}: {e}")
            raise PubSubClientError(f"Topic creation failed: {e}")
    
    def _create_topic_sync(self, topic_path: str) -> None:
        """Synchronous topic creation implementation"""
        try:
            self._publisher.create_topic(request={"name": topic_path})
        except gcp_exceptions.AlreadyExists:
            # Topic already exists, which is fine
            pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def publish_message(
        self,
        topic_name: str,
        data: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Publish a message to a Pub/Sub topic.
        
        Args:
            topic_name: Name of the topic to publish to
            data: Message data (will be JSON serialized)
            attributes: Optional message attributes
            
        Returns:
            Message ID of the published message
            
        Raises:
            PubSubClientError: If publishing fails
        """
        if not self.is_available:
            raise PubSubClientError("Pub/Sub client is not available")
        
        try:
            # Ensure topic exists
            topic_path = await self.create_topic(topic_name)
            
            # Prepare message
            message_data = json.dumps(data, default=str).encode('utf-8')
            message_attributes = attributes or {}
            
            # Add timestamp
            message_attributes['timestamp'] = datetime.utcnow().isoformat()
            message_attributes['source'] = 'htx-trading-platform'
            
            # Publish message
            loop = asyncio.get_event_loop()
            future = await loop.run_in_executor(
                self._executor,
                self._publish_message_sync,
                topic_path,
                message_data,
                message_attributes
            )
            
            message_id = future.result()
            logger.info(f"Published message {message_id} to topic {topic_name}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish message to {topic_name}: {e}")
            raise PubSubClientError(f"Message publishing failed: {e}")
    
    def _publish_message_sync(
        self,
        topic_path: str,
        data: bytes,
        attributes: Dict[str, str]
    ):
        """Synchronous message publishing implementation"""
        return self._publisher.publish(topic_path, data, **attributes)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_subscription(
        self,
        topic_name: str,
        subscription_name: str,
        ack_deadline_seconds: int = 600
    ) -> str:
        """
        Create a subscription to a Pub/Sub topic.
        
        Args:
            topic_name: Name of the topic to subscribe to
            subscription_name: Name of the subscription to create
            ack_deadline_seconds: Acknowledgment deadline in seconds
            
        Returns:
            The full subscription path
            
        Raises:
            PubSubClientError: If subscription creation fails
        """
        if not self.is_available:
            raise PubSubClientError("Pub/Sub client is not available")
        
        try:
            # Ensure topic exists
            topic_path = await self.create_topic(topic_name)
            subscription_path = self._get_subscription_path(subscription_name)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self._create_subscription_sync,
                subscription_path,
                topic_path,
                ack_deadline_seconds
            )
            
            logger.info(f"Created/verified subscription: {subscription_path}")
            return subscription_path
            
        except Exception as e:
            logger.error(f"Failed to create subscription {subscription_name}: {e}")
            raise PubSubClientError(f"Subscription creation failed: {e}")
    
    def _create_subscription_sync(
        self,
        subscription_path: str,
        topic_path: str,
        ack_deadline_seconds: int
    ) -> None:
        """Synchronous subscription creation implementation"""
        try:
            self._subscriber.create_subscription(
                request={
                    "name": subscription_path,
                    "topic": topic_path,
                    "ack_deadline_seconds": ack_deadline_seconds
                }
            )
        except gcp_exceptions.AlreadyExists:
            # Subscription already exists, which is fine
            pass
    
    async def subscribe_to_topic(
        self,
        topic_name: str,
        subscription_name: str,
        callback: Callable[[Dict[str, Any]], None],
        max_messages: int = 10
    ) -> None:
        """
        Subscribe to a topic and process messages with a callback.
        
        Args:
            topic_name: Name of the topic to subscribe to
            subscription_name: Name of the subscription
            callback: Function to call for each message
            max_messages: Maximum number of messages to process concurrently
            
        Raises:
            PubSubClientError: If subscription fails
        """
        if not self.is_available:
            raise PubSubClientError("Pub/Sub client is not available")
        
        try:
            # Create subscription if it doesn't exist
            subscription_path = await self.create_subscription(topic_name, subscription_name)
            
            # Define message handler
            def message_handler(message: PubsubMessage):
                try:
                    # Parse message data
                    data = json.loads(message.data.decode('utf-8'))
                    
                    # Add metadata
                    data['_message_id'] = message.message_id
                    data['_publish_time'] = message.publish_time
                    data['_attributes'] = dict(message.attributes)
                    
                    # Call user callback
                    callback(data)
                    
                    # Acknowledge message
                    message.ack()
                    
                except Exception as e:
                    logger.error(f"Error processing message {message.message_id}: {e}")
                    message.nack()
            
            # Configure flow control
            flow_control = pubsub_v1.types.FlowControl(max_messages=max_messages)
            
            # Start pulling messages
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self._start_subscription_sync,
                subscription_path,
                message_handler,
                flow_control
            )
            
        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic_name}: {e}")
            raise PubSubClientError(f"Subscription failed: {e}")
    
    def _start_subscription_sync(
        self,
        subscription_path: str,
        callback: Callable,
        flow_control
    ) -> None:
        """Synchronous subscription implementation"""
        # This is a blocking call that will run in the executor
        self._subscriber.subscribe(
            subscription_path,
            callback=callback,
            flow_control=flow_control
        )
    
    async def list_topics(self) -> List[str]:
        """
        List all topics in the project.
        
        Returns:
            List of topic names
            
        Raises:
            PubSubClientError: If listing fails
        """
        if not self.is_available:
            raise PubSubClientError("Pub/Sub client is not available")
        
        try:
            project_path = f"projects/{self.project_id}"
            
            loop = asyncio.get_event_loop()
            topics = await loop.run_in_executor(
                self._executor,
                self._list_topics_sync,
                project_path
            )
            
            # Extract topic names from full paths
            topic_names = [
                topic.name.split('/')[-1] 
                for topic in topics
            ]
            
            logger.info(f"Found {len(topic_names)} topics")
            return topic_names
            
        except Exception as e:
            logger.error(f"Failed to list topics: {e}")
            raise PubSubClientError(f"Topic listing failed: {e}")
    
    def _list_topics_sync(self, project_path: str):
        """Synchronous topic listing implementation"""
        return list(self._publisher.list_topics(request={"project": project_path}))
    
    async def delete_subscription(self, subscription_name: str) -> bool:
        """
        Delete a subscription.
        
        Args:
            subscription_name: Name of the subscription to delete
            
        Returns:
            True if deletion successful, False otherwise
            
        Raises:
            PubSubClientError: If deletion fails
        """
        if not self.is_available:
            raise PubSubClientError("Pub/Sub client is not available")
        
        try:
            subscription_path = self._get_subscription_path(subscription_name)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self._subscriber.delete_subscription,
                request={"subscription": subscription_path}
            )
            
            logger.info(f"Deleted subscription: {subscription_path}")
            return True
            
        except gcp_exceptions.NotFound:
            logger.warning(f"Subscription {subscription_name} not found")
            return False
        except Exception as e:
            logger.error(f"Failed to delete subscription {subscription_name}: {e}")
            raise PubSubClientError(f"Subscription deletion failed: {e}")
    
    async def close(self) -> None:
        """Close the Pub/Sub clients and cleanup resources"""
        if self._executor:
            self._executor.shutdown(wait=True)
            logger.info("Pub/Sub client resources cleaned up")


# Factory function for easy initialization
def create_pubsub_client(settings) -> PubSubClient:
    """
    Factory function to create a Pub/Sub client.
    
    Args:
        settings: Application settings
        
    Returns:
        Configured PubSubClient instance
    """
    return PubSubClient(settings)