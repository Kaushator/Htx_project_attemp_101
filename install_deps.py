#!/usr/bin/env python3
"""
HTX Project - Cross-Platform Dependency Installer
Works on Windows, Linux, and WSL
"""

import subprocess
import sys
import os
from pathlib import Path
import venv

def run_command(cmd, shell=True):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 HTX Project - Cross-Platform Dependency Installer")
    print("=" * 55)
    
    project_root = Path(__file__).parent
    print(f"📂 Project root: {project_root}")
    
    # Check Python version
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return 1
    
    # Create virtual environment
    venv_dir = project_root / ".venv_wsl2"
    if not venv_dir.exists():
        print(f"📦 Creating virtual environment: {venv_dir}")
        venv.create(venv_dir, with_pip=True)
    else:
        print(f"📦 Using existing virtual environment: {venv_dir}")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = venv_dir / "Scripts" / "pip.exe"
        python_path = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux
        pip_path = venv_dir / "bin" / "pip"
        python_path = venv_dir / "bin" / "python"
    
    # Upgrade pip
    print("⬆️ Upgrading pip...")
    success, stdout, stderr = run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], shell=False)
    if not success:
        print(f"⚠️ Failed to upgrade pip: {stderr}")
    
    # Install requirements
    requirements_file = project_root / "backend" / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing requirements...")
        success, stdout, stderr = run_command([str(pip_path), "install", "-r", str(requirements_file)], shell=False)
        if not success:
            print(f"❌ Failed to install requirements: {stderr}")
            return 1
        print("✅ Requirements installed successfully")
    else:
        print(f"❌ Requirements file not found: {requirements_file}")
        return 1
    
    # Install dev requirements
    dev_requirements_file = project_root / "backend" / "requirements-dev.txt"
    if dev_requirements_file.exists():
        print("📦 Installing development requirements...")
        success, stdout, stderr = run_command([str(pip_path), "install", "-r", str(dev_requirements_file)], shell=False)
        if not success:
            print(f"⚠️ Failed to install dev requirements: {stderr}")
    
    # Verify imports
    print("🔍 Verifying imports...")
    critical_imports = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic", "pydantic_settings",
        "httpx", "pandas", "numpy"
    ]
    
    optional_imports = [
        "transformers", "torch", "openai"
    ]
    
    failed_critical = []
    failed_optional = []
    
    for module in critical_imports:
        success, _, _ = run_command([str(python_path), "-c", f"import {module}"], shell=False)
        if success:
            print(f"✅ {module}")
        else:
            print(f"❌ {module}")
            failed_critical.append(module)
    
    for module in optional_imports:
        success, _, _ = run_command([str(python_path), "-c", f"import {module}"], shell=False)
        if success:
            print(f"✅ {module} (optional)")
        else:
            print(f"⚠️ {module} (optional - ML features may be disabled)")
            failed_optional.append(module)
    
    if failed_critical:
        print(f"\n❌ Critical imports failed: {', '.join(failed_critical)}")
        return 1
    
    print("\n✅ Dependencies installed successfully!")
    print("\n🚀 To run the backend:")
    
    if os.name == 'nt':  # Windows
        print("   # Activate virtual environment first:")
        print(f"   {venv_dir}\\Scripts\\Activate.ps1")
        print("   # Then run backend:")
        print("   cd backend && python run.py")
    else:  # Unix/Linux
        print("   # Activate virtual environment first:")
        print(f"   source {venv_dir}/bin/activate")
        print("   # Then run backend:")
        print("   cd backend && python run.py")
    
    if failed_optional:
        print(f"\n⚠️ Optional ML features disabled due to missing: {', '.join(failed_optional)}")
        print("   Install these manually if you need ML features:")
        print("   pip install torch transformers openai")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())