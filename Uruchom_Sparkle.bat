@echo off
title Uruchamianie Sparkle VIBE IDE...
echo ===================================================
echo   Uruchamianie srodowiska Sparkle dla Blyskawicy V8
echo ===================================================
cd /d "%~dp0"

:: Generowanie bezpiecznego tokenu sesji przy uzyciu PowerShell
for /f "delims=" %%i in ('powershell -NoProfile -Command "[guid]::NewGuid().ToString('N')"') do set "SPARKLE_TOKEN=%%i"
set "X_BLY_TOKEN=%SPARKLE_TOKEN%"

:: Sprawdzenie czy uzywany jest venv_orbital
if exist venv_orbital\Scripts\python.exe (
    echo [Wykryto venv_orbital] Uruchamianie backendu z wirtualnego srodowiska...
    start "" /B venv_orbital\Scripts\python.exe blyskawica_app\backend\main.py
) else (
    echo [Brak venv_orbital] Uruchamianie backendu z globalnego interpretera python...
    start "" /B python blyskawica_app\backend\main.py
)

echo Oczekiwanie na start serwera API (3 sekundy)...
timeout /t 3 /nobreak >nul

echo Otwieranie natywnej powloki Sparkle VIBE IDE (Tauri)...
if exist sparkle_app\src-tauri\target\release\sparkle_app.exe (
    echo [Wykryto wersje produkcyjna] Uruchamianie powloki Tauri...
    start "" sparkle_app\src-tauri\target\release\sparkle_app.exe
) else (
    echo [Brak wersji produkcyjnej] Uruchamianie deweloperskiej powloki Tauri - tauri dev...
    cd sparkle_app
    start "" cmd /c "npm run tauri dev"
    cd ..
)

echo Gotowe! Mozesz zamknac to okno (procesy dzialaja w tle).
timeout /t 3 >nul
