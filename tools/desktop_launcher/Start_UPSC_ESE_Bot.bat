@echo off
title UPSC ESE (Mechanical) Local Bot
cd /d "c:\Users\brred\Desktop\AI_Assistant\App\backend"
"C:\Python313\python.exe" "c:\Users\brred\Desktop\AI_Assistant\App\backend\UPSC_ESE_Bot.py"
if errorlevel 1 (
    echo.
    echo Something went wrong starting the bot.
    pause
)
