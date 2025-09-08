#!/bin/bash
# Quick test for HTX backend

set -euo pipefail

echo "=== HTX Backend Test ==="

cd /mnt/e/Htx_project_attemp_101/backend
source ../.venv_wsl/bin/activate

echo "✓ Environment activated"

# Test import
python -c "import app.main; print('✓ Import OK')"

# Start server in background
ENABLE_BACKGROUND_TASKS=false nohup uvicorn app.main:app --host 127.0.0.1 --port 8004 --log-level error >/dev/null 2>&1 &
SERVER_PID=$!

echo "✓ Server starting (PID: $SERVER_PID)"

# Wait for startup
sleep 5

# Test endpoints
echo "Testing endpoints..."

# Health check
HEALTH=$(curl -s -w "%{http_code}" "http://127.0.0.1:8004/api/v1/health" -o /tmp/health.json || echo "000")
if [ "$HEALTH" = "200" ]; then
    echo "✓ Health endpoint: $(cat /tmp/health.json)"
else
    echo "✗ Health endpoint failed (HTTP $HEALTH)"
fi

# Advanced PnL Summary  
SUMMARY=$(curl -s -w "%{http_code}" "http://127.0.0.1:8004/api/v1/advanced-pnl/summary?days=7" -o /tmp/summary.json || echo "000")
if [ "$SUMMARY" = "200" ]; then
    echo "✓ Advanced PnL Summary: $(cat /tmp/summary.json | head -100)"
else
    echo "✗ Advanced PnL Summary failed (HTTP $SUMMARY)"
    cat /tmp/summary.json 2>/dev/null || echo "No response body"
fi

# OpenAPI docs
DOCS=$(curl -s -w "%{http_code}" "http://127.0.0.1:8004/docs" -o /dev/null || echo "000")
if [ "$DOCS" = "200" ]; then
    echo "✓ OpenAPI docs available at http://127.0.0.1:8004/docs"
else
    echo "✗ OpenAPI docs failed (HTTP $DOCS)"
fi

# Cleanup
kill $SERVER_PID 2>/dev/null || true
echo "✓ Server stopped"

echo "=== Test Complete ==="
