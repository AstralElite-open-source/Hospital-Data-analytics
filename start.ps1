# Hospital Patient Analytics - Setup and Run Script
# This script creates a virtual environment, installs requirements, runs analysis, and starts the dashboard

Write-Host "🏥 Hospital Patient Analytics - Setup and Run" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10 first." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`n📦 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists." -ForegroundColor Yellow
}

python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Virtual environment created" -ForegroundColor Green

# Activate virtual environment
Write-Host "`n🚀 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Upgrade pip
Write-Host "`n⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✅ Pip upgraded" -ForegroundColor Green

# Install requirements
Write-Host "`n📥 Installing requirements..." -ForegroundColor Yellow
pip install -r requirements_simple.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install requirements" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Requirements installed successfully" -ForegroundColor Green

# Run system test
Write-Host "`n🧪 Running system tests..." -ForegroundColor Yellow
python test_system.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ System tests failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ All tests passed" -ForegroundColor Green

# Run analysis
Write-Host "`n📊 Running comprehensive analysis..." -ForegroundColor Yellow
python run_demo.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Analysis completed with warnings, but continuing..." -ForegroundColor Yellow
}
Write-Host "✅ Analysis completed" -ForegroundColor Green

# Create exports directory if it doesn't exist
Write-Host "`n📁 Creating exports directory..." -ForegroundColor Yellow
if (!(Test-Path "exports")) {
    New-Item -ItemType Directory -Path "exports" | Out-Null
}
if (!(Test-Path "exports/charts")) {
    New-Item -ItemType Directory -Path "exports/charts" | Out-Null
}
if (!(Test-Path "exports/reports")) {
    New-Item -ItemType Directory -Path "exports/reports" | Out-Null
}
Write-Host "✅ Exports directory ready" -ForegroundColor Green

# Start Streamlit dashboard
Write-Host "`n🌐 Starting Streamlit dashboard..." -ForegroundColor Yellow
Write-Host "📝 The dashboard will open in your default web browser" -ForegroundColor Cyan
Write-Host "📝 URL: http://localhost:8501" -ForegroundColor Cyan
Write-Host "📝 Press Ctrl+C to stop the dashboard" -ForegroundColor Cyan
Write-Host "`n🚀 Launching dashboard..." -ForegroundColor Green

# Run Streamlit
streamlit run dashboard/app.py

Write-Host "`n👋 Dashboard stopped. Thank you for using Hospital Patient Analytics!" -ForegroundColor Cyan
