"""
WebSocket service for real-time notifications
Phase 2.3: Live updates for trading data
"""

import json
import logging
import asyncio
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from app.services.cache import cache

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for topic, subscribers in self.subscriptions.items():
            subscribers.discard(websocket)
        
        logger.info(f"WebSocket disconnected. Remaining: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def subscribe(self, websocket: WebSocket, topic: str):
        """Subscribe connection to specific topic"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        
        self.subscriptions[topic].add(websocket)
        logger.info(f"Subscribed to topic '{topic}'. Subscribers: {len(self.subscriptions[topic])}")
    
    async def unsubscribe(self, websocket: WebSocket, topic: str):
        """Unsubscribe connection from topic"""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(websocket)
    
    async def broadcast_to_topic(self, topic: str, message: dict):
        """Broadcast message to specific topic subscribers"""
        if topic not in self.subscriptions:
            return
        
        subscribers = list(self.subscriptions[topic])  # Copy to avoid modification during iteration
        if not subscribers:
            return
        
        message_data = {
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
            **message
        }
        message_str = json.dumps(message_data)
        disconnected = []
        
        for connection in subscribers:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send to subscriber: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
        
        logger.debug(f"Broadcasted to topic '{topic}': {len(subscribers) - len(disconnected)} recipients")


class NotificationService:
    """Service for sending real-time notifications"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
    
    async def notify_trade_update(self, trade_data: Dict[str, Any]):
        """Notify about new trade data"""
        await self.manager.broadcast_to_topic("trades", {
            "type": "trade_update",
            "data": trade_data
        })
    
    async def notify_pnl_update(self, pnl_data: Dict[str, Any]):
        """Notify about PnL changes"""
        await self.manager.broadcast_to_topic("pnl", {
            "type": "pnl_update", 
            "data": pnl_data
        })
    
    async def notify_balance_update(self, balance_data: Dict[str, Any]):
        """Notify about balance changes"""
        await self.manager.broadcast_to_topic("balance", {
            "type": "balance_update",
            "data": balance_data
        })
    
    async def notify_htx_sync(self, sync_status: str, details: Optional[Dict[str, Any]] = None):
        """Notify about HTX sync status"""
        await self.manager.broadcast_to_topic("htx_sync", {
            "type": "sync_status",
            "status": sync_status,
            "details": details or {}
        })
    
    async def notify_cache_update(self, cache_key: str, action: str):
        """Notify about cache updates"""
        await self.manager.broadcast_to_topic("cache", {
            "type": "cache_update",
            "cache_key": cache_key,
            "action": action  # "updated", "invalidated", "warmed"
        })
    
    async def notify_system_status(self, component: str, status: str, message: str = ""):
        """Notify about system component status"""
        await self.manager.broadcast({
            "type": "system_status",
            "component": component,
            "status": status,  # "healthy", "warning", "error"
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_welcome_message(self, websocket: WebSocket):
        """Send welcome message to new connection"""
        # Get quick stats for welcome
        try:
            # Try to get cached dashboard data
            dashboard = await cache.get("dashboard_snapshot")
            if dashboard:
                welcome_data = {
                    "type": "welcome",
                    "message": "Connected to HTX Project real-time updates",
                    "dashboard": dashboard,
                    "available_topics": [
                        "trades", "pnl", "balance", "htx_sync", "cache"
                    ]
                }
            else:
                welcome_data = {
                    "type": "welcome", 
                    "message": "Connected to HTX Project real-time updates",
                    "available_topics": [
                        "trades", "pnl", "balance", "htx_sync", "cache"
                    ]
                }
            
            await self.manager.send_personal_message(welcome_data, websocket)
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")


# Global instances
manager = ConnectionManager()
notification_service = NotificationService(manager)


async def handle_websocket_message(websocket: WebSocket, data: dict):
    """Handle incoming WebSocket messages"""
    try:
        message_type = data.get("type")
        
        if message_type == "subscribe":
            topic = data.get("topic")
            if topic:
                await manager.subscribe(websocket, topic)
                await manager.send_personal_message({
                    "type": "subscription_confirmed",
                    "topic": topic
                }, websocket)
        
        elif message_type == "unsubscribe":
            topic = data.get("topic") 
            if topic:
                await manager.unsubscribe(websocket, topic)
                await manager.send_personal_message({
                    "type": "unsubscription_confirmed",
                    "topic": topic
                }, websocket)
        
        elif message_type == "ping":
            await manager.send_personal_message({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }, websocket)
        
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }, websocket)
    
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": "Failed to process message"
        }, websocket)
