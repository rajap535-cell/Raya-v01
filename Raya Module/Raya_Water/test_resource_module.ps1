# Get the folder where this test script is located
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# RAYA executable is expected to be in the same folder
$exePath = Join-Path $projectRoot "raya.exe"

Write-Host "RAYA Water Module Tests" -ForegroundColor Cyan
Write-Host "Project Folder: $projectRoot" -ForegroundColor Gray
Write-Host "Executable: $exePath" -ForegroundColor Gray

# Check whether raya.exe exists
if (-not (Test-Path $exePath)) {
    Write-Host "`nraya.exe not found!" -ForegroundColor Red
    Write-Host "Expected location: $exePath" -ForegroundColor Red
    exit 1
}

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

# Run validation from the project folder
Push-Location $projectRoot

try {
    & $exePath --validation | Out-Null

    $validationFile = Join-Path $projectRoot "validation_summary.csv"

    if (Test-Path $validationFile) {
        Write-Host "Validation File Created: PASS" -ForegroundColor Green
    } else {
        Write-Host "Validation File Not Found: FAIL" -ForegroundColor Red
    }
}
finally {
    Pop-Location
}

Write-Host "`nAll tests completed." -ForegroundColor Cyan