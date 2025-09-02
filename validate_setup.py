#!/usr/bin/env python3
"""
HTX Project Setup Validation
Comprehensive testing of all endpoints, integrations, and configurations
"""

import os
import sys
import asyncio
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass, asdict

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('validation_results.log')
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


@dataclass
class ValidationResult:
    """Result of a validation check"""
    name: str
    category: str
    status: str  # "PASS", "FAIL", "WARNING", "SKIP"
    message: str
    details: Optional[Dict[str, Any]] = None
    duration: float = 0.0


class HTXProjectValidator:
    """Comprehensive validator for HTX Project setup"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.results: List[ValidationResult] = []
        self.backend_process = None
        
    def add_result(self, name: str, category: str, status: str, message: str, 
                   details: Optional[Dict[str, Any]] = None, duration: float = 0.0):
        """Add a validation result"""
        result = ValidationResult(name, category, status, message, details, duration)
        self.results.append(result)
        
        # Print result immediately
        status_color = {
            "PASS": Colors.OKGREEN,
            "FAIL": Colors.FAIL,
            "WARNING": Colors.WARNING,
            "SKIP": Colors.OKCYAN
        }.get(status, Colors.ENDC)
        
        status_icon = {
            "PASS": "✅",
            "FAIL": "❌", 
            "WARNING": "⚠️",
            "SKIP": "⏭️"
        }.get(status, "❓")
        
        print(f"  {status_icon} {status_color}{name}: {message}{Colors.ENDC}")
        
        if details and logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Details for {name}: {details}")
    
    def validate_environment(self):
        """Validate environment configuration"""
        print(f"\n{Colors.HEADER}🔧 Environment Configuration{Colors.ENDC}")
        
        start_time = time.time()
        
        # Check .env file
        env_file = project_root / ".env"
        if env_file.exists():
            self.add_result(
                "Environment File", "Environment", "PASS",
                f"Found .env file at {env_file}",
                duration=time.time() - start_time
            )
        else:
            self.add_result(
                "Environment File", "Environment", "FAIL",
                ".env file not found. Run activation script first.",
                duration=time.time() - start_time
            )
            return
        
        # Load and validate configuration
        try:
            from app.core.config import settings
            
            # Validate API keys
            api_validation = settings.validate_api_keys()
            
            for service, config in api_validation.items():
                status = "PASS" if config.get("configured", False) else "WARNING"
                self.add_result(
                    f"{service.upper()} API Keys", "Environment", status,
                    f"Configured: {config.get('configured', False)}",
                    details=config,
                    duration=time.time() - start_time
                )
            
            # Check Secret Manager
            if settings.secret_manager_enabled:
                self.add_result(
                    "Google Secret Manager", "Environment", "PASS",
                    "Secret Manager integration enabled",
                    duration=time.time() - start_time
                )
            else:
                self.add_result(
                    "Google Secret Manager", "Environment", "WARNING",
                    "Secret Manager not enabled (using environment variables)",
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            self.add_result(
                "Configuration Loading", "Environment", "FAIL",
                f"Failed to load configuration: {e}",
                duration=time.time() - start_time
            )
    
    def validate_dependencies(self):
        """Validate installed dependencies"""
        print(f"\n{Colors.HEADER}📦 Dependencies{Colors.ENDC}")
        
        # Backend dependencies
        backend_deps = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("sqlalchemy", "Database ORM"),
            ("pydantic", "Data validation"),
            ("cryptography", "Encryption support"),
            ("requests", "HTTP client"),
            ("pandas", "Data analysis"),
            ("numpy", "Numerical computing")
        ]
        
        for package, description in backend_deps:
            start_time = time.time()
            try:
                __import__(package)
                self.add_result(
                    package, "Dependencies", "PASS",
                    f"{description} available",
                    duration=time.time() - start_time
                )
            except ImportError:
                self.add_result(
                    package, "Dependencies", "FAIL",
                    f"{description} not found",
                    duration=time.time() - start_time
                )
        
        # Optional ML dependencies
        ml_deps = [
            ("sklearn", "Machine Learning"),
            ("torch", "PyTorch (optional)"),
            ("transformers", "Transformers (optional)")
        ]
        
        for package, description in ml_deps:
            start_time = time.time()
            try:
                __import__(package)
                self.add_result(
                    package, "Dependencies", "PASS",
                    f"{description} available",
                    duration=time.time() - start_time
                )
            except ImportError:
                self.add_result(
                    package, "Dependencies", "SKIP",
                    f"{description} not installed (optional)",
                    duration=time.time() - start_time
                )
        
        # GCP dependencies
        gcp_deps = [
            ("google.cloud.storage", "Google Cloud Storage"),
            ("google.cloud.secretmanager", "Google Secret Manager"),
            ("google.cloud.pubsub_v1", "Google Pub/Sub")
        ]
        
        for package, description in gcp_deps:
            start_time = time.time()
            try:
                __import__(package)
                self.add_result(
                    package.split('.')[-1], "Dependencies", "PASS",
                    f"{description} available",
                    duration=time.time() - start_time
                )
            except ImportError:
                self.add_result(
                    package.split('.')[-1], "Dependencies", "WARNING",
                    f"{description} not installed (GCP features disabled)",
                    duration=time.time() - start_time
                )
    
    def validate_database(self):
        """Validate database connectivity"""
        print(f"\n{Colors.HEADER}🗄️  Database{Colors.ENDC}")
        
        start_time = time.time()
        try:
            from app.db.session import engine
            from app.db.init_db import init_db
            
            # Test database connection
            async def test_db():
                try:
                    await init_db()
                    return True
                except Exception as e:
                    logger.error(f"Database initialization failed: {e}")
                    return False
            
            success = asyncio.run(test_db())
            
            if success:
                self.add_result(
                    "Database Connection", "Database", "PASS",
                    "Database initialized successfully",
                    duration=time.time() - start_time
                )
            else:
                self.add_result(
                    "Database Connection", "Database", "FAIL",
                    "Database initialization failed",
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            self.add_result(
                "Database Setup", "Database", "FAIL",
                f"Database setup error: {e}",
                duration=time.time() - start_time
            )
    
    def validate_api_endpoints(self):
        """Validate API endpoints"""
        print(f"\n{Colors.HEADER}🌐 API Endpoints{Colors.ENDC}")
        
        # Core endpoints to test
        endpoints = [
            ("/", "Root endpoint"),
            ("/docs", "API documentation"),
            ("/api/v1/health/ping", "Health check"),
            ("/api/v1/health/status", "System status"),
            ("/api/v1/trades/summary", "Trades summary"),
            ("/api/v1/pnl/overview", "P&L overview"),
            ("/api/v1/cashflow/summary", "Cashflow summary"),
            ("/api/v1/htx/markets", "HTX markets"),
            ("/api/v1/insights/quick", "Quick insights")
        ]
        
        # Optional endpoints (may not be available)
        optional_endpoints = [
            ("/api/v1/ml/plan", "ML planning"),
            ("/api/v1/ml/dashboard", "ML dashboard"),
            ("/api/v1/gcp/health", "GCP health check")
        ]
        
        # Test core endpoints
        for endpoint, description in endpoints:
            self._test_endpoint(endpoint, description, required=True)
        
        # Test optional endpoints
        for endpoint, description in optional_endpoints:
            self._test_endpoint(endpoint, description, required=False)
    
    def _test_endpoint(self, endpoint: str, description: str, required: bool = True):
        """Test a single API endpoint"""
        start_time = time.time()
        
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                self.add_result(
                    description, "API", "PASS",
                    f"Endpoint responding (HTTP {response.status_code})",
                    details={"url": url, "status_code": response.status_code},
                    duration=time.time() - start_time
                )
            elif response.status_code == 404 and not required:
                self.add_result(
                    description, "API", "SKIP",
                    "Optional endpoint not available",
                    details={"url": url, "status_code": response.status_code},
                    duration=time.time() - start_time
                )
            else:
                status = "FAIL" if required else "WARNING"
                self.add_result(
                    description, "API", status,
                    f"Endpoint error (HTTP {response.status_code})",
                    details={"url": url, "status_code": response.status_code},
                    duration=time.time() - start_time
                )
                
        except requests.exceptions.ConnectionError:
            status = "FAIL" if required else "WARNING"
            self.add_result(
                description, "API", status,
                "Cannot connect to API server",
                details={"url": f"{self.base_url}{endpoint}"},
                duration=time.time() - start_time
            )
        except Exception as e:
            status = "FAIL" if required else "WARNING"
            self.add_result(
                description, "API", status,
                f"Request failed: {e}",
                details={"url": f"{self.base_url}{endpoint}"},
                duration=time.time() - start_time
            )
    
    def validate_gcp_integration(self):
        """Validate Google Cloud Platform integration"""
        print(f"\n{Colors.HEADER}☁️  Google Cloud Platform{Colors.ENDC}")
        
        start_time = time.time()
        
        try:
            from app.core.config import settings
            
            if not settings.gcp_enabled:
                self.add_result(
                    "GCP Configuration", "GCP", "SKIP",
                    "GCP integration not configured",
                    duration=time.time() - start_time
                )
                return
            
            # Test GCP credentials
            creds_file = Path(settings.GOOGLE_APPLICATION_CREDENTIALS or "")
            if creds_file.exists():
                self.add_result(
                    "GCP Credentials", "GCP", "PASS",
                    f"Service account key found: {creds_file}",
                    duration=time.time() - start_time
                )
            else:
                self.add_result(
                    "GCP Credentials", "GCP", "FAIL",
                    "Service account key file not found",
                    duration=time.time() - start_time
                )
                return
            
            # Test Secret Manager
            if settings.secret_manager_enabled:
                try:
                    secrets_manager = settings._get_secrets_manager()
                    if secrets_manager:
                        validation = secrets_manager.validate_setup()
                        if validation["secret_manager_available"]:
                            self.add_result(
                                "Secret Manager", "GCP", "PASS",
                                "Secret Manager connectivity verified",
                                details=validation,
                                duration=time.time() - start_time
                            )
                        else:
                            self.add_result(
                                "Secret Manager", "GCP", "FAIL",
                                "Secret Manager not available",
                                details=validation,
                                duration=time.time() - start_time
                            )
                    else:
                        self.add_result(
                            "Secret Manager", "GCP", "FAIL",
                            "Failed to initialize Secret Manager",
                            duration=time.time() - start_time
                        )
                except Exception as e:
                    self.add_result(
                        "Secret Manager", "GCP", "FAIL",
                        f"Secret Manager error: {e}",
                        duration=time.time() - start_time
                    )
            else:
                self.add_result(
                    "Secret Manager", "GCP", "SKIP",
                    "Secret Manager integration disabled",
                    duration=time.time() - start_time
                )
            
        except Exception as e:
            self.add_result(
                "GCP Setup", "GCP", "FAIL",
                f"GCP validation error: {e}",
                duration=time.time() - start_time
            )
    
    def validate_file_processing(self):
        """Validate file processing capabilities"""
        print(f"\n{Colors.HEADER}📁 File Processing{Colors.ENDC}")
        
        start_time = time.time()
        
        try:
            from app.core.config import settings
            
            # Check upload directory
            upload_dir = Path(settings.UPLOAD_DIR)
            if upload_dir.exists():
                self.add_result(
                    "Upload Directory", "Files", "PASS",
                    f"Upload directory exists: {upload_dir}",
                    duration=time.time() - start_time
                )
            else:
                upload_dir.mkdir(parents=True, exist_ok=True)
                self.add_result(
                    "Upload Directory", "Files", "PASS",
                    f"Created upload directory: {upload_dir}",
                    duration=time.time() - start_time
                )
            
            # Check processed directory
            processed_dir = Path(settings.PROCESSED_DIR)
            if processed_dir.exists():
                self.add_result(
                    "Processed Directory", "Files", "PASS",
                    f"Processed directory exists: {processed_dir}",
                    duration=time.time() - start_time
                )
            else:
                processed_dir.mkdir(parents=True, exist_ok=True)
                self.add_result(
                    "Processed Directory", "Files", "PASS",
                    f"Created processed directory: {processed_dir}",
                    duration=time.time() - start_time
                )
            
            # Test CSV parser
            try:
                from app.services.parser_csv import CSVParser
                parser = CSVParser()
                
                self.add_result(
                    "CSV Parser", "Files", "PASS",
                    "CSV parser initialized successfully",
                    duration=time.time() - start_time
                )
            except Exception as e:
                self.add_result(
                    "CSV Parser", "Files", "FAIL",
                    f"CSV parser error: {e}",
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            self.add_result(
                "File Processing Setup", "Files", "FAIL",
                f"File processing validation error: {e}",
                duration=time.time() - start_time
            )
    
    def generate_report(self):
        """Generate validation report"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔" + "═" * 60 + "╗")
        print("║" + " " * 20 + "VALIDATION REPORT" + " " * 21 + "║")
        print("╚" + "═" * 60 + "╝")
        print(f"{Colors.ENDC}")
        
        # Count results by status
        status_counts = {"PASS": 0, "FAIL": 0, "WARNING": 0, "SKIP": 0}
        for result in self.results:
            status_counts[result.status] += 1
        
        total_tests = len(self.results)
        
        print(f"{Colors.OKBLUE}Test Summary:{Colors.ENDC}")
        print(f"  Total Tests: {total_tests}")
        print(f"  {Colors.OKGREEN}✅ Passed: {status_counts['PASS']}{Colors.ENDC}")
        print(f"  {Colors.FAIL}❌ Failed: {status_counts['FAIL']}{Colors.ENDC}")
        print(f"  {Colors.WARNING}⚠️  Warnings: {status_counts['WARNING']}{Colors.ENDC}")
        print(f"  {Colors.OKCYAN}⏭️  Skipped: {status_counts['SKIP']}{Colors.ENDC}")
        
        # Calculate success rate
        success_rate = (status_counts['PASS'] / max(total_tests - status_counts['SKIP'], 1)) * 100
        
        print(f"\n{Colors.OKBLUE}Success Rate: {success_rate:.1f}%{Colors.ENDC}")
        
        # Show failures if any
        failures = [r for r in self.results if r.status == "FAIL"]
        if failures:
            print(f"\n{Colors.FAIL}❌ Failed Tests:{Colors.ENDC}")
            for failure in failures:
                print(f"  • {failure.name}: {failure.message}")
        
        # Show warnings if any
        warnings = [r for r in self.results if r.status == "WARNING"]
        if warnings:
            print(f"\n{Colors.WARNING}⚠️  Warnings:{Colors.ENDC}")
            for warning in warnings:
                print(f"  • {warning.name}: {warning.message}")
        
        # Overall status
        if status_counts['FAIL'] == 0:
            if status_counts['WARNING'] == 0:
                print(f"\n{Colors.OKGREEN}🎉 All tests passed! Your HTX Project is ready to use.{Colors.ENDC}")
            else:
                print(f"\n{Colors.WARNING}✅ Tests passed with warnings. Review warnings above.{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}❌ Some tests failed. Please fix the issues above.{Colors.ENDC}")
        
        # Save detailed report
        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed": status_counts['PASS'],
                "failed": status_counts['FAIL'],
                "warnings": status_counts['WARNING'],
                "skipped": status_counts['SKIP'],
                "success_rate": success_rate
            },
            "results": [asdict(result) for result in self.results]
        }
        
        report_file = project_root / "validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n{Colors.OKCYAN}📊 Detailed report saved to: {report_file}{Colors.ENDC}")
    
    def run_validation(self):
        """Run complete validation suite"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("╔" + "═" * 60 + "╗")
        print("║" + " " * 15 + "HTX PROJECT VALIDATION" + " " * 16 + "║")
        print("╚" + "═" * 60 + "╝")
        print(f"{Colors.ENDC}")
        
        print(f"{Colors.OKBLUE}Validating HTX Trading Platform setup...{Colors.ENDC}")
        
        # Run validation steps
        self.validate_environment()
        self.validate_dependencies()
        self.validate_database()
        self.validate_api_endpoints()
        self.validate_gcp_integration()
        self.validate_file_processing()
        
        # Generate report
        self.generate_report()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HTX Project Setup Validation")
    parser.add_argument("--base-url", default="http://localhost:8004", 
                       help="Base URL for API testing")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = HTXProjectValidator(base_url=args.base_url)
    validator.run_validation()


if __name__ == "__main__":
    main()