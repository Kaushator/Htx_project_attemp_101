# Security Testing Framework for HTX Trading Platform

## Overview

This document outlines a comprehensive security testing framework specifically designed for the HTX Trading Platform, focusing on API key management, CORS configuration, authentication mechanisms, and protection against common web vulnerabilities.

## Security Test Categories

### 1. API Key & Secret Management Security

#### 1.1 HTX API Key Protection
```python
# test_htx_api_security.py
import pytest
import os
from app.core.config import settings
from app.services.htx_client import HTXClient

class TestHTXAPIKeySecurity:
    
    def test_api_keys_not_logged(self, caplog):
        """Ensure API keys are never written to logs"""
        # Simulate API call with real key structure
        test_key = "test-htx-key-12345"
        test_secret = "test-htx-secret-67890"
        
        # Mock HTX client initialization
        with caplog.at_level("DEBUG"):
            client = HTXClient(api_key=test_key, api_secret=test_secret)
            client.get_account_balance()  # This should trigger logging
        
        # Verify keys don't appear in logs
        log_content = caplog.text
        assert test_key not in log_content
        assert test_secret not in log_content
        assert "***" in log_content or "[REDACTED]" in log_content
    
    def test_api_key_encryption_at_rest(self):
        """Test that API keys are encrypted when stored"""
        from app.core.config import settings
        
        # Test encryption/decryption
        test_key = "test-api-key-12345"
        encrypted_key = settings.encrypt(test_key)
        decrypted_key = settings.decrypt(encrypted_key)
        
        assert encrypted_key != test_key
        assert decrypted_key == test_key
        assert len(encrypted_key) > len(test_key)
    
    def test_env_file_security(self):
        """Ensure .env file doesn't contain plain text secrets"""
        env_file_path = ".env"
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r') as f:
                content = f.read()
            
            # Check for obvious plain text patterns
            suspicious_patterns = [
                "HTX_API_KEY=ak-",  # Plain HTX key
                "HTX_API_SECRET=sk-",  # Plain HTX secret
                "password=",
                "secret=admin"
            ]
            
            for pattern in suspicious_patterns:
                assert pattern not in content.lower()
    
    def test_api_key_validation(self):
        """Test API key format validation"""
        from app.services.htx_client import HTXClient
        
        invalid_keys = [
            "",  # Empty key
            "short",  # Too short
            "invalid-chars-!@#$",  # Invalid characters
            None,  # Null key
        ]
        
        for invalid_key in invalid_keys:
            with pytest.raises(ValueError):
                HTXClient(api_key=invalid_key, api_secret="valid-secret")
    
    def test_api_signature_security(self):
        """Test HMAC signature generation security"""
        client = HTXClient(api_key="test-key", api_secret="test-secret")
        
        # Test signature consistency
        params = {"symbol": "btcusdt", "limit": 100}
        sig1 = client._generate_signature(params)
        sig2 = client._generate_signature(params)
        
        assert sig1 == sig2  # Same params should generate same signature
        
        # Test signature changes with different params
        params2 = {"symbol": "ethusdt", "limit": 100}
        sig3 = client._generate_signature(params2)
        
        assert sig1 != sig3  # Different params should generate different signatures
```

#### 1.2 Authentication Security Testing
```python
# test_authentication_security.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestAuthenticationSecurity:
    
    @pytest.mark.asyncio
    async def test_protected_endpoints_require_auth(self):
        """Test that protected endpoints reject unauthenticated requests"""
        protected_endpoints = [
            "/api/v1/htx/balance",
            "/api/v1/htx/trades",
            "/api/v1/htx/orders",
            "/api/v1/user/profile",
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for endpoint in protected_endpoints:
                response = await client.get(endpoint)
                assert response.status_code == 401
                
                error_data = response.json()
                assert "unauthorized" in error_data.get("detail", "").lower()
    
    @pytest.mark.asyncio
    async def test_invalid_api_key_rejection(self):
        """Test rejection of invalid API keys"""
        invalid_keys = [
            "invalid-key-123",
            "expired-key-456",
            "",
            "malformed-key-!@#$"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for invalid_key in invalid_keys:
                response = await client.get(
                    "/api/v1/htx/balance",
                    headers={"X-HTX-API-KEY": invalid_key}
                )
                assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_api_key_timing_attack_protection(self):
        """Test protection against timing attacks on API key validation"""
        import time
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test with valid-length but wrong key
            start_time = time.time()
            response1 = await client.get(
                "/api/v1/htx/balance",
                headers={"X-HTX-API-KEY": "valid-length-wrong-key-123456789"}
            )
            time1 = time.time() - start_time
            
            # Test with completely invalid key
            start_time = time.time()
            response2 = await client.get(
                "/api/v1/htx/balance",
                headers={"X-HTX-API-KEY": "invalid"}
            )
            time2 = time.time() - start_time
            
            # Both should take similar time (within 50ms)
            time_diff = abs(time1 - time2)
            assert time_diff < 0.05  # 50ms tolerance
            
            # Both should return 401
            assert response1.status_code == 401
            assert response2.status_code == 401
```

### 2. CORS Security Testing

#### 2.1 CORS Configuration Validation
```python
# test_cors_security.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestCORSSecurity:
    
    @pytest.mark.asyncio
    async def test_cors_allowed_origins(self):
        """Test CORS allows only specified origins"""
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8080",
            "https://htx-platform.com"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for origin in allowed_origins:
                response = await client.options(
                    "/api/v1/health",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "GET"
                    }
                )
                
                assert response.status_code == 200
                cors_origin = response.headers.get("Access-Control-Allow-Origin")
                assert cors_origin == origin or cors_origin == "*"
    
    @pytest.mark.asyncio
    async def test_cors_blocks_unauthorized_origins(self):
        """Test CORS blocks unauthorized origins"""
        unauthorized_origins = [
            "http://malicious-site.com",
            "https://attacker.evil",
            "http://localhost:9999",
            "file://local-file"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for origin in unauthorized_origins:
                response = await client.options(
                    "/api/v1/health",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "GET"
                    }
                )
                
                # Should either reject or not include the origin in response
                cors_origin = response.headers.get("Access-Control-Allow-Origin")
                assert cors_origin != origin
    
    @pytest.mark.asyncio
    async def test_cors_method_restrictions(self):
        """Test CORS method restrictions"""
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        dangerous_methods = ["TRACE", "CONNECT", "PATCH"]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test allowed methods
            for method in allowed_methods:
                response = await client.options(
                    "/api/v1/health",
                    headers={
                        "Origin": "http://localhost:3000",
                        "Access-Control-Request-Method": method
                    }
                )
                
                allowed = response.headers.get("Access-Control-Allow-Methods", "")
                assert method in allowed
            
            # Test dangerous methods are not allowed
            for method in dangerous_methods:
                response = await client.options(
                    "/api/v1/health",
                    headers={
                        "Origin": "http://localhost:3000",
                        "Access-Control-Request-Method": method
                    }
                )
                
                allowed = response.headers.get("Access-Control-Allow-Methods", "")
                assert method not in allowed
    
    @pytest.mark.asyncio
    async def test_cors_credentials_handling(self):
        """Test CORS credentials handling"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.options(
                "/api/v1/health",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET"
                }
            )
            
            # Check if credentials are properly configured
            credentials = response.headers.get("Access-Control-Allow-Credentials")
            if credentials:
                assert credentials.lower() == "true"
                
                # If credentials are allowed, origin must be specific (not *)
                origin = response.headers.get("Access-Control-Allow-Origin")
                assert origin != "*"
```

### 3. Input Validation & Injection Protection

#### 3.1 SQL Injection Prevention
```python
# test_sql_injection_security.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestSQLInjectionSecurity:
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_query_params(self):
        """Test SQL injection prevention in query parameters"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE trades; --",
            "' UNION SELECT * FROM users --",
            "1; DELETE FROM trades WHERE 1=1 --",
            "' OR 1=1 #",
            "\"; SELECT * FROM information_schema.tables --"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for payload in sql_payloads:
                # Test in symbol parameter
                response = await client.get(f"/api/v1/trades?symbol={payload}")
                
                # Should return validation error, not execute SQL
                assert response.status_code == 422
                error_data = response.json()
                assert "validation" in error_data.get("detail", "").lower()
                
                # Response should not contain SQL error messages
                response_text = response.text.lower()
                sql_errors = ["syntax error", "mysql", "postgresql", "sqlite", "table", "column"]
                for error_term in sql_errors:
                    assert error_term not in response_text
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_json_body(self):
        """Test SQL injection prevention in JSON request bodies"""
        sql_payloads = [
            {"symbol": "' OR '1'='1"},
            {"start_date": "'; DROP TABLE trades; --"},
            {"metrics": ["sharpe", "' UNION SELECT password FROM users --"]}
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for payload in sql_payloads:
                response = await client.post(
                    "/api/v1/analytics/risk",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Should validate and reject malicious input
                assert response.status_code == 422
                
                # Should not expose SQL internals
                response_text = response.text.lower()
                assert "drop" not in response_text
                assert "union" not in response_text
                assert "select" not in response_text
```

#### 3.2 File Upload Security
```python
# test_file_upload_security.py
import pytest
from httpx import AsyncClient
from app.main import app
import io

class TestFileUploadSecurity:
    
    @pytest.mark.asyncio
    async def test_file_type_validation(self):
        """Test file type validation and restrictions"""
        malicious_files = [
            ("malware.exe", b"MZ\x90\x00", "application/x-executable"),
            ("script.js", b"alert('xss')", "application/javascript"),
            ("virus.bat", b"@echo off\ndel *.*", "text/plain"),
            ("shell.php", b"<?php system($_GET['cmd']); ?>", "application/x-php")
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for filename, content, content_type in malicious_files:
                files = {"file": (filename, content, content_type)}
                response = await client.post("/api/v1/files/upload", files=files)
                
                # Should reject non-CSV/Excel files
                assert response.status_code == 422
                error_data = response.json()
                assert "file type" in error_data.get("detail", "").lower()
    
    @pytest.mark.asyncio
    async def test_file_size_limits(self):
        """Test file size limit enforcement"""
        # Create oversized file (>50MB)
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            files = {"file": ("large.csv", large_content, "text/csv")}
            response = await client.post("/api/v1/files/upload", files=files)
            
            assert response.status_code == 413  # Payload Too Large
            error_data = response.json()
            assert "file size" in error_data.get("detail", "").lower()
    
    @pytest.mark.asyncio
    async def test_filename_sanitization(self):
        """Test filename sanitization against path traversal"""
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "normal.csv\x00.exe",  # Null byte injection
            "file with spaces and unicode 你好.csv",
            "very-long-filename-" + "x" * 500 + ".csv"
        ]
        
        csv_content = "date,symbol,side,quantity,price\n2024-01-01,BTC,buy,1.0,50000"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for filename in malicious_filenames:
                files = {"file": (filename, csv_content.encode(), "text/csv")}
                response = await client.post("/api/v1/files/upload", files=files)
                
                if response.status_code == 200:
                    # If upload succeeds, verify filename was sanitized
                    response_data = response.json()
                    stored_filename = response_data.get("filename", "")
                    
                    # Should not contain path traversal elements
                    assert "../" not in stored_filename
                    assert "..\\" not in stored_filename
                    assert "\x00" not in stored_filename
                    
                    # Should have reasonable length
                    assert len(stored_filename) < 255
```

### 4. Security Headers & Configuration

#### 4.1 Security Headers Testing
```python
# test_security_headers.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestSecurityHeaders:
    
    @pytest.mark.asyncio
    async def test_security_headers_present(self):
        """Test that essential security headers are present"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/health")
            
            headers = response.headers
            
            # Content Security Policy
            csp = headers.get("Content-Security-Policy")
            if csp:
                assert "default-src 'self'" in csp
                assert "script-src" in csp
            
            # X-Frame-Options
            frame_options = headers.get("X-Frame-Options")
            if frame_options:
                assert frame_options in ["DENY", "SAMEORIGIN"]
            
            # X-Content-Type-Options
            content_type_options = headers.get("X-Content-Type-Options")
            if content_type_options:
                assert content_type_options == "nosniff"
            
            # Strict-Transport-Security (for HTTPS)
            hsts = headers.get("Strict-Transport-Security")
            if hsts:
                assert "max-age=" in hsts
            
            # X-XSS-Protection
            xss_protection = headers.get("X-XSS-Protection")
            if xss_protection:
                assert xss_protection in ["1; mode=block", "0"]
    
    @pytest.mark.asyncio
    async def test_information_disclosure_prevention(self):
        """Test that sensitive information is not disclosed"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/health")
            
            headers = response.headers
            
            # Server header should not reveal version
            server = headers.get("Server", "")
            assert "FastAPI" not in server or "/" not in server
            
            # Should not expose internal framework details
            response_text = response.text
            assert "FastAPI" not in response_text
            assert "uvicorn" not in response_text.lower()
            assert "python" not in response_text.lower()
    
    @pytest.mark.asyncio
    async def test_error_information_leakage(self):
        """Test that errors don't leak sensitive information"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test 404 error
            response = await client.get("/api/v1/nonexistent-endpoint")
            assert response.status_code == 404
            
            error_data = response.json()
            error_text = str(error_data).lower()
            
            # Should not contain sensitive paths or system info
            sensitive_terms = [
                "/home/", "/var/", "/etc/",
                "traceback", "exception",
                "sqlalchemy", "database",
                "file not found", "permission denied"
            ]
            
            for term in sensitive_terms:
                assert term not in error_text
```

### 5. Rate Limiting & DoS Protection

#### 5.1 Rate Limiting Tests
```python
# test_rate_limiting_security.py
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

class TestRateLimitingSecurity:
    
    @pytest.mark.asyncio
    async def test_api_rate_limiting(self):
        """Test API rate limiting enforcement"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Make rapid requests to test rate limiting
            tasks = []
            for _ in range(150):  # Exceed typical rate limits
                task = client.get("/api/v1/health")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Should have some rate limited responses
            rate_limited_count = sum(
                1 for r in responses 
                if hasattr(r, 'status_code') and r.status_code == 429
            )
            
            # At least some requests should be rate limited
            assert rate_limited_count > 0
            
            # Rate limited responses should include retry-after
            for response in responses:
                if hasattr(response, 'status_code') and response.status_code == 429:
                    retry_after = response.headers.get('Retry-After')
                    assert retry_after is not None
                    assert int(retry_after) > 0
    
    @pytest.mark.asyncio
    async def test_file_upload_rate_limiting(self):
        """Test file upload rate limiting"""
        csv_content = "date,symbol,side,quantity,price\n2024-01-01,BTC,buy,1.0,50000"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Attempt multiple rapid file uploads
            upload_tasks = []
            for i in range(10):
                files = {"file": (f"test{i}.csv", csv_content.encode(), "text/csv")}
                task = client.post("/api/v1/files/upload", files=files)
                upload_tasks.append(task)
            
            responses = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            # Should limit concurrent uploads
            too_many_requests = sum(
                1 for r in responses 
                if hasattr(r, 'status_code') and r.status_code == 429
            )
            
            # Some uploads should be rejected
            assert too_many_requests > 0
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_protection(self):
        """Test protection against resource exhaustion attacks"""
        # Test with many concurrent connections
        connection_limit = 100
        
        async def make_slow_request():
            async with AsyncClient(app=app, base_url="http://test") as client:
                return await client.get("/api/v1/advanced-pnl/comprehensive?days=365")
        
        # Create many concurrent expensive requests
        tasks = [make_slow_request() for _ in range(connection_limit)]
        
        start_time = asyncio.get_event_loop().time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = asyncio.get_event_loop().time()
        
        # Should not take excessively long (protection mechanisms should kick in)
        total_time = end_time - start_time
        assert total_time < 60  # Should complete within 1 minute
        
        # Some requests should be rejected or timeout
        errors = sum(1 for r in responses if isinstance(r, Exception))
        rate_limited = sum(
            1 for r in responses 
            if hasattr(r, 'status_code') and r.status_code == 429
        )
        
        assert errors + rate_limited > 0  # Some protection should activate
```

## Security Testing Automation

### Automated Security Test Runner
```bash
#!/bin/bash
# security_test_runner.sh

echo "🔒 HTX Platform Security Test Suite"
echo "==================================="

# Set test environment
export TESTING=true
export DATABASE_URL="sqlite+aiosqlite:///./test_security.db"

# Run security tests with specific markers
echo "🔐 Testing API Key Security..."
pytest -m "security and api_keys" -v tests/security/

echo "🌐 Testing CORS Configuration..."
pytest -m "security and cors" -v tests/security/

echo "💉 Testing Injection Protection..."
pytest -m "security and injection" -v tests/security/

echo "📁 Testing File Upload Security..."
pytest -m "security and file_upload" -v tests/security/

echo "🚦 Testing Rate Limiting..."
pytest -m "security and rate_limiting" -v tests/security/

echo "🛡️ Testing Security Headers..."
pytest -m "security and headers" -v tests/security/

# Generate security report
echo "📊 Generating Security Report..."
pytest --html=reports/security_report.html --self-contained-html tests/security/

echo "✅ Security testing complete!"
echo "📋 Report available at: reports/security_report.html"
```

### Security Configuration Checklist
```yaml
security_checklist:
  api_security:
    - [ ] API keys encrypted at rest
    - [ ] API keys not logged in plain text
    - [ ] HMAC signature validation implemented
    - [ ] Rate limiting on API endpoints
    - [ ] Invalid API key rejection tested
  
  cors_security:
    - [ ] Allowed origins explicitly configured
    - [ ] Unauthorized origins blocked
    - [ ] Dangerous HTTP methods restricted
    - [ ] Credentials handling secure
  
  input_validation:
    - [ ] SQL injection prevention tested
    - [ ] File upload type validation
    - [ ] File size limits enforced
    - [ ] Filename sanitization implemented
  
  security_headers:
    - [ ] Content Security Policy configured
    - [ ] X-Frame-Options set
    - [ ] X-Content-Type-Options enabled
    - [ ] Information disclosure prevented
  
  dos_protection:
    - [ ] Rate limiting implemented
    - [ ] Resource exhaustion protection
    - [ ] Concurrent connection limits
    - [ ] Request size limits enforced
```

This comprehensive security testing framework ensures the HTX Trading Platform is protected against common web vulnerabilities and follows security best practices for handling sensitive trading data and API integrations.