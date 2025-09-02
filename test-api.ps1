# PowerShell script for testing API endpoints
# Replacement for Linux commands like curl | head

param(
    [string]$Url,
    [int]$Lines = 20
)

function Test-Api {
    param(
        [string]$ApiUrl,
        [int]$MaxLines = 20
    )
    
    try {
        Write-Host "🔄 Testing endpoint: $ApiUrl" -ForegroundColor Cyan
        
        # Use Invoke-RestMethod for better JSON handling
        $response = Invoke-RestMethod -Uri $ApiUrl -Method GET -TimeoutSec 30
        
        # Convert to JSON with nice formatting
        $jsonOutput = $response | ConvertTo-Json -Depth 10
        
        # Split into lines and take first N lines
        $lines = $jsonOutput -split "`n"
        if ($lines.Count -gt $MaxLines) {
            $lines[0..($MaxLines-1)] | ForEach-Object { Write-Host $_ }
            Write-Host "... (showing first $MaxLines lines of $($lines.Count) total)" -ForegroundColor Yellow
        } else {
            $lines | ForEach-Object { Write-Host $_ }
        }
        
        Write-Host "✅ Success: $($lines.Count) lines total" -ForegroundColor Green
        
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Try with curl as fallback
        Write-Host "🔄 Trying with curl..." -ForegroundColor Yellow
        try {
            $curlResult = & curl $ApiUrl 2>$null
            if ($curlResult) {
                $curlResult | Select-Object -First $MaxLines
            }
        } catch {
            Write-Host "❌ Curl also failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Main execution
if ($Url) {
    Test-Api -ApiUrl $Url -MaxLines $Lines
} else {
    Write-Host "🚀 HTX API Testing Tool" -ForegroundColor Green
    Write-Host "Usage: .\test-api.ps1 -Url 'http://localhost:8000/api/v1/health' -Lines 20"
    Write-Host ""
    Write-Host "Testing common endpoints:" -ForegroundColor Cyan
    
    $endpoints = @(
        "http://localhost:8000/api/v1/health",
        "http://localhost:8000/api/v1/htx/balance", 
        "http://localhost:8000/api/v1/htx/trades",
        "http://localhost:8000/api/v1/htx/coins",
        "http://localhost:8000/"
    )
    
    foreach ($endpoint in $endpoints) {
        Write-Host "`n--- Testing: $endpoint ---" -ForegroundColor Cyan
        Test-Api -ApiUrl $endpoint -MaxLines 10
        Start-Sleep -Seconds 1
    }
}