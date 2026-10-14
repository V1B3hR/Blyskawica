@echo off
title Sparkle VIBE IDE — Standalone Offline AI
echo ========================================================
echo   ⚡ BŁYSKAWICA (SPARKLE V10) — STANDALONE OFFLINE AI ⚡
echo ========================================================
cd /d "%~dp0"

:: 1. Priorytet: Natywna wersja Standalone (Rust + Tauri v2 + Candle)
if exist target\release\sparkle_app.exe (
    echo [Wykryto natywny silnik Release] Uruchamianie Standalone Błyskawica...
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
