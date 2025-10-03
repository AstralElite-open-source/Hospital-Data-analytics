# Hospital Patient Analytics - Virtual Environment Activation Script
# Quick activation script for the virtual environment

Write-Host "🚀 Activating Hospital Analytics Virtual Environment..." -ForegroundColor Yellow

# Check if virtual environment exists
if (!(Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found. Please run start.ps1 first to create it." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Virtual environment activated successfully!" -ForegroundColor Green
    Write-Host "📝 You can now run Python commands in the activated environment" -ForegroundColor Cyan
    Write-Host "📝 To deactivate, type: deactivate" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}
