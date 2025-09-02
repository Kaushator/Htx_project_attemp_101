#!/bin/bash
# Docker API Testing Script
# Tests HTX API endpoints directly inside Docker container

echo "🐳 HTX API Testing via Docker"
echo "=========================================="

# Find backend container name
CONTAINER_NAME=$(docker ps --format "table {{.Names}}" | grep -E "(backend|htx)" | head -1)

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ No backend container found. Looking for any running container..."
    docker ps
    exit 1
fi

echo "✅ Found container: $CONTAINER_NAME"
echo ""

# Test endpoints inside Docker container
echo "🔄 Testing endpoints inside Docker container..."
echo ""

# Test 1: Health endpoint
echo "1. Testing /api/v1/health"
docker exec $CONTAINER_NAME curl -s "http://localhost:8000/api/v1/health" | head -5
echo ""

# Test 2: HTX Balance 
echo "2. Testing /api/v1/htx/balance"
docker exec $CONTAINER_NAME curl -s "http://localhost:8000/api/v1/htx/balance" | head -5
echo ""

# Test 3: HTX Coins (the problematic endpoint)
echo "3. Testing /api/v1/htx/coins"
docker exec $CONTAINER_NAME curl -s "http://localhost:8000/api/v1/htx/coins" | head -10
echo ""

# Test 4: Check available routes via OpenAPI
echo "4. Checking available HTX routes in OpenAPI spec"
docker exec $CONTAINER_NAME curl -s "http://localhost:8000/openapi.json" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    paths = data.get('paths', {})
    htx_paths = [p for p in paths.keys() if 'htx' in p]
    print('🔍 HTX endpoints found in OpenAPI:')
    for path in sorted(htx_paths):
        methods = list(paths[path].keys())
        print(f'  {path} [{", ".join(methods).upper()}]')
except:
    print('Failed to parse OpenAPI JSON')
"
echo ""

# Test 5: Check running processes in container
echo "5. Checking Python processes in container"
docker exec $CONTAINER_NAME ps aux | grep python
echo ""

echo "🏁 Docker API testing completed!"