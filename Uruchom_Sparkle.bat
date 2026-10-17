@echo off
title Sparkle VIBE IDE — Standalone Offline AI
echo ========================================================
echo   ⚡ BŁYSKAWICA (SPARKLE V10) — STANDALONE OFFLINE AI ⚡
echo ========================================================
cd /d "%~dp0"

:: 1. Priorytet: Dedykowany folder Standalone (Błyskawica standalone)
if exist "..\Błyskawica standalone\sparkle_app.exe" (
    echo [Wykryto natywny silnik w Błyskawica standalone] Uruchamianie...
    start "" "..\Błyskawica standalone\sparkle_app.exe"
    goto :done
)
if exist "C:\Projekty\Błyskawica standalone\sparkle_app.exe" (
    echo [Wykryto natywny silnik w Błyskawica standalone] Uruchamianie...
    start "" "C:\Projekty\Błyskawica standalone\sparkle_app.exe"
    goto :done
)

:: 2. Lokalna wersja release (repo)
if exist target\release\sparkle_app.exe (
    echo [Wykryto lokalny silnik Release] Uruchamianie Standalone Błyskawica...
    start "" target\release\sparkle_app.exe
    goto :done
)

if exist sparkle_app\src-tauri\target\release\sparkle_app.exe (
    echo [Wykryto natywny silnik Release] Uruchamianie Standalone Błyskawica...
    start "" sparkle_app\src-tauri\target\release\sparkle_app.exe
    goto :done
)

:: 2. Tryb deweloperski (jeśli brak binarki release)
echo [Brak wersji release] Uruchamianie deweloperskiej powłoki Tauri...
cd sparkle_app
start "" cmd /c "npm run tauri dev"
cd ..

:done
echo Gotowe! Błyskawica działa w natywnym oknie aplikacji.
timeout /t 2 >nul
