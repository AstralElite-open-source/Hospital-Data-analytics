@echo off
REM Hospital Analytics - Docker Build and Push Script (Windows)
REM Usage: build-and-push.bat [version]

setlocal EnableDelayedExpansion

REM Configuration
set REGISTRY=ghcr.io
set REPOSITORY=astralelite-open-source/hospital-data-analytics
set IMAGE_NAME=%REGISTRY%/%REPOSITORY%

REM Get version from parameter or use 'latest'
if "%1"=="" (
    set VERSION=latest
) else (
    set VERSION=%1
)

echo 🏥 Building Hospital Analytics Container
echo ========================================
echo Registry: %REGISTRY%
echo Repository: %REPOSITORY%
echo Version: %VERSION%
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Build the container
echo 🔨 Building container...
docker build -t "%IMAGE_NAME%:%VERSION%" .
if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

REM Tag as latest if version is not latest
if not "%VERSION%"=="latest" (
    echo 🏷️ Tagging as latest...
    docker tag "%IMAGE_NAME%:%VERSION%" "%IMAGE_NAME%:latest"
)

REM Ask for confirmation to push
echo.
set /p PUSH_CONFIRM="🚀 Do you want to push to %REGISTRY%? (y/N): "

if /i "%PUSH_CONFIRM%"=="y" (
    echo 📤 Pushing to registry...
    
    REM Push the images
    docker push "%IMAGE_NAME%:%VERSION%"
    if errorlevel 1 (
        echo ❌ Push failed! Make sure you're logged in with: docker login %REGISTRY%
        pause
        exit /b 1
    )
    
    if not "%VERSION%"=="latest" (
        docker push "%IMAGE_NAME%:latest"
    )
    
    echo ✅ Successfully pushed to %REGISTRY%!
    echo.
    echo 🎉 Your container is now available at:
    echo    %IMAGE_NAME%:%VERSION%
    echo.
    echo 🚀 To run your container:
    echo    docker run -p 8501:8501 %IMAGE_NAME%:%VERSION%
    echo.
    echo 🌐 Access your application at: http://localhost:8501
) else (
    echo ⏹️ Push cancelled. Container built locally as:
    echo    %IMAGE_NAME%:%VERSION%
    echo.
    echo 🚀 To run locally:
    echo    docker run -p 8501:8501 %IMAGE_NAME%:%VERSION%
)

echo.
echo ✨ Build process completed!
pause