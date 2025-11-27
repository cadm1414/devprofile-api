# =============================================================================
# SCRIPT DE DEPLOYMENT SUPER SIMPLE PARA AWS
# =============================================================================
# Este script hace todo el proceso automáticamente
# Solo necesitas responder 1 pregunta: Tu IP pública
# =============================================================================

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   DevProfile API - Deployment Automático a AWS               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# =============================================================================
# Verificar pre-requisitos
# =============================================================================
Write-Host "🔍 Verificando pre-requisitos..." -ForegroundColor Yellow

# Verificar AWS CLI
if (!(Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI no está instalado" -ForegroundColor Red
    Write-Host "   Instalar con: choco install awscli" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ AWS CLI instalado" -ForegroundColor Green

# Verificar configuración AWS
try {
    $awsIdentity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ AWS CLI no está configurado" -ForegroundColor Red
        Write-Host "   Configurar con: aws configure" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ AWS CLI configurado" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al verificar AWS CLI" -ForegroundColor Red
    exit 1
}

# Verificar Terraform
if (!(Get-Command terraform -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Terraform no está instalado" -ForegroundColor Red
    Write-Host "   Instalar con: choco install terraform" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Terraform instalado" -ForegroundColor Green

# Verificar Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker no está instalado" -ForegroundColor Red
    Write-Host "   Instalar Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker instalado" -ForegroundColor Green

Write-Host "`n"

# =============================================================================
# Obtener información necesaria
# =============================================================================
Write-Host "📝 Configuración del deployment" -ForegroundColor Yellow
Write-Host "───────────────────────────────────────────────────────" -ForegroundColor DarkGray

# Obtener IP pública
Write-Host "`n🌐 Obteniendo tu IP pública..." -ForegroundColor Cyan
$myIP = (Invoke-WebRequest -Uri "http://ifconfig.me/ip" -UseBasicParsing).Content.Trim()
Write-Host "   Tu IP: $myIP" -ForegroundColor Green

$confirmIP = Read-Host "`n¿Es correcta esta IP? (s/n)"
if ($confirmIP -ne "s") {
    $myIP = Read-Host "Ingresa tu IP pública"
}

# Generar passwords seguros
Write-Host "`n🔐 Generando credenciales seguras..." -ForegroundColor Cyan

# Password de PostgreSQL
$dbPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 24 | ForEach-Object {[char]$_})
Write-Host "   DB Password: $dbPassword" -ForegroundColor Green

# Secret Key para JWT
$apiSecretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "   API Secret: $apiSecretKey" -ForegroundColor Green

Write-Host "`n⚠️  IMPORTANTE: Guarda estas credenciales en un lugar seguro!" -ForegroundColor Yellow
Write-Host "`n"
Read-Host "Presiona Enter para continuar"

# =============================================================================
# Preparar archivos de Terraform
# =============================================================================
Write-Host "`n📦 Preparando configuración de Terraform..." -ForegroundColor Yellow

Set-Location terraform

# Usar archivos simplificados
Copy-Item main-simple.tf main.tf -Force
Copy-Item variables-simple.tf variables.tf -Force

# Crear terraform.tfvars
$tfvarsContent = @"
# Generado automáticamente por deploy-simple.ps1
# Fecha: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

allowed_ssh_cidr = ["$myIP/32"]
db_password = "$dbPassword"
api_secret_key = "$apiSecretKey"

# Valores por defecto
aws_region = "us-east-1"
db_name = "devprofile_db"
db_user = "devprofile_user"
ami_id = "ami-0c02fb55b5c460776"
"@

$tfvarsContent | Out-File -FilePath terraform.tfvars -Encoding UTF8
Write-Host "✅ terraform.tfvars creado" -ForegroundColor Green

# =============================================================================
# Inicializar Terraform
# =============================================================================
Write-Host "`n🚀 Inicializando Terraform..." -ForegroundColor Yellow
terraform init

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al inicializar Terraform" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Terraform inicializado" -ForegroundColor Green

# =============================================================================
# Mostrar plan
# =============================================================================
Write-Host "`n📋 Plan de deployment:" -ForegroundColor Yellow
terraform plan

Write-Host "`n"
$confirm = Read-Host "¿Continuar con el deployment? (s/n)"
if ($confirm -ne "s") {
    Write-Host "❌ Deployment cancelado" -ForegroundColor Red
    exit 0
}

# =============================================================================
# Aplicar Terraform
# =============================================================================
Write-Host "`n🚀 Desplegando infraestructura en AWS..." -ForegroundColor Yellow
Write-Host "   ⏱️  Esto tomará 3-5 minutos..." -ForegroundColor Cyan
Write-Host "`n"

terraform apply -auto-approve

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al desplegar infraestructura" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Infraestructura desplegada exitosamente!" -ForegroundColor Green

# =============================================================================
# Obtener información de la instancia
# =============================================================================
$publicIP = terraform output -raw public_ip
$sshCommand = terraform output -raw ssh_command

Write-Host "`n"
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   INFRAESTRUCTURA DESPLEGADA                                  ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host "`n"
Write-Host "🌐 IP Pública: $publicIP" -ForegroundColor Cyan
Write-Host "🔗 API URL: http://$publicIP" -ForegroundColor Cyan
Write-Host "📚 Docs: http://$publicIP/docs" -ForegroundColor Cyan
Write-Host "🔑 SSH: $sshCommand" -ForegroundColor Cyan
Write-Host "`n"

# =============================================================================
# Esperar inicialización de EC2
# =============================================================================
Write-Host "⏱️  Esperando inicialización de EC2 (5-10 minutos)..." -ForegroundColor Yellow
Write-Host "   Puedes monitorear el progreso en otra terminal con:" -ForegroundColor DarkGray
Write-Host "   $sshCommand" -ForegroundColor DarkGray
Write-Host "   tail -f /var/log/user-data.log" -ForegroundColor DarkGray
Write-Host "`n"

Start-Sleep -Seconds 30

Write-Host "🔍 Verificando si EC2 está lista..." -ForegroundColor Yellow
$ready = $false
$attempts = 0
$maxAttempts = 20

while (-not $ready -and $attempts -lt $maxAttempts) {
    $attempts++
    Write-Host "   Intento $attempts/$maxAttempts..." -ForegroundColor DarkGray
    
    try {
        $result = ssh -i devprofile-aws-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=10 ubuntu@$publicIP "test -f /var/log/cloud-init-output.log && echo 'ready'" 2>$null
        if ($result -eq "ready") {
            $ready = $true
            Write-Host "✅ EC2 está lista!" -ForegroundColor Green
            break
        }
    } catch {
        # Continuar intentando
    }
    
    Start-Sleep -Seconds 15
}

if (-not $ready) {
    Write-Host "⚠️  No se pudo verificar automáticamente el estado" -ForegroundColor Yellow
    Write-Host "   Continúa manualmente siguiendo las instrucciones en DEPLOY_SIMPLE.md" -ForegroundColor Yellow
}

# =============================================================================
# Resumen final
# =============================================================================
Write-Host "`n"
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   PRÓXIMOS PASOS                                              ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"
Write-Host "1️⃣  Espera a que termine la inicialización de EC2 (~10 min)" -ForegroundColor White
Write-Host "   Monitorear: $sshCommand" -ForegroundColor DarkGray
Write-Host "   Luego: tail -f /var/log/user-data.log" -ForegroundColor DarkGray
Write-Host "`n"
Write-Host "2️⃣  Build y deploy de la aplicación (ver DEPLOY_SIMPLE.md paso 'Desplegar la aplicación')" -ForegroundColor White
Write-Host "`n"
Write-Host "3️⃣  Abrir en navegador: http://$publicIP/docs" -ForegroundColor White
Write-Host "`n"
Write-Host "💾 Credenciales guardadas en: terraform/terraform.tfvars" -ForegroundColor Yellow
Write-Host "💰 Costo estimado: ~`$5/mes (~`$30 por 6 meses)" -ForegroundColor Green
Write-Host "`n"

# Abrir documentación
$openDocs = Read-Host "¿Abrir la API en el navegador? (s/n)"
if ($openDocs -eq "s") {
    Start-Process "http://$publicIP/docs"
}

Write-Host "`n🎉 ¡Deployment completado!" -ForegroundColor Green
Write-Host "`n"
