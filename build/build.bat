@echo off
title Minelink Build

echo ================================
echo   Building Minelink Client
echo ================================
echo.

REM
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b
)

REM
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

REM
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [INFO] Building exe...
pyinstaller ^
  --onefile ^
  --name minelink ^
  --clean ^
  ..\client\app.py

echo.
echo [DONE] Build finished
pause
