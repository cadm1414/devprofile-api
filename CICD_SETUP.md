# 🚀 Configuración de CI/CD con GitHub Actions

## 📋 Requisitos Previos

1. Infraestructura AWS desplegada con Terraform
2. Servidor EC2 corriendo con Docker y PostgreSQL
3. Acceso a GitHub Repository Settings

---

## 🔐 Configuración de GitHub Secrets

Ve a tu repositorio en GitHub:
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Secrets Requeridos:

| Secret Name | Descripción | Dónde obtenerlo |
|------------|-------------|-----------------|
| `EC2_HOST` | IP pública de tu EC2 | Output de Terraform: `terraform output public_ip` |
| `EC2_SSH_KEY` | Clave privada SSH | Archivo `terraform/devprofile-aws-key.pem` |
| `DB_NAME` | Nombre de la base de datos | Configurado en `terraform.tfvars` |
| `DB_USER` | Usuario de PostgreSQL | Configurado en `terraform.tfvars` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | Configurado en `terraform.tfvars` |
| `SECRET_KEY` | Secret key para JWT | Configurado en `terraform.tfvars` (api_secret_key) |

---

## 📝 Cómo copiar la SSH Key

### En PowerShell (Windows):
```powershell
Get-Content terraform\devprofile-aws-key.pem | Set-Clipboard
```

### En Linux/Mac:
```bash
cat terraform/devprofile-aws-key.pem | pbcopy  # Mac
cat terraform/devprofile-aws-key.pem | xclip    # Linux
```

⚠️ **Importante**: Copia todo el contenido incluyendo:
```
-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
```

---

## ✅ Verificar Secrets Configurados

Una vez configurados todos los secrets, verifica que estén bien:

1. Ve a **Settings** → **Secrets and variables** → **Actions**
2. Deberías ver 6 secrets listados (sin poder ver sus valores)

---

## 🔄 Proceso de Deployment Automático

### Trigger Automático:
El workflow se ejecuta automáticamente cuando haces push a:
- ✅ `main` branch
- ✅ `production` branch

### Trigger Manual:
También puedes ejecutarlo manualmente:
1. Ve a **Actions** tab
2. Selecciona "Deploy to AWS EC2"
3. Click en "Run workflow"
4. Selecciona la rama
5. Click en "Run workflow"

---

## 📊 Monitorear el Deployment

### Durante el Deployment:
1. Ve a **Actions** tab en GitHub
2. Click en el workflow que se está ejecutando
3. Verás 4 jobs principales:
   - 📦 **Build Docker image**
   - 🚀 **Copy files to EC2**
   - 🔄 **Deploy on EC2**
   - ✅ **Verify deployment**

### Después del Deployment:
Verifica que tu API está funcionando:

```bash
# Health check
curl http://TU_IP_EC2/health

# API Docs
curl http://TU_IP_EC2/docs
```

---

## 🧪 Probar el CI/CD

### 1. Hacer un cambio en tu código:
```bash
# Edita algún archivo
git add .
git commit -m "Test CI/CD deployment"
git push origin feature/aws-deployment
```

### 2. Merge a main:
```bash
git checkout main
git merge feature/aws-deployment
git push origin main
```

### 3. Ver el deployment:
- El workflow se ejecutará automáticamente
- GitHub Actions hará:
  1. Build de la imagen Docker
  2. Copia de archivos al servidor
  3. Deploy con docker-compose
  4. Verificación de health check

---

## 🐛 Troubleshooting

### ❌ Error: "Permission denied (publickey)"
**Solución**: Verifica que copiaste toda la SSH key correctamente en `EC2_SSH_KEY`

### ❌ Error: "Health check failed"
**Solución**: 
1. SSH al servidor: `ssh -i terraform/devprofile-aws-key.pem ubuntu@TU_IP`
2. Ver logs: `cd /home/ubuntu/devprofile-api && docker-compose logs`

### ❌ Error: "Database connection failed"
**Solución**: Verifica que los secrets `DB_NAME`, `DB_USER`, `DB_PASSWORD` sean correctos

---

## 📁 Archivos de CI/CD

| Archivo | Descripción |
|---------|-------------|
| `.github/workflows/deploy-aws.yml` | Workflow principal de deployment |
| `.github/workflows/test.yml` | Tests automáticos (opcional) |
| `docker-compose.yml` | Configuración de servicios |
| `Dockerfile` | Build de la imagen |

---

## 🔒 Seguridad

### ✅ Buenas prácticas implementadas:
- ✅ Secrets almacenados en GitHub Secrets (encriptados)
- ✅ SSH keys no están en el repositorio (`.gitignore`)
- ✅ Archivos `*.tfvars` ignorados (tienen contraseñas)
- ✅ Archivos `.env` ignorados (variables de entorno)
- ✅ `terraform.tfstate` ignorado (puede contener secrets)

### ⚠️ Nunca subas al repositorio:
- ❌ Archivos `.pem` o `.key` (SSH keys)
- ❌ Archivos `terraform.tfvars` (contraseñas)
- ❌ Archivos `.env` (variables de entorno)
- ❌ Archivos `terraform.tfstate*` (estado de Terraform)

---

## 📚 Recursos Adicionales

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

## 🎯 Siguiente Paso

Una vez configurados los secrets, estás listo para hacer tu primer deployment:

```bash
git add .
git commit -m "Add health endpoint and CI/CD"
git push origin feature/aws-deployment
```

Luego haz merge a `main` y observa cómo se despliega automáticamente! 🚀
