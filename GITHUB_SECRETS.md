# Configuración de GitHub Secrets para CI/CD

## 📋 Secrets Requeridos

Para que los workflows de GitHub Actions funcionen correctamente, debes configurar los siguientes secrets en tu repositorio:

### 🔐 Cómo agregar secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Click en **Settings** > **Secrets and variables** > **Actions**
3. Click en **New repository secret**
4. Agrega cada uno de los secrets listados abajo

---

## 🧪 Secrets para Testing (test.yml, newman-test.yml)

### `DATABASE_URL`
- **Descripción:** URL de conexión a PostgreSQL para testing
- **Formato:** `postgresql://username:password@localhost:5432/database_name`
- **Ejemplo:** `postgresql://test_user:test_pass@localhost:5432/test_db`

### `SECRET_KEY`
- **Descripción:** Clave secreta para JWT tokens
- **Generar con:** 
  ```bash
  # Linux/Mac
  openssl rand -base64 32
  
  # PowerShell
  $bytes = New-Object Byte[] 32
  [Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
  [Convert]::ToBase64String($bytes)
  ```
- **Ejemplo:** `dGhpc2lzYXN1cGVyc2VjcmV0a2V5Zm9yand0dG9rZW5z`

---

## 🚀 Secrets para Deployment AWS (deploy-aws.yml)

### `EC2_HOST`
- **Descripción:** IP pública o DNS de tu instancia EC2
- **Obtener con:**
  ```bash
  terraform output -raw instance_public_ip
  ```
- **Ejemplo:** `54.123.45.67` o `ec2-54-123-45-67.compute-1.amazonaws.com`

### `EC2_SSH_KEY`
- **Descripción:** Clave privada SSH completa para conectar a EC2
- **Obtener:** Contenido del archivo `~/.ssh/devprofile-aws` (generado con terraform)
- **Formato:** 
  ```
  -----BEGIN RSA PRIVATE KEY-----
  MIIEpAIBAAKCAQEA...
  ... (múltiples líneas)
  -----END RSA PRIVATE KEY-----
  ```
- **⚠️ IMPORTANTE:** Copia TODO el contenido incluyendo las líneas BEGIN y END

### `DB_NAME`
- **Descripción:** Nombre de la base de datos PostgreSQL
- **Debe coincidir con:** Valor en `terraform/terraform.tfvars`
- **Ejemplo:** `devprofile_db`

### `DB_USER`
- **Descripción:** Usuario de PostgreSQL
- **Debe coincidir con:** Valor en `terraform/terraform.tfvars`
- **Ejemplo:** `devprofile_user`

### `DB_PASSWORD`
- **Descripción:** Contraseña de PostgreSQL
- **Debe coincidir con:** Valor en `terraform/terraform.tfvars`
- **Generar con:**
  ```bash
  # Linux/Mac
  openssl rand -base64 24
  
  # PowerShell
  -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 24 | ForEach-Object {[char]$_})
  ```

### `API_SECRET_KEY`
- **Descripción:** Secret key para la API en producción
- **Debe coincidir con:** Valor en `terraform/terraform.tfvars`
- **Generar con:** Igual que `SECRET_KEY` (ver arriba)

---

## 📝 Script para Configurar Secrets Rápidamente

### Bash/Linux/Mac
```bash
#!/bin/bash

# GitHub CLI debe estar instalado: brew install gh
# Autenticar primero: gh auth login

REPO="tu-usuario/devprofile-api"  # ⚠️ CAMBIAR

# Testing secrets
gh secret set DATABASE_URL --body "postgresql://test:test@localhost:5432/test_db" -R $REPO
gh secret set SECRET_KEY --body "$(openssl rand -base64 32)" -R $REPO

# Deployment secrets (después de terraform apply)
gh secret set EC2_HOST --body "$(cd terraform && terraform output -raw instance_public_ip)" -R $REPO
gh secret set EC2_SSH_KEY --body "$(cat ~/.ssh/devprofile-aws)" -R $REPO
gh secret set DB_NAME --body "$(cd terraform && terraform output -raw db_name)" -R $REPO
gh secret set DB_USER --body "$(cd terraform && terraform output -raw db_user)" -R $REPO
gh secret set DB_PASSWORD --body "TU_PASSWORD_AQUI" -R $REPO  # ⚠️ CAMBIAR
gh secret set API_SECRET_KEY --body "$(openssl rand -base64 32)" -R $REPO

echo "✅ Todos los secrets configurados!"
```

### PowerShell/Windows
```powershell
# GitHub CLI debe estar instalado: choco install gh
# Autenticar primero: gh auth login

$REPO = "tu-usuario/devprofile-api"  # ⚠️ CAMBIAR

# Testing secrets
gh secret set DATABASE_URL --body "postgresql://test:test@localhost:5432/test_db" -R $REPO

$bytes = New-Object Byte[] 32
[Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
$secretKey = [Convert]::ToBase64String($bytes)
gh secret set SECRET_KEY --body $secretKey -R $REPO

# Deployment secrets (después de terraform apply)
cd terraform
$ec2Host = terraform output -raw instance_public_ip
cd ..
gh secret set EC2_HOST --body $ec2Host -R $REPO

$sshKey = Get-Content ~/.ssh/devprofile-aws -Raw
gh secret set EC2_SSH_KEY --body $sshKey -R $REPO

gh secret set DB_NAME --body "devprofile_db" -R $REPO
gh secret set DB_USER --body "devprofile_user" -R $REPO
gh secret set DB_PASSWORD --body "TU_PASSWORD_AQUI" -R $REPO  # ⚠️ CAMBIAR

$apiKey = [Convert]::ToBase64String((New-Object Byte[] 32))
gh secret set API_SECRET_KEY --body $apiKey -R $REPO

Write-Host "✅ Todos los secrets configurados!"
```

---

## ✅ Verificar Secrets Configurados

```bash
# Listar todos los secrets (no muestra valores)
gh secret list -R tu-usuario/devprofile-api

# Debería mostrar:
# - DATABASE_URL
# - SECRET_KEY
# - EC2_HOST
# - EC2_SSH_KEY
# - DB_NAME
# - DB_USER
# - DB_PASSWORD
# - API_SECRET_KEY
```

---

## 🔒 Seguridad

### ⚠️ NUNCA hagas lo siguiente:
- ❌ Commitear secrets en el código
- ❌ Poner secrets en archivos `.env` en el repo
- ❌ Compartir secrets por chat/email
- ❌ Usar passwords débiles o obvios

### ✅ Buenas prácticas:
- ✅ Usar GitHub Secrets para valores sensibles
- ✅ Generar passwords aleatorios fuertes
- ✅ Rotar secrets periódicamente
- ✅ Usar diferentes secrets para dev/staging/prod
- ✅ Limitar acceso a secrets solo a quien los necesita

---

## 🔄 Rotar Secrets

Si necesitas cambiar algún secret:

1. **Genera nuevo valor:**
   ```bash
   openssl rand -base64 32
   ```

2. **Actualiza en GitHub:**
   ```bash
   gh secret set SECRET_KEY --body "nuevo_valor" -R tu-usuario/devprofile-api
   ```

3. **Actualiza en EC2 (si es DB o API secret):**
   ```bash
   ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_HOST
   cd ~/devprofile-api
   nano .env  # Editar valores
   docker-compose restart
   ```

---

## 🆘 Troubleshooting

### Error: "Secret not found"
- Verifica que el nombre del secret coincide exactamente (case-sensitive)
- Revisa que estés en el repositorio correcto

### Workflow falla con "Permission denied"
- El secret `EC2_SSH_KEY` debe incluir las líneas BEGIN/END
- Verificar permisos del archivo SSH: `chmod 600 ~/.ssh/devprofile-aws`

### Error de conexión a base de datos
- Verificar formato de `DATABASE_URL`
- Asegurar que PostgreSQL está corriendo en EC2

---

## 📚 Referencias

- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [OpenSSL Random](https://www.openssl.org/docs/man1.1.1/man1/rand.html)

---

**Próximos Pasos:**
1. ✅ Configurar todos los secrets listados arriba
2. ✅ Ejecutar `terraform apply` para crear infraestructura
3. ✅ Hacer push a `main` branch para trigger deployment automático
4. ✅ Verificar workflow en GitHub Actions tab

---

**Autor:** Carlos Alberto Diaz Minaya  
**Fecha:** Noviembre 2025  
**Versión:** 1.0
