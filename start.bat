@echo off
setlocal
title OpenLMS Server
echo ===============================================================
echo Starting OpenLMS (Python Flask)
echo ===============================================================

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your PATH. Please install Python 3.10+
    pause
    exit /b 1
)

python run.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] OpenLMS exited with an error.
    pause
)
