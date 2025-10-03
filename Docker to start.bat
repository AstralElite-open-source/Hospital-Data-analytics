@echo off
echo.
echo ===============================================
echo   Hospital Analytics Docker Launcher
echo ===============================================
echo.
echo Starting Docker containers...
echo This will build and run your PowerShell script!
echo.

REM Build and start the container in detached mode
echo Building and starting Docker container...
docker-compose up --build -d

REM Check if Docker command succeeded
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Docker failed to start!
    echo Make sure Docker Desktop is running.
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo Docker container started successfully!
echo Waiting for application to be ready...

REM Wait a few seconds for the application to start
timeout /t 10 /nobreak > nul

echo Opening browser at http://localhost:8501
start http://localhost:8501

echo.
echo Dashboard opened in your default browser!
echo Container is running in the background.
echo.
echo To stop the container, run: docker-compose down
echo To view logs, run: docker-compose logs -f
echo.
pause