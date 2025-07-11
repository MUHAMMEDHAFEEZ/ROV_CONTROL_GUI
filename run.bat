@echo off
chcp 65001 >nul
title ROV Control System Setup

echo.
echo ========================================
echo    ROV Control System Setup
echo ========================================
echo.

echo This script will check your system and install the necessary requirements for the ROV Control System.
echo Checking system and installing requirements...
python setup.py

echo.
echo Do you want to start the app now? (y/n)
set /p choice="Choose (y/n): "

if /i "%choice%"=="y" (
    echo.
    echo Start ROV Control System...
    python main.py
) else (
    echo.
    echo you can start the app later by running:
    echo python main.py
)

echo.
echo Click any key to exit...
pause >nul
