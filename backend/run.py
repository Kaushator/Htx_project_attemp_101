#!/usr/bin/env python3
"""
HTX Project - Application Runner
Proper entry point that sets up Python path and runs the FastAPI application
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import and run the application
if __name__ == "__main__":
    from app.main import app
    import uvicorn
    from app.core.config import settings
    
    print(f"🚀 Starting HTX Trading Platform")
    print(f"📂 Backend directory: {current_dir}")
    print(f"🌐 Server will run on: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )