# Quick Start Script for AI Code Remediation Microservice
# This script helps set up and run the service

Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "AI CODE REMEDIATION MICROSERVICE - QUICK START" -ForegroundColor Cyan
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/6] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.([0-9]+)") {
    $minorVersion = [int]$matches[1]
    if ($minorVersion -ge 10) {
        Write-Host "✓ Python version OK: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "✗ Python 3.10+ required. Found: $pythonVersion" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Python not found or version check failed" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/6] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[4/6] Installing dependencies (this may take 5-10 minutes)..." -ForegroundColor Yellow
pip install --upgrade pip | Out-Null
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Create necessary directories
Write-Host ""
Write-Host "[5/6] Verifying project structure..." -ForegroundColor Yellow
$directories = @("app", "app/rag", "app/rag/recipes", "app/utils")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
}
Write-Host "✓ Project structure verified" -ForegroundColor Green

# Display next steps
Write-Host ""
Write-Host "[6/6] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the service:" -ForegroundColor Yellow
Write-Host "   uvicorn app.main:app --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "2. In a new terminal, run tests:" -ForegroundColor Yellow
Write-Host "   python test_local.py" -ForegroundColor White
Write-Host ""
Write-Host "3. Access API documentation:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "===========================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to start the service now, or Ctrl+C to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Starting AI Code Remediation Microservice..." -ForegroundColor Yellow
Write-Host ""
uvicorn app.main:app --host 0.0.0.0 --port 8000
