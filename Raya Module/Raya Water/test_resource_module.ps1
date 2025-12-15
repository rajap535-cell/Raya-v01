# Resolve raya.exe relative to this script location
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exePath   = Join-Path $scriptDir "raya.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "ERROR: raya.exe not found at $exePath" -ForegroundColor Red
    exit 1
}

Write-Host "Running RAYA Tests..." -ForegroundColor Cyan

# ------------------------------
# TEST 1: Past Year (2000)
# ------------------------------
Write-Host "`n---- TEST 1: Past Year (2000) ----" -ForegroundColor Yellow
"2000`n9999" | & $exePath | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Test 1 Passed" -ForegroundColor Green
} else {
    Write-Host "Test 1 Failed" -ForegroundColor Red
}

# ------------------------------
# TEST 2: Future Year (2050)
# ------------------------------
Write-Host "`n---- TEST 2: Future Year (2050) ----" -ForegroundColor Yellow
"2050`n9999" | & $exePath | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Test 2 Passed" -ForegroundColor Green
} else {
    Write-Host "Test 2 Failed" -ForegroundColor Red
}

# ------------------------------
# TEST 3: Validation Mode
# ------------------------------
Write-Host "`n---- TEST 3: Validation Mode ----" -ForegroundColor Yellow
& $exePath --validation | Out-Null

$validationFile = Join-Path $scriptDir "validation_summary.csv"

if (Test-Path $validationFile) {
    Write-Host "Validation File Created: PASS" -ForegroundColor Green
} else {
    Write-Host "Validation File Not Found: FAIL" -ForegroundColor Red
}

Write-Host "`nAll tests completed."
