#!/usr/bin/env python3
"""
HTX Project Personal Activation Setup
Master script for one-time setup and configuration on personal PC

This script handles:
- GCP project setup and authentication
- Google Secret Manager configuration
- API key storage and validation
- Environment setup and dependency installation
- Service validation and testing
"""

import os
import sys
import json
import getpass
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('activation_setup.log')
    ]
)
logger = logging.getLogger(__name__)

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class HTXProjectActivator:
    """Main activation class for HTX Project setup"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.config = {}
        self.secrets_manager = None
        
    def print_header(self):
        """Print welcome header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔" + "═" * 60 + "╗")
        print("║" + " " * 20 + "HTX PROJECT SETUP" + " " * 21 + "║")
        print("║" + " " * 15 + "Personal PC Activation" + " " * 16 + "║")
        print("╚" + "═" * 60 + "╝")
        print(f"{Colors.ENDC}")
        
        print(f"{Colors.OKBLUE}Welcome to HTX Trading Platform Setup!{Colors.ENDC}")
        print("This wizard will configure your personal trading analytics system.\n")
        
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        print(f"{Colors.OKCYAN}🔍 Checking Prerequisites...{Colors.ENDC}")
        
        prerequisites = {
            "Python 3.12+": self._check_python_version(),
            "WSL2/Linux Environment": self._check_wsl_environment(),
            "Git": self._check_git(),
            "Node.js": self._check_nodejs(),
            "Docker": self._check_docker()
        }
        
        all_good = True
        for name, status in prerequisites.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {name}")
            if not status:
                all_good = False
        
        if not all_good:
            print(f"\n{Colors.WARNING}⚠️  Some prerequisites are missing. Please install them first.{Colors.ENDC}")
            return False
        
        print(f"\n{Colors.OKGREEN}✅ All prerequisites satisfied!{Colors.ENDC}")
        return True
    
    def _check_python_version(self) -> bool:
        """Check Python version"""
        return sys.version_info >= (3, 12)
    
    def _check_wsl_environment(self) -> bool:
        """Check if running in WSL2 or Linux"""
        return os.name == 'posix' or 'WSL' in os.environ.get('WSL_DISTRO_NAME', '')
    
    def _check_git(self) -> bool:
        """Check if git is available"""
        return shutil.which('git') is not None
    
    def _check_nodejs(self) -> bool:
        """Check if Node.js is available"""
        return shutil.which('node') is not None
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        return shutil.which('docker') is not None
    
    def setup_gcp_project(self) -> bool:
        """Set up Google Cloud Project"""
        print(f"\n{Colors.OKCYAN}☁️  Google Cloud Platform Setup{Colors.ENDC}")
        
        # Get GCP Project ID
        project_id = input("Enter your GCP Project ID: ").strip()
        if not project_id:
            print(f"{Colors.FAIL}❌ Project ID is required{Colors.ENDC}")
            return False
        
        self.config['gcp_project_id'] = project_id
        
        # Check for service account key
        print(f"\n{Colors.OKBLUE}🔑 Service Account Setup{Colors.ENDC}")
        print("You need a GCP Service Account JSON key file.")
        
        key_file_path = input("Enter path to service account JSON file: ").strip()
        if not key_file_path or not Path(key_file_path).exists():
            print(f"{Colors.FAIL}❌ Service account key file not found{Colors.ENDC}")
            return False
        
        # Copy service account key to project
        target_key_path = self.project_root / "gcp-service-account.json"
        shutil.copy2(key_file_path, target_key_path)
        
        # Set environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(target_key_path)
        self.config['google_credentials_path'] = str(target_key_path)
        
        print(f"{Colors.OKGREEN}✅ GCP Project configured: {project_id}{Colors.ENDC}")
        return True
    
    def collect_api_keys(self) -> Dict[str, str]:
        """Collect API keys from user"""
        print(f"\n{Colors.OKCYAN}🔐 API Keys Collection{Colors.ENDC}")
        print("Please provide your API keys. These will be securely stored in Google Secret Manager.\n")
        
        api_keys = {}
        
        # HTX API Keys
        print(f"{Colors.OKBLUE}HTX Exchange API Keys:{Colors.ENDC}")
        htx_key = getpass.getpass("HTX API Key: ").strip()
        htx_secret = getpass.getpass("HTX API Secret: ").strip()
        htx_subuid = input("HTX Sub-account UID (optional): ").strip()
        
        if htx_key and htx_secret:
            api_keys['HTX_API_KEY'] = htx_key
            api_keys['HTX_API_SECRET'] = htx_secret
            if htx_subuid:
                api_keys['HTX_SUBUID'] = htx_subuid
        
        # OpenAI API Key
        print(f"\n{Colors.OKBLUE}OpenAI API Key (for ML analytics):{Colors.ENDC}")
        openai_key = getpass.getpass("OpenAI API Key (optional): ").strip()
        if openai_key:
            api_keys['OPENAI_API_KEY'] = openai_key
        
        # 3Commas API Keys
        print(f"\n{Colors.OKBLUE}3Commas API Keys (optional):{Colors.ENDC}")
        threecommas_key = getpass.getpass("3Commas API Key: ").strip()
        threecommas_secret = getpass.getpass("3Commas API Secret: ").strip()
        
        if threecommas_key and threecommas_secret:
            api_keys['THREECOMMAS_API_KEY'] = threecommas_key
            api_keys['THREECOMMAS_API_SECRET'] = threecommas_secret
        
        # Generate encryption key
        from cryptography.fernet import Fernet
        api_keys['ENCRYPTION_KEY'] = Fernet.generate_key().decode()
        
        return api_keys
    
    def setup_secret_manager(self, api_keys: Dict[str, str]) -> bool:
        """Set up Google Secret Manager with API keys"""
        print(f"\n{Colors.OKCYAN}🔒 Setting up Google Secret Manager{Colors.ENDC}")
        
        try:
            # Import the secrets manager
            sys.path.insert(0, str(self.backend_dir))
            from app.services.secret_manager import HTXSecretsManager
            
            self.secrets_manager = HTXSecretsManager(self.config['gcp_project_id'])
            
            # Create secrets
            print("Creating secrets...")
            setup_results = self.secrets_manager.setup_all_secrets()
            
            success_count = sum(setup_results.values())
            total_count = len(setup_results)
            
            print(f"Created {success_count}/{total_count} secrets")
            
            # Store API keys
            print("Storing API keys...")
            store_results = self.secrets_manager.store_api_keys(api_keys)
            
            stored_count = sum(store_results.values())
            print(f"Stored {stored_count}/{len(api_keys)} API keys")
            
            if stored_count > 0:
                print(f"{Colors.OKGREEN}✅ Secret Manager configured successfully{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.FAIL}❌ Failed to store API keys{Colors.ENDC}")
                return False
            
        except Exception as e:
            logger.error(f"Secret Manager setup failed: {e}")
            print(f"{Colors.FAIL}❌ Secret Manager setup failed: {e}{Colors.ENDC}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install project dependencies"""
        print(f"\n{Colors.OKCYAN}📦 Installing Dependencies{Colors.ENDC}")
        
        try:
            # Backend dependencies
            print("Installing backend dependencies...")
            backend_result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], cwd=self.backend_dir, capture_output=True, text=True)
            
            if backend_result.returncode != 0:
                print(f"{Colors.FAIL}❌ Backend dependency installation failed{Colors.ENDC}")
                print(backend_result.stderr)
                return False
            
            # Frontend dependencies
            print("Installing frontend dependencies...")
            frontend_dir = self.project_root / "frontend"
            frontend_result = subprocess.run([
                "npm", "install"
            ], cwd=frontend_dir, capture_output=True, text=True)
            
            if frontend_result.returncode != 0:
                print(f"{Colors.WARNING}⚠️  Frontend dependency installation failed{Colors.ENDC}")
                print(frontend_result.stderr)
            
            print(f"{Colors.OKGREEN}✅ Dependencies installed{Colors.ENDC}")
            return True
            
        except Exception as e:
            logger.error(f"Dependency installation failed: {e}")
            print(f"{Colors.FAIL}❌ Dependency installation failed: {e}{Colors.ENDC}")
            return False
    
    def generate_configuration(self) -> bool:
        """Generate environment configuration"""
        print(f"\n{Colors.OKCYAN}⚙️  Generating Configuration{Colors.ENDC}")
        
        try:
            if self.secrets_manager:
                # Generate .env from Secret Manager
                env_path = self.project_root / ".env"
                success = self.secrets_manager.generate_env_file(str(env_path))
                
                if success:
                    print(f"✅ Generated .env file: {env_path}")
                else:
                    print(f"❌ Failed to generate .env file")
                    return False
            
            # Generate startup scripts
            self._generate_startup_scripts()
            
            print(f"{Colors.OKGREEN}✅ Configuration generated{Colors.ENDC}")
            return True
            
        except Exception as e:
            logger.error(f"Configuration generation failed: {e}")
            print(f"{Colors.FAIL}❌ Configuration generation failed: {e}{Colors.ENDC}")
            return False
    
    def _generate_startup_scripts(self):
        """Generate convenient startup scripts"""
        # Backend startup script
        backend_script = self.project_root / "start_backend_personal.sh"
        backend_content = f"""#!/bin/bash
# HTX Project Backend Startup Script (Personal PC)
cd "{self.backend_dir}"
export PYTHONPATH="{self.backend_dir}:$PYTHONPATH"
export GOOGLE_APPLICATION_CREDENTIALS="{self.config.get('google_credentials_path', '')}"

echo "Starting HTX Trading Platform Backend..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
"""
        
        with open(backend_script, 'w') as f:
            f.write(backend_content)
        backend_script.chmod(0o755)
        
        # Frontend startup script
        frontend_script = self.project_root / "start_frontend_personal.sh"
        frontend_content = f"""#!/bin/bash
# HTX Project Frontend Startup Script (Personal PC)
cd "{self.project_root}/frontend"

echo "Starting HTX Trading Platform Frontend..."
npm run dev
"""
        
        with open(frontend_script, 'w') as f:
            f.write(frontend_content)
        frontend_script.chmod(0o755)
        
        # Combined startup script
        combined_script = self.project_root / "start_htx_personal.sh"
        combined_content = f"""#!/bin/bash
# HTX Project Complete Startup Script (Personal PC)
echo "🚀 Starting HTX Trading Platform..."

# Start backend in background
echo "📡 Starting backend..."
{backend_script} &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend in background
echo "🌐 Starting frontend..."
{frontend_script} &
FRONTEND_PID=$!

echo "✅ HTX Trading Platform is starting up!"
echo "Backend: http://localhost:8004"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8004/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
"""
        
        with open(combined_script, 'w') as f:
            f.write(combined_content)
        combined_script.chmod(0o755)
    
    def validate_setup(self) -> bool:
        """Validate the complete setup"""
        print(f"\n{Colors.OKCYAN}🔍 Validating Setup{Colors.ENDC}")
        
        validation_results = []
        
        # Check environment file
        env_file = self.project_root / ".env"
        if env_file.exists():
            validation_results.append(("Environment file", True))
        else:
            validation_results.append(("Environment file", False))
        
        # Check GCP credentials
        creds_file = Path(self.config.get('google_credentials_path', ''))
        if creds_file.exists():
            validation_results.append(("GCP credentials", True))
        else:
            validation_results.append(("GCP credentials", False))
        
        # Check Secret Manager connectivity
        if self.secrets_manager:
            try:
                validation = self.secrets_manager.validate_setup()
                sm_status = validation['secret_manager_available']
                validation_results.append(("Secret Manager", sm_status))
            except:
                validation_results.append(("Secret Manager", False))
        else:
            validation_results.append(("Secret Manager", False))
        
        # Print results
        all_valid = True
        for check_name, status in validation_results:
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {check_name}")
            if not status:
                all_valid = False
        
        if all_valid:
            print(f"\n{Colors.OKGREEN}🎉 Setup validation successful!{Colors.ENDC}")
        else:
            print(f"\n{Colors.WARNING}⚠️  Some validations failed. Check the logs.{Colors.ENDC}")
        
        return all_valid
    
    def print_completion_summary(self):
        """Print setup completion summary"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔" + "═" * 60 + "╗")
        print("║" + " " * 18 + "SETUP COMPLETED!" + " " * 19 + "║")
        print("╚" + "═" * 60 + "╝")
        print(f"{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}🎉 HTX Trading Platform has been successfully configured!{Colors.ENDC}\n")
        
        print(f"{Colors.OKBLUE}Quick Start Commands:{Colors.ENDC}")
        print(f"  Full platform:  {Colors.BOLD}./start_htx_personal.sh{Colors.ENDC}")
        print(f"  Backend only:    {Colors.BOLD}./start_backend_personal.sh{Colors.ENDC}")
        print(f"  Frontend only:   {Colors.BOLD}./start_frontend_personal.sh{Colors.ENDC}")
        
        print(f"\n{Colors.OKBLUE}Access URLs:{Colors.ENDC}")
        print(f"  📊 Dashboard:    {Colors.BOLD}http://localhost:3000{Colors.ENDC}")
        print(f"  📡 API:          {Colors.BOLD}http://localhost:8004{Colors.ENDC}")
        print(f"  📚 API Docs:     {Colors.BOLD}http://localhost:8004/docs{Colors.ENDC}")
        
        print(f"\n{Colors.OKBLUE}Configuration Files:{Colors.ENDC}")
        print(f"  🔧 Environment:  {Colors.BOLD}.env{Colors.ENDC}")
        print(f"  🔑 GCP Key:      {Colors.BOLD}gcp-service-account.json{Colors.ENDC}")
        print(f"  📝 Setup Log:    {Colors.BOLD}activation_setup.log{Colors.ENDC}")
        
        print(f"\n{Colors.WARNING}📋 Next Steps:{Colors.ENDC}")
        print("  1. Start the platform using the quick start commands")
        print("  2. Visit the dashboard to upload your trading data")
        print("  3. Configure additional settings in the web interface")
        print("  4. Review the logs if you encounter any issues")
        
        print(f"\n{Colors.OKCYAN}💡 Tips:{Colors.ENDC}")
        print("  • All API keys are securely stored in Google Secret Manager")
        print("  • Use the web interface to manage additional settings")
        print("  • Check activation_setup.log for detailed setup information")
        print("  • Restart services if configuration changes are needed")
    
    def run_setup(self):
        """Run the complete setup process"""
        try:
            self.print_header()
            
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return False
            
            # Step 2: GCP setup
            if not self.setup_gcp_project():
                return False
            
            # Step 3: Collect API keys
            api_keys = self.collect_api_keys()
            if not api_keys:
                print(f"{Colors.FAIL}❌ No API keys provided{Colors.ENDC}")
                return False
            
            # Step 4: Set up Secret Manager
            if not self.setup_secret_manager(api_keys):
                return False
            
            # Step 5: Install dependencies
            if not self.install_dependencies():
                return False
            
            # Step 6: Generate configuration
            if not self.generate_configuration():
                return False
            
            # Step 7: Validate setup
            if not self.validate_setup():
                print(f"{Colors.WARNING}⚠️  Setup completed with warnings{Colors.ENDC}")
            
            # Step 8: Show completion summary
            self.print_completion_summary()
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Setup interrupted by user{Colors.ENDC}")
            return False
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            print(f"\n{Colors.FAIL}❌ Setup failed: {e}{Colors.ENDC}")
            return False


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("HTX Project Personal Activation Setup")
        print("Usage: python activate_project.py")
        print("\nThis script will guide you through the complete setup process.")
        return
    
    activator = HTXProjectActivator()
    success = activator.run_setup()
    
    if success:
        print(f"\n{Colors.OKGREEN}🎉 Setup completed successfully!{Colors.ENDC}")
        sys.exit(0)
    else:
        print(f"\n{Colors.FAIL}❌ Setup failed. Check the logs for details.{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()