#!/bin/bash
# Quick API test script for Phase 2.2
# Tests new insights endpoints for performance

BASE_URL="http://127.0.0.1:8004/api/v1"

echo "🚀 HTX Project Phase 2.2 - Quick Insights API Test"
echo "=================================================="

# Function to test endpoint with timing
test_endpoint() {
    local endpoint=$1
    local name=$2
    echo -n "Testing $name... "
    
    start_time=$(date +%s.%3N)
    response=$(curl -s -w "%{http_code}" "$BASE_URL$endpoint" -o /tmp/response.json)
    end_time=$(date +%s.%3N)
    
    response_time=$(echo "$end_time - $start_time" | bc -l)
    
    if [ "$response" = "200" ]; then
        echo "✅ ${response_time}s"
        # Show first few lines of response
        head -3 /tmp/response.json | jq . 2>/dev/null || head -3 /tmp/response.json
    else
        echo "❌ HTTP $response"
        cat /tmp/response.json
    fi
    echo
}

# Check if server is running
echo "Checking server status..."
if ! curl -s "$BASE_URL/health/" > /dev/null; then
    echo "❌ Server not running on $BASE_URL"
    echo "Start with: make dev"
    exit 1
fi

echo "✅ Server is running"
echo

# Test all quick insights endpoints
test_endpoint "/insights/health-quick" "Quick Health Check"
test_endpoint "/insights/dashboard" "Dashboard Snapshot"
test_endpoint "/insights/top-symbols?limit=5" "Top 5 Symbols"
test_endpoint "/insights/activity?hours=24" "24h Activity"
test_endpoint "/insights/pnl-estimate" "Quick PnL Estimate"
test_endpoint "/insights/streak" "Trading Streak"

# Test existing endpoints for comparison
echo "🔄 Testing existing endpoints for comparison:"
test_endpoint "/trades/" "Trade List"
test_endpoint "/pnl/summary" "PnL Summary (cached)"

echo "=================================================="
echo "Phase 2.2 Quick Insights Test Complete!"

# Clean up
rm -f /tmp/response.json
