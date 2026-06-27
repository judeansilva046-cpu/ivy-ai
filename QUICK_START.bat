@echo off
REM Jarvis AI Quick Start Script (Windows)
REM This script helps you get started with Jarvis AI Backend

echo.
echo ================================================================================
echo                  JARVIS AI - QUICK START HELPER
echo ================================================================================
echo.

REM Check if we're in the right directory
if not exist "server\venv" (
    echo Error: venv not found in server directory!
    echo Please run this script from C:\JarvisAI
    echo.
    pause
    exit /b 1
)

REM Display menu
:menu
echo.
echo Select an option:
echo.
echo 1. Start the API server
echo 2. Ingest documents
echo 3. Open Swagger UI in browser
echo 4. Show health status
echo 5. Run chat example
echo 6. View logs
echo 7. Setup .env file
echo 8. Exit
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto start_server
if "%choice%"=="2" goto ingest
if "%choice%"=="3" goto swagger
if "%choice%"=="4" goto health
if "%choice%"=="5" goto chat
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto setup_env
if "%choice%"=="8" goto end

echo Invalid choice. Please try again.
goto menu

:start_server
echo.
echo Starting Jarvis AI API Server...
echo.
cd server
call venv\Scripts\activate.bat
echo.
echo Starting uvicorn on http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
pause
cd ..
goto menu

:ingest
echo.
echo Ingesting documents...
echo.
cd server
call venv\Scripts\activate.bat
echo.
python ingest/ingest_documents.py
echo.
pause
cd ..
goto menu

:swagger
echo.
echo Opening Swagger UI...
echo.
start http://127.0.0.1:8000/docs
goto menu

:health
echo.
echo Checking server health...
echo.
powershell -Command "(Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health').Content" 2>nul
if errorlevel 1 (
    echo.
    echo Server is not running. Start it first with option 1.
)
echo.
pause
goto menu

:chat
echo.
echo Testing chat endpoint...
echo.
powershell -Command @"
try {
    `$body = @{
        query = 'O que e Jarvis AI?'
        session_id = 'test_user'
    } | ConvertTo-Json

    `$response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/chat/' `
        -Method POST `
        -Body `$body `
        -ContentType 'application/json' `
        -ErrorAction Stop

    `$json = `$response.Content | ConvertFrom-Json
    Write-Host "Response:" -ForegroundColor Green
    Write-Host `$json.response
} catch {
    Write-Host "Error: Server is not running. Start it first with option 1." -ForegroundColor Red
}
"@
echo.
pause
goto menu

:logs
echo.
echo Recent logs:
echo.
cd server
if exist "logs\jarvis_ai.log" (
    powershell -Command "Get-Content logs/jarvis_ai.log -Tail 20"
) else (
    echo No logs found yet. Run the server first.
)
echo.
pause
cd ..
goto menu

:setup_env
echo.
echo Setting up .env file...
echo.
cd server
if exist ".env" (
    echo .env file already exists. Opening for editing...
    notepad .env
) else (
    echo Creating .env from template...
    copy .env.example .env
    echo .env file created! Opening for editing...
    echo Please add your OPENAI_API_KEY
    notepad .env
)
echo.
pause
cd ..
goto menu

:end
echo.
echo Thank you for using Jarvis AI!
echo.
echo For more information, see:
echo - C:\JarvisAI\GETTING_STARTED.md
echo - C:\JarvisAI\server\README.md
echo.
pause
exit /b 0
