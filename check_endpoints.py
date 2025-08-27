#!/usr/bin/env python3
"""
Simple endpoint checker
"""

import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8001"

def check_endpoint(name, url):
    """Check single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ {name}: {response.status_code}")
        if response.status_code == 200:
            return True
        else:
            print(f"   Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def main():
    print("🔍 Checking HTX Project API endpoints...")
    print(f"Base URL: {BASE_URL}")
    print()

    # Wait a bit for server to start
    time.sleep(3)

    results = []

    # Test root endpoint
    results.append(check_endpoint("Root", f"{BASE_URL}/"))

    # Test health endpoint
    results.append(check_endpoint("Health", f"{BASE_URL}/api/v1/health"))

    # Test files endpoint
    results.append(check_endpoint("Files", f"{BASE_URL}/api/v1/files"))

    # Test cashflow endpoint
    results.append(check_endpoint("Cashflow", f"{BASE_URL}/api/v1/cashflow"))

    print()
    print(f"Results: {sum(results)}/{len(results)} endpoints working")

    if all(results):
        print("🎉 All endpoints are working!")
        return 0
    else:
        print("❌ Some endpoints are not working")
        return 1

if __name__ == "__main__":
    sys.exit(main())
