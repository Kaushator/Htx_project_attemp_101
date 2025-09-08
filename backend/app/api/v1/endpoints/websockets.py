"""
WebSocket endpoints for real-time updates
Phase 2.3: Live notifications
"""

import json
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket import manager, notification_service, handle_websocket_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time updates
    
    Available topics for subscription:
    - trades: Trade updates and new trades
    - pnl: PnL calculation updates
    - balance: Account balance changes
    - htx_sync: HTX synchronization status
    - cache: Cache warming and invalidation
    
    Message format:
    {
        "type": "subscribe|unsubscribe|ping",
        "topic": "trades|pnl|balance|htx_sync|cache"
    }
    """
    await manager.connect(websocket)
    
    # Send welcome message
    await notification_service.send_welcome_message(websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Failed to process message"
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/live/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """
    Dedicated WebSocket for dashboard updates
    Automatically subscribes to key dashboard metrics
    """
    await manager.connect(websocket)
    
    # Auto-subscribe to dashboard-relevant topics
    await manager.subscribe(websocket, "trades")
    await manager.subscribe(websocket, "pnl")
    await manager.subscribe(websocket, "balance")
    
    # Send welcome with subscription info
    await manager.send_personal_message({
        "type": "dashboard_connected",
        "message": "Connected to dashboard live updates",
        "auto_subscriptions": ["trades", "pnl", "balance"]
    }, websocket)
    
    try:
        while True:
            # Keep connection alive, handle ping/pong
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
            except:
                pass  # Ignore malformed messages on dashboard channel
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")
        manager.disconnect(websocket)
