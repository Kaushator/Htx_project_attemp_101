#!/usr/bin/env python3
"""
API Test Script
Tests all endpoints of the HTX Project API
"""

import json
import time
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

# Use TestClient instead of real server
client = TestClient(app)

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = client.get("/api/v1/health")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        assert False

def test_files_list():
    """Test files list endpoint"""
    print("\n🔍 Testing Files List Endpoint...")
    try:
        response = client.get("/api/v1/files")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        assert False

def test_trades_list():
    """Test trades list endpoint"""
    print("\n🔍 Testing Trades List Endpoint...")
    try:
        response = client.get("/api/v1/trades")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        assert False

def test_cashflow():
    """Test cashflow endpoint"""
    print("\n🔍 Testing Cashflow Endpoint...")
    try:
        response = client.get("/api/v1/cashflow")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        assert False

def test_file_upload():
    """Test file upload endpoint"""
    print("\n🔍 Testing File Upload Endpoint...")
    try:
        # Create a test CSV file
        test_file = Path("test_data.csv")
        test_content = "date,symbol,side,amount,price\n2024-01-01,BTC,SELL,0.1,50000"
        test_file.write_text(test_content)

        with open(test_file, 'rb') as f:
            response = client.post("/api/v1/files/upload", files={'file': ('test_data.csv', f, 'text/csv')})

        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")

        # Clean up
        test_file.unlink()
        assert response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        assert False

def main():
    """Run all tests"""
    print("🚀 Starting API Tests...")
    print("📍 Using TestClient (no server required)")
    print("=" * 50)

    tests = [
        test_health,
        test_files_list,
        test_trades_list,
        test_cashflow,
        test_file_upload
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")

if __name__ == "__main__":
    main()
