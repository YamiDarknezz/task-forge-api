# AXE Accessibility Test Runner for Windows
# Este script ejecuta las pruebas de accesibilidad AXE localmente

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AXE Accessibility Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Node.js
Write-Host "Verificando Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js no esta instalado" -ForegroundColor Red
    Write-Host "Descarga e instala Node.js desde: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green

# Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python no esta instalado" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Instalar dependencias NPM si es necesario
if (-Not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias de Node.js..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error instalando dependencias NPM" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "📥 Instalando navegadores de Playwright..." -ForegroundColor Yellow
    npx playwright install chromium
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error instalando navegadores" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Iniciando API Flask..." -ForegroundColor Yellow

# Activar entorno virtual si existe
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .venv\Scripts\Activate.ps1
}

# Configurar variables de entorno
$env:FLASK_ENV = "development"
$env:SECRET_KEY = "test-secret-key-for-local-axe"
$env:JWT_SECRET_KEY = "test-jwt-secret-key-for-local-axe"

# Iniciar Flask en background
$flaskProcess = Start-Process python -ArgumentList "run.py" -PassThru -WindowStyle Hidden

Write-Host "⏳ Esperando a que la API este lista (15 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar que la API este corriendo
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ API esta corriendo en http://localhost:5000" -ForegroundColor Green
} catch {
    Write-Host "❌ No se pudo conectar a la API" -ForegroundColor Red
    Stop-Process -Id $flaskProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""
Write-Host "🔍 Ejecutando pruebas de accesibilidad AXE..." -ForegroundColor Cyan
Write-Host ""

# Ejecutar pruebas AXE
node tests\accessibility\axe-swagger-test.js
$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "🛑 Deteniendo API Flask..." -ForegroundColor Yellow
Stop-Process -Id $flaskProcess.Id -Force -ErrorAction SilentlyContinue

if ($exitCode -eq 0) {
    Write-Host "✅ Pruebas completadas exitosamente!" -ForegroundColor Green
    
    # Buscar el reporte mas reciente
    $reportFile = Get-ChildItem -Path "tests\accessibility\axe-report-*.html" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($reportFile) {
        Write-Host ""
        Write-Host "📊 Abriendo reporte en navegador..." -ForegroundColor Cyan
        Start-Process $reportFile.FullName
    }
} else {
    Write-Host "❌ Las pruebas fallaron. Revisa el reporte para mas detalles." -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Pruebas finalizadas" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

exit $exitCode
