# Docker API Testing Script (PowerShell)
# Tests HTX API endpoints directly inside Docker container

Write-Host "🐳 HTX API Testing via Docker" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Find backend container name
$containers = docker ps --format "{{.Names}}" | Where-Object { $_ -match "(backend|htx|app)" }

if (-not $containers) {
    Write-Host "❌ No backend container found. Showing all running containers..." -ForegroundColor Red
    docker ps
    exit 1
}

$containerName = $containers[0]
Write-Host "✅ Found container: $containerName" -ForegroundColor Green
Write-Host ""

# Test endpoints inside Docker container
Write-Host "🔄 Testing endpoints inside Docker container..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Health endpoint
Write-Host "1. Testing /api/v1/health" -ForegroundColor Yellow
try {
    $result = docker exec $containerName curl -s "http://localhost:8000/api/v1/health"
    $result | Select-Object -First 5
} catch {
    Write-Host "Error testing health endpoint: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: HTX Balance 
Write-Host "2. Testing /api/v1/htx/balance" -ForegroundColor Yellow
try {
    $result = docker exec $containerName curl -s "http://localhost:8000/api/v1/htx/balance"
    $result | Select-Object -First 5
} catch {
    Write-Host "Error testing balance endpoint: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: HTX Coins (the problematic endpoint)
Write-Host "3. Testing /api/v1/htx/coins" -ForegroundColor Yellow
try {
    $result = docker exec $containerName curl -s "http://localhost:8000/api/v1/htx/coins"
    if ($result) {
        Write-Host "✅ Response received:" -ForegroundColor Green
        $result | Select-Object -First 10
    } else {
        Write-Host "❌ No response received" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing coins endpoint: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Check container logs for errors
Write-Host "4. Checking recent container logs for errors" -ForegroundColor Yellow
try {
    docker logs $containerName --tail 20 | Select-String -Pattern "(error|Error|ERROR|404|500)" | Select-Object -First 5
} catch {
    Write-Host "Could not retrieve logs" -ForegroundColor Red
}
Write-Host ""

# Test 5: Check if FastAPI is properly running
Write-Host "5. Checking FastAPI server status in container" -ForegroundColor Yellow
try {
    $processes = docker exec $containerName ps aux | Select-String "python"
    $processes | Select-Object -First 3
} catch {
    Write-Host "Could not check processes" -ForegroundColor Red
}
Write-Host ""

Write-Host "🏁 Docker API testing completed!" -ForegroundColor Green