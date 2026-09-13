# ==============================================================================
# ⚡ Błyskawica & SPARKLE V10 — Environment Preparation & Tool Verification Script
# ==============================================================================

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "⚡ Błyskawica / SPARKLE V10 — Przygotowanie Środowiska Deweloperskiego" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $workspace

# 1. Weryfikacja Python
Write-Host "🔍 [1/5] Weryfikacja środowiska Python..." -ForegroundColor Cyan
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pyVersion = & python --version 2>&1
    Write-Host "✓ Wykryto Python: $pyVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️ Brak Python w PATH. Zalecana instalacja Python 3.11 lub 3.12:" -ForegroundColor Yellow
    Write-Host "   winget install Python.Python.3.12" -ForegroundColor Gray
}

# 2. Weryfikacja Rust & Cargo
Write-Host "`n🔍 [2/5] Weryfikacja kompilatora Rust (Cargo)..." -ForegroundColor Cyan
$cargoCmd = Get-Command cargo -ErrorAction SilentlyContinue
if ($cargoCmd) {
    $rustVersion = & rustc --version 2>&1
    Write-Host "✓ Wykryto Rust: $rustVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️ Brak Rust/Cargo w PATH. Wymagany do kompilacji Tauri i Candle:" -ForegroundColor Yellow
    Write-Host "   winget install Rustlang.Rustup" -ForegroundColor Gray
    Write-Host "   rustup default stable-x86_64-pc-windows-msvc" -ForegroundColor Gray
}

# 3. Weryfikacja Node.js & npm
Write-Host "`n🔍 [3/5] Weryfikacja Node.js i npm (dla Tauri CLI)..." -ForegroundColor Cyan
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if ($nodeCmd -and $npmCmd) {
    $nodeVer = & node --version 2>&1
    $npmVer = & npm --version 2>&1
    Write-Host "✓ Wykryto Node.js: $nodeVer (npm: $npmVer)" -ForegroundColor Green
} else {
    Write-Host "⚠️ Brak Node.js/npm. Wymagany do uruchomienia frontendu Tauri:" -ForegroundColor Yellow
    Write-Host "   winget install OpenJS.NodeJS.LTS" -ForegroundColor Gray
}

# 4. Przygotowanie katalogu na modele (model/)
Write-Host "`n📁 [4/5] Przygotowanie katalogu modeli offline..." -ForegroundColor Cyan
$modelDir = Join-Path $workspace "model"
if (-not (Test-Path $modelDir)) {
    New-Item -ItemType Directory -Path $modelDir -Force | Out-Null
    Write-Host "✓ Utworzono katalog: $modelDir" -ForegroundColor Green
} else {
    Write-Host "✓ Katalog modeli istnieje: $modelDir" -ForegroundColor Green
}

$ggufPath = Join-Path $modelDir "qwen2.5-1.5b-coder.gguf"
$tokPath = Join-Path $modelDir "tokenizer.json"

if ((Test-Path $ggufPath) -and (Test-Path $tokPath)) {
    Write-Host "✓ Wykryto wagi modelu GGUF i plik tokenizatora." -ForegroundColor Green
} else {
    Write-Host "ℹ️ Brak plików wag modelu w katalogu model/." -ForegroundColor Yellow
    Write-Host "   Aby pobrać domyślny model Qwen 2.5 Coder 1.5B GGUF, uruchom:" -ForegroundColor Gray
    Write-Host "   python scripts/download_qwen_model.py" -ForegroundColor Cyan
}

# 5. Podsumowanie
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "✅ Weryfikacja zakończona." -ForegroundColor Green
Write-Host "Aby uruchomić Sparkle Desktop V10 po zainstalowaniu narzędzi:" -ForegroundColor Yellow
Write-Host "   .\Uruchom_Sparkle.bat" -ForegroundColor Cyan
Write-Host "lub w trybie deweloperskim:" -ForegroundColor Yellow
Write-Host "   cd sparkle_app; npm run tauri dev" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
