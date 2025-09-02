#!/usr/bin/env python3
"""
Simple Backend Runner
Alternative approach using environment variables
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the backend directory
    backend_dir = Path(__file__).parent / "backend"
    
    # Set PYTHONPATH to include backend directory
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir)
    
    print("🚀 Starting HTX Trading Platform Backend...")
    print(f"📂 Backend directory: {backend_dir}")
    print(f"🐍 Python path: {env.get('PYTHONPATH', 'default')}")
    
    # Change to backend directory and run
    os.chdir(backend_dir)
    
    try:
        # Try to run with uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        print(f"🎯 Running command: {' '.join(cmd)}")
        subprocess.run(cmd, env=env, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        print("\n💡 Try installing dependencies first:")
        print("   bash quick_fix_deps.sh")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())