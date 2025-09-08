#!/usr/bin/env python3
"""
WebSocket Test Client
Test WebSocket real-time notifications
"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_websocket_connection():
    """Test WebSocket connection and messaging"""
    uri = "ws://127.0.0.1:8004/ws/live"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            
            # Wait for welcome message
            welcome = await websocket.recv()
            logger.info(f"Welcome: {welcome}")
            
            # Subscribe to trades topic
            subscribe_msg = {
                "type": "subscribe",
                "topic": "trades"
            }
            await websocket.send(json.dumps(subscribe_msg))
            logger.info("Sent subscription to trades")
            
            # Wait for confirmation
            confirmation = await websocket.recv()
            logger.info(f"Subscription response: {confirmation}")
            
            # Subscribe to PnL topic
            subscribe_pnl = {
                "type": "subscribe", 
                "topic": "pnl"
            }
            await websocket.send(json.dumps(subscribe_pnl))
            logger.info("Sent subscription to pnl")
            
            pnl_confirmation = await websocket.recv()
            logger.info(f"PnL subscription response: {pnl_confirmation}")
            
            # Send ping
            ping_msg = {
                "type": "ping"
            }
            await websocket.send(json.dumps(ping_msg))
            logger.info("Sent ping")
            
            pong = await websocket.recv()
            logger.info(f"Pong response: {pong}")
            
            # Listen for messages for 30 seconds
            logger.info("Listening for messages...")
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    logger.info(f"Received: {data.get('type', 'unknown')} - {message[:100]}...")
            except asyncio.TimeoutError:
                logger.info("Timeout reached, closing connection")
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


async def test_dashboard_websocket():
    """Test dedicated dashboard WebSocket"""
    uri = "ws://127.0.0.1:8004/ws/live/dashboard"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to dashboard WebSocket: {uri}")
            
            # Wait for welcome message
            welcome = await websocket.recv()
            logger.info(f"Dashboard welcome: {welcome}")
            
            # Send ping
            ping_msg = {
                "type": "ping"
            }
            await websocket.send(json.dumps(ping_msg))
            logger.info("Sent ping to dashboard")
            
            pong = await websocket.recv()
            logger.info(f"Dashboard pong: {pong}")
            
            # Listen for dashboard updates
            logger.info("Listening for dashboard updates...")
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=20.0)
                    data = json.loads(message)
                    logger.info(f"Dashboard update: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                logger.info("Dashboard timeout, closing")
                
    except Exception as e:
        logger.error(f"Dashboard WebSocket error: {e}")


async def main():
    """Run WebSocket tests"""
    logger.info("Starting WebSocket tests...")
    
    # Test main WebSocket endpoint
    logger.info("\n=== Testing main WebSocket endpoint ===")
    await test_websocket_connection()
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Test dashboard WebSocket
    logger.info("\n=== Testing dashboard WebSocket endpoint ===")
    await test_dashboard_websocket()
    
    logger.info("WebSocket tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
