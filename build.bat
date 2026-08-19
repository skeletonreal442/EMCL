@echo off
chcp 65001 >nul
title EasyMCLauncher Builder

echo ==========================================
echo        EasyMCLauncher Build Script        
echo ==========================================
echo.

echo [1/3] Проверка и установка зависимостей Python...
pip install --upgrade minecraft-launcher-lib pyinstaller

echo.
echo [2/3] Сборка проекта в один .exe файл...
pyinstaller --onefile --noconfirm --name EasyMCLauncher main.py

echo.
echo [3/3] Очистка временных файлов сборки...
if exist build rmdir /s /q build
if exist EasyMCLauncher.spec del /f /q EasyMCLauncher.spec

echo.
echo ==========================================
echo   Сборка завершена! Файл EasyMCLauncher.exe
echo   находится в созданной папке \dist
echo ==========================================
pause