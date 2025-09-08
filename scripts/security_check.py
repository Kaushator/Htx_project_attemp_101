#!/usr/bin/env python3
"""
HTX Project Security Validation Script
Comprehensive security checks for release preparation
"""

import os
import re
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation for pre-release checks"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_path = project_root / "backend"
        self.security_issues: List[Dict[str, Any]] = []
        
    def check_secrets_exposure(self) -> List[Dict[str, Any]]:
        """Check for exposed secrets in code"""
        logger.info("🔐 Checking for exposed secrets...")
        
        issues = []
        secret_patterns = [
            (r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'API Key'),
            (r'secret[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'Secret Key'),
            (r'password\s*[=:]\s*["\']([^"\']+)["\']', 'Password'),
            (r'token\s*[=:]\s*["\']([^"\']+)["\']', 'Token'),
            (r'["\'][A-Za-z0-9]{32,}["\']', 'Potential Secret'),
            (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
            (r'xoxb-[a-zA-Z0-9-]+', 'Slack Bot Token'),
            (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token'),
        ]
        
        for file_path in self.project_root.rglob("*.py"):
            if "venv" in str(file_path) or ".git" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern, secret_type in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip obvious environment variable references
                            if 'os.environ' in line or 'getenv' in line:
                                continue
                            if line.strip().startswith('#'):
                                continue
                                
                            issues.append({
                                'type': 'Exposed Secret',
                                'severity': 'HIGH',
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': line_num,
                                'content': line.strip(),
                                'secret_type': secret_type
                            })
            except Exception as e:
                logger.warning(f"Could not read file {file_path}: {e}")
        
        return issues
    
    def check_input_validation(self) -> List[Dict[str, Any]]:
        """Check for proper input validation"""
        logger.info("🛡️ Checking input validation...")
        
        issues = []
        validation_patterns = [
            (r'request\..*\.get\([^)]+\)', 'Direct request parameter access'),
            (r'eval\s*\(', 'Use of eval()'),
            (r'exec\s*\(', 'Use of exec()'),
            (r'subprocess\.[^(]+\([^)]*shell\s*=\s*True', 'Shell injection risk'),
            (r'os\.system\s*\(', 'OS command injection risk'),
        ]
        
        for file_path in self.backend_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern, issue_type in validation_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                'type': 'Input Validation',
                                'severity': 'MEDIUM',
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': line_num,
                                'content': line.strip(),
                                'issue': issue_type
                            })
            except Exception as e:
                logger.warning(f"Could not read file {file_path}: {e}")
        
        return issues
    
    def check_dependency_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check for known vulnerabilities in dependencies"""
        logger.info("📦 Checking dependency vulnerabilities...")
        
        issues = []
        requirements_file = self.backend_path / "requirements.txt"
        
        if not requirements_file.exists():
            issues.append({
                'type': 'Missing File',
                'severity': 'HIGH',
                'file': 'requirements.txt',
                'issue': 'Requirements file not found'
            })
            return issues
        
        try:
            # Try to use safety to check vulnerabilities
            result = subprocess.run(
                ["pip", "install", "safety"],
                capture_output=True,
                text=True,
                cwd=self.backend_path
            )
            
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd=self.backend_path
            )
            
            if result.returncode == 0:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    for vuln in vulnerabilities:
                        issues.append({
                            'type': 'Dependency Vulnerability',
                            'severity': 'HIGH',
                            'package': vuln.get('package'),
                            'version': vuln.get('installed_version'),
                            'vulnerability': vuln.get('vulnerability'),
                            'description': vuln.get('advisory')
                        })
                except json.JSONDecodeError:
                    pass
            
        except FileNotFoundError:
            logger.warning("Safety tool not available for vulnerability scanning")
        
        return issues
    
    def check_configuration_security(self) -> List[Dict[str, Any]]:
        """Check configuration security"""
        logger.info("⚙️ Checking configuration security...")
        
        issues = []
        
        # Check for insecure configurations
        config_files = [
            self.project_root / "docker-compose.yml",
            self.backend_path / "app" / "core" / "config.py",
            self.project_root / ".env",
            self.backend_path / ".env"
        ]
        
        for config_file in config_files:
            if not config_file.exists():
                continue
                
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for insecure settings
                insecure_patterns = [
                    (r'DEBUG\s*=\s*True', 'Debug mode enabled'),
                    (r'ALLOW_ORIGINS\s*=\s*\[\s*["\*"]', 'CORS allows all origins'),
                    (r'host\s*=\s*["\']0\.0\.0\.0["\']', 'Binding to all interfaces'),
                    (r'ssl_verify\s*=\s*False', 'SSL verification disabled'),
                    (r'verify\s*=\s*False', 'Certificate verification disabled'),
                ]
                
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern, issue_desc in insecure_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                'type': 'Configuration Security',
                                'severity': 'MEDIUM',
                                'file': str(config_file.relative_to(self.project_root)),
                                'line': line_num,
                                'content': line.strip(),
                                'issue': issue_desc
                            })
            except Exception as e:
                logger.warning(f"Could not read config file {config_file}: {e}")
        
        return issues
    
    def check_file_permissions(self) -> List[Dict[str, Any]]:
        """Check file permissions for sensitive files"""
        logger.info("📄 Checking file permissions...")
        
        issues = []
        sensitive_files = [
            ".env",
            "backend/.env",
            "secrets.json",
            "private_key.pem",
        ]
        
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    stat_info = full_path.stat()
                    permissions = oct(stat_info.st_mode)[-3:]
                    
                    # Check if file is readable by others
                    if permissions[2] in ['4', '5', '6', '7']:
                        issues.append({
                            'type': 'File Permissions',
                            'severity': 'MEDIUM',
                            'file': file_path,
                            'permissions': permissions,
                            'issue': 'Sensitive file readable by others'
                        })
                except Exception as e:
                    logger.warning(f"Could not check permissions for {file_path}: {e}")
        
        return issues
    
    def run_security_scan(self) -> Tuple[bool, Dict[str, Any]]:
        """Run comprehensive security scan"""
        logger.info("🔒 Starting Security Validation...")
        
        all_issues = []
        
        # Run all security checks
        checks = [
            ("Secrets Exposure", self.check_secrets_exposure),
            ("Input Validation", self.check_input_validation),
            ("Dependency Vulnerabilities", self.check_dependency_vulnerabilities),
            ("Configuration Security", self.check_configuration_security),
            ("File Permissions", self.check_file_permissions),
        ]
        
        for check_name, check_func in checks:
            try:
                logger.info(f"Running {check_name} check...")
                issues = check_func()
                all_issues.extend(issues)
                
                if issues:
                    logger.warning(f"{check_name}: Found {len(issues)} issues")
                else:
                    logger.info(f"{check_name}: No issues found")
                    
            except Exception as e:
                logger.error(f"Error in {check_name}: {e}")
                all_issues.append({
                    'type': 'Check Error',
                    'severity': 'HIGH',
                    'check': check_name,
                    'error': str(e)
                })
        
        # Categorize issues by severity
        critical_issues = [i for i in all_issues if i.get('severity') == 'CRITICAL']
        high_issues = [i for i in all_issues if i.get('severity') == 'HIGH']
        medium_issues = [i for i in all_issues if i.get('severity') == 'MEDIUM']
        low_issues = [i for i in all_issues if i.get('severity') == 'LOW']
        
        report = {
            'summary': {
                'total_issues': len(all_issues),
                'critical': len(critical_issues),
                'high': len(high_issues),
                'medium': len(medium_issues),
                'low': len(low_issues)
            },
            'issues': all_issues,
            'passed': len(critical_issues) == 0 and len(high_issues) == 0
        }
        
        # Save security report
        report_file = self.project_root / "security_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*50)
        print("🔒 SECURITY VALIDATION SUMMARY")
        print("="*50)
        print(f"Total Issues: {report['summary']['total_issues']}")
        print(f"🔴 Critical: {report['summary']['critical']}")
        print(f"🟠 High: {report['summary']['high']}")
        print(f"🟡 Medium: {report['summary']['medium']}")
        print(f"🟢 Low: {report['summary']['low']}")
        
        if report['passed']:
            print("\n✅ SECURITY VALIDATION PASSED")
        else:
            print("\n❌ SECURITY VALIDATION FAILED")
            print("Critical or High severity issues found!")
        
        print(f"\nDetailed report saved to: {report_file}")
        
        return report['passed'], report

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()
    
    validator = SecurityValidator(project_root)
    passed, report = validator.run_security_scan()
    
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()