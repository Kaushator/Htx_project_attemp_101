#!/usr/bin/env python3
"""
HTX Project Pre-Release Test Execution Framework
Comprehensive testing suite for release preparation
"""

import asyncio
import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pre_release_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PreReleaseTestRunner:
    """Comprehensive pre-release test execution framework"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_path = project_root / "backend"
        self.test_results: Dict[str, Any] = {}
        self.start_time = datetime.now()
        
    def run_command(self, command: str, cwd: Path = None) -> Tuple[int, str, str]:
        """Execute shell command and return result"""
        if cwd is None:
            cwd = self.project_root
            
        logger.info(f"Executing: {command} in {cwd}")
        
        try:
            result = subprocess.run(
                command.split(),
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return 1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Command failed: {command}, Error: {str(e)}")
            return 1, "", str(e)
    
    def test_code_quality(self) -> bool:
        """Test code quality with linting and formatting checks"""
        logger.info("🔍 Testing Code Quality...")
        
        # Check if backend directory exists
        if not self.backend_path.exists():
            logger.error("Backend directory not found")
            return False
        
        # Linting check
        return_code, stdout, stderr = self.run_command(
            "python -m ruff check .", 
            cwd=self.backend_path
        )
        
        self.test_results['code_quality'] = {
            'linting': {
                'passed': return_code == 0,
                'output': stdout,
                'errors': stderr
            }
        }
        
        if return_code != 0:
            logger.error(f"Linting failed: {stderr}")
            return False
        
        logger.info("✅ Code quality checks passed")
        return True
    
    def test_unit_tests(self) -> bool:
        """Run unit tests with coverage"""
        logger.info("🧪 Running Unit Tests...")
        
        # Install test dependencies
        self.run_command("pip install pytest pytest-asyncio pytest-cov", cwd=self.backend_path)
        
        # Run pytest with coverage
        return_code, stdout, stderr = self.run_command(
            "python -m pytest tests/ -v --cov=app --cov-report=json --cov-report=term",
            cwd=self.backend_path
        )
        
        # Parse coverage report if available
        coverage_file = self.backend_path / "coverage.json"
        coverage_percent = 0
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                    coverage_percent = coverage_data.get('totals', {}).get('percent_covered', 0)
            except Exception as e:
                logger.warning(f"Could not parse coverage report: {e}")
        
        self.test_results['unit_tests'] = {
            'passed': return_code == 0,
            'coverage': coverage_percent,
            'output': stdout,
            'errors': stderr
        }
        
        if return_code != 0:
            logger.error(f"Unit tests failed: {stderr}")
            return False
        
        if coverage_percent < 85:
            logger.warning(f"Coverage {coverage_percent}% below target 85%")
        
        logger.info(f"✅ Unit tests passed with {coverage_percent}% coverage")
        return True
    
    def test_api_endpoints(self) -> bool:
        """Test API endpoints functionality"""
        logger.info("🌐 Testing API Endpoints...")
        
        # Start the application in background
        import signal
        import time
        from multiprocessing import Process
        
        def start_server():
            os.chdir(self.backend_path)
            os.system("python -m uvicorn app.main:app --host 0.0.0.0 --port 8001")
        
        # Start server process
        server_process = Process(target=start_server)
        server_process.start()
        
        # Wait for server to start
        time.sleep(10)
        
        try:
            # Test health endpoint
            import httpx
            
            client = httpx.Client(base_url="http://localhost:8001")
            
            # Health check
            try:
                response = client.get("/health")
                health_ok = response.status_code == 200
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                health_ok = False
            
            # Test other endpoints
            endpoints_tested = []
            
            try:
                # Test file upload endpoint
                response = client.get("/api/v1/files/")
                endpoints_tested.append(("files", response.status_code == 200))
            except:
                endpoints_tested.append(("files", False))
            
            try:
                # Test PnL endpoint
                response = client.get("/api/v1/pnl/")
                endpoints_tested.append(("pnl", response.status_code == 200))
            except:
                endpoints_tested.append(("pnl", False))
            
            self.test_results['api_endpoints'] = {
                'health': health_ok,
                'endpoints': dict(endpoints_tested),
                'server_started': True
            }
            
            success = health_ok and all(result for _, result in endpoints_tested)
            
        except Exception as e:
            logger.error(f"API testing failed: {e}")
            self.test_results['api_endpoints'] = {
                'error': str(e),
                'server_started': False
            }
            success = False
        
        finally:
            # Cleanup server process
            server_process.terminate()
            server_process.join(timeout=5)
            if server_process.is_alive():
                server_process.kill()
        
        if success:
            logger.info("✅ API endpoints tests passed")
        else:
            logger.error("❌ API endpoints tests failed")
        
        return success
    
    def test_docker_build(self) -> bool:
        """Test Docker build process"""
        logger.info("🐳 Testing Docker Build...")
        
        # Check if Dockerfile exists
        dockerfile = self.backend_path / "Dockerfile"
        if not dockerfile.exists():
            logger.error("Dockerfile not found")
            return False
        
        # Build Docker image
        return_code, stdout, stderr = self.run_command(
            "docker build -t htx-project-test .",
            cwd=self.backend_path
        )
        
        self.test_results['docker_build'] = {
            'passed': return_code == 0,
            'output': stdout,
            'errors': stderr
        }
        
        if return_code != 0:
            logger.error(f"Docker build failed: {stderr}")
            return False
        
        logger.info("✅ Docker build successful")
        return True
    
    def test_gcp_integration(self) -> bool:
        """Test GCP integration components"""
        logger.info("☁️ Testing GCP Integration...")
        
        # Check if GCP test files exist
        gcp_tests = list(self.backend_path.glob("tests/test_gcp_*.py"))
        
        if not gcp_tests:
            logger.warning("No GCP integration tests found")
            self.test_results['gcp_integration'] = {'skipped': True}
            return True
        
        # Run GCP specific tests
        return_code, stdout, stderr = self.run_command(
            f"python -m pytest {' '.join(str(t) for t in gcp_tests)} -v",
            cwd=self.backend_path
        )
        
        self.test_results['gcp_integration'] = {
            'passed': return_code == 0,
            'test_files': [t.name for t in gcp_tests],
            'output': stdout,
            'errors': stderr
        }
        
        if return_code != 0:
            logger.warning(f"GCP integration tests failed: {stderr}")
            return False
        
        logger.info("✅ GCP integration tests passed")
        return True
    
    def test_performance(self) -> bool:
        """Run performance tests"""
        logger.info("⚡ Testing Performance...")
        
        perf_script = self.project_root / "scripts" / "test_performance.py"
        
        if not perf_script.exists():
            logger.warning("Performance test script not found")
            self.test_results['performance'] = {'skipped': True}
            return True
        
        return_code, stdout, stderr = self.run_command(
            f"python {perf_script}",
            cwd=self.project_root
        )
        
        self.test_results['performance'] = {
            'passed': return_code == 0,
            'output': stdout,
            'errors': stderr
        }
        
        if return_code != 0:
            logger.warning(f"Performance tests failed: {stderr}")
            return False
        
        logger.info("✅ Performance tests passed")
        return True
    
    def generate_report(self) -> None:
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report = {
            'execution_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration.total_seconds(),
                'project_root': str(self.project_root)
            },
            'test_results': self.test_results,
            'summary': {
                'total_tests': len(self.test_results),
                'passed': sum(1 for r in self.test_results.values() 
                            if isinstance(r, dict) and r.get('passed', False)),
                'failed': sum(1 for r in self.test_results.values() 
                            if isinstance(r, dict) and r.get('passed') is False),
                'skipped': sum(1 for r in self.test_results.values() 
                             if isinstance(r, dict) and r.get('skipped', False))
            }
        }
        
        # Save detailed report
        report_file = self.project_root / "pre_release_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 PRE-RELEASE TEST SUMMARY")
        print("="*60)
        print(f"Duration: {duration}")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"✅ Passed: {report['summary']['passed']}")
        print(f"❌ Failed: {report['summary']['failed']}")
        print(f"⏭️ Skipped: {report['summary']['skipped']}")
        print(f"\nDetailed report saved to: {report_file}")
        
        # Overall status
        all_passed = report['summary']['failed'] == 0
        if all_passed:
            print("\n🎉 ALL TESTS PASSED - READY FOR RELEASE! 🎉")
        else:
            print("\n⚠️ SOME TESTS FAILED - REVIEW BEFORE RELEASE ⚠️")
        
        return all_passed
    
    def run_all_tests(self) -> bool:
        """Execute all pre-release tests"""
        logger.info("🚀 Starting Pre-Release Test Suite...")
        
        test_suite = [
            ("Code Quality", self.test_code_quality),
            ("Unit Tests", self.test_unit_tests),
            ("API Endpoints", self.test_api_endpoints),
            ("Docker Build", self.test_docker_build),
            ("GCP Integration", self.test_gcp_integration),
            ("Performance", self.test_performance)
        ]
        
        results = []
        
        for test_name, test_func in test_suite:
            try:
                logger.info(f"\n{'='*50}")
                logger.info(f"Running: {test_name}")
                logger.info(f"{'='*50}")
                
                result = test_func()
                results.append(result)
                
                if result:
                    logger.info(f"✅ {test_name} completed successfully")
                else:
                    logger.error(f"❌ {test_name} failed")
                    
            except Exception as e:
                logger.error(f"💥 {test_name} crashed: {str(e)}")
                results.append(False)
        
        # Generate final report
        all_passed = self.generate_report()
        
        return all_passed

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()
    
    if not project_root.exists():
        logger.error(f"Project root does not exist: {project_root}")
        sys.exit(1)
    
    runner = PreReleaseTestRunner(project_root)
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()