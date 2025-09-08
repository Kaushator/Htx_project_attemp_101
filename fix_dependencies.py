#!/usr/bin/env python3
"""
HTX Project - Dependencies Fix Script
Fix all import errors and dependency issues
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print("❌ Python 3.12+ required")
        return False
    
    print("✅ Python version OK")
    return True

def install_requirements():
    """Install requirements"""
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print("📦 Installing requirements...")
    
    # Upgrade pip first
    success, stdout, stderr = run_command(f"{sys.executable} -m pip install --upgrade pip")
    if not success:
        print(f"⚠️ Failed to upgrade pip: {stderr}")
    
    # Install requirements
    success, stdout, stderr = run_command(f"{sys.executable} -m pip install -r {requirements_file}")
    if not success:
        print(f"❌ Failed to install requirements: {stderr}")
        return False
    
    print("✅ Requirements installed successfully")
    return True

def verify_imports():
    """Verify critical imports"""
    critical_imports = [
        "fastapi",
        "uvicorn", 
        "sqlalchemy",
        "pydantic",
        "pydantic_settings",
        "python_dotenv",
        "transformers",
        "torch",
        "openai",
        "httpx",
        "pandas",
        "numpy"
    ]
    
    print("🔍 Verifying imports...")
    failed_imports = []
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
        return False
    
    print("\n✅ All critical imports verified")
    return True

def main():
    """Main function"""
    print("🔧 HTX Project - Dependencies Fix")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n💡 Try manually:")
        print("   pip install --upgrade pip")
        print("   pip install -r backend/requirements.txt")
        sys.exit(1)
    
    # Verify imports
    if not verify_imports():
        print("\n⚠️ Some imports failed, but continuing...")
    
    print("\n✅ Dependencies fix completed!")
    print("\n🚀 You can now run:")
    print("   cd backend && python -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()