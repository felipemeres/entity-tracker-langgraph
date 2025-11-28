# Entity Tracker - Setup Script (Windows PowerShell)
# This script sets up the entity tracker environment on Windows

Write-Host "================================================" -ForegroundColor Green
Write-Host "Entity Tracker - Setup Script" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = (python --version 2>&1 | Out-String).Trim()
if ($pythonVersion -match "Python (\d+\.\d+)") {
    $version = [version]$matches[1]
    $requiredVersion = [version]"3.11"
    
    if ($version -ge $requiredVersion) {
        Write-Host "✓ $pythonVersion detected" -ForegroundColor Green
    } else {
        Write-Host "❌ Python 3.11 or higher is required (found $pythonVersion)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Could not detect Python version" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null
Write-Host "✓ pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Set up environment file
Write-Host ""
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env and add your API keys before running the agent" -ForegroundColor Yellow
    Write-Host "   Required: OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "   Optional: TAVILY_API_KEY" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Run tests
Write-Host ""
$runTests = Read-Host "Run tests to verify installation? (y/n)"
if ($runTests -eq "y" -or $runTests -eq "Y") {
    Write-Host "Running tests..." -ForegroundColor Yellow
    pytest
    Write-Host "✓ Tests completed" -ForegroundColor Green
}

# Print next steps
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "Setup Complete! 🎉" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env and add your API keys"
Write-Host "  2. Activate the virtual environment:" -ForegroundColor Cyan
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  3. Run an example:" -ForegroundColor Cyan
Write-Host "     python examples\basic_tracking.py" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see:" -ForegroundColor Cyan
Write-Host "  - QUICKSTART.md"
Write-Host "  - README.md"
Write-Host ""
Write-Host "Happy tracking! 🎯" -ForegroundColor Green
Write-Host ""

