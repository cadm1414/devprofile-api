# ✅ Checklist de Deployment a AWS

## Pre-Deployment

### 🔧 Herramientas Instaladas
- [ ] Terraform >= 1.0
- [ ] AWS CLI >= 2.0
- [ ] Docker >= 20.0
- [ ] Git
- [ ] OpenSSL o equivalente

### 🔑 Credenciales y Configuración
- [ ] AWS credentials configuradas (`aws configure`)
- [ ] Cuenta AWS activa
- [ ] Subscription ID verificado (`aws sts get-caller-identity`)
- [ ] Par de llaves SSH generado (`ssh-keygen -t rsa -b 4096 -f ~/.ssh/devprofile-aws`)

### 📝 Archivos de Configuración
- [ ] `terraform/terraform.tfvars` creado (desde `terraform.tfvars.example`)
- [ ] Valores en `terraform.tfvars` completados:
  - [ ] `aws_region`
  - [ ] `allowed_ssh_cidr` (tu IP pública)
  - [ ] `db_name`
  - [ ] `db_user`
  - [ ] `db_password` (generado con `openssl rand -base64 24`)
  - [ ] `api_secret_key` (generado con `openssl rand -base64 32`)
  - [ ] `ami_id` (Ubuntu 22.04 ARM64)

---

## Infraestructura (Terraform)

### 🏗️ Crear Infraestructura
- [ ] `cd terraform`
- [ ] `terraform init`
- [ ] `terraform validate`
- [ ] `terraform plan` (revisar output)
- [ ] `terraform apply` (confirmar con "yes")
- [ ] Guardar outputs importantes:
  ```bash
  terraform output instance_public_ip
  terraform output ssh_connection
  terraform output api_url
  ```

### ⏱️ Esperar Inicialización
- [ ] Esperar 5-10 minutos para que user-data complete setup
- [ ] Verificar logs de inicialización:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "tail -f /var/log/user-data.log"
  ```
- [ ] Confirmar mensaje "CONFIGURACIÓN COMPLETADA" en logs

### ✅ Verificar Servicios
- [ ] PostgreSQL corriendo:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "sudo systemctl status postgresql"
  ```
- [ ] Docker instalado:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "docker --version"
  ```
- [ ] Nginx configurado:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "sudo systemctl status nginx"
  ```

---

## Aplicación (Deployment)

### 🐳 Opción A: GitHub Actions (Recomendado)

#### Configurar Secrets
- [ ] Ir a repo > Settings > Secrets and variables > Actions
- [ ] Agregar secrets requeridos (ver `GITHUB_SECRETS.md`):
  - [ ] `EC2_HOST`
  - [ ] `EC2_SSH_KEY`
  - [ ] `DB_NAME`
  - [ ] `DB_USER`
  - [ ] `DB_PASSWORD`
  - [ ] `API_SECRET_KEY`
  - [ ] `DATABASE_URL` (para testing)
  - [ ] `SECRET_KEY` (para testing)

#### Trigger Deployment
- [ ] Push a branch `main` o `production`
- [ ] O trigger manualmente: Actions > Deploy to AWS EC2 > Run workflow
- [ ] Monitorear workflow en GitHub Actions tab
- [ ] Verificar que todos los steps pasen ✅

### 🔨 Opción B: Deployment Manual

- [ ] Copiar `.env.deploy.example` a `.env.deploy`
- [ ] Completar valores en `.env.deploy`
- [ ] Dar permisos de ejecución:
  ```bash
  chmod +x deploy-manual.sh
  ```
- [ ] Ejecutar script:
  ```bash
  ./deploy-manual.sh
  ```
- [ ] Confirmar cuando se pregunte
- [ ] Esperar a que complete todos los pasos

---

## Verificación Post-Deployment

### 🌐 Acceso Web
- [ ] Abrir en navegador: `http://<EC2_IP>/docs`
- [ ] Swagger UI carga correctamente
- [ ] Abrir: `http://<EC2_IP>/redoc`
- [ ] ReDoc carga correctamente

### 🔍 Health Checks
- [ ] Health endpoint responde:
  ```bash
  curl http://<EC2_IP>/health
  ```
  Debe retornar: `{"status":"healthy"}`

### 🧪 Pruebas de API

#### Registrar Usuario
- [ ] Ejecutar:
  ```bash
  curl -X POST http://<EC2_IP>/api/v1/identity/register \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "full_name": "Test User",
      "password": "testpassword123"
    }'
  ```
- [ ] Respuesta exitosa (status 200 o 201)

#### Login
- [ ] Ejecutar:
  ```bash
  curl -X POST http://<EC2_IP>/api/v1/auth/access \
    -H "Content-Type: application/json" \
    -d '{
      "email": "test@example.com",
      "password": "testpassword123"
    }'
  ```
- [ ] Recibir access token

#### Acceso Protegido
- [ ] Usar token recibido:
  ```bash
  curl http://<EC2_IP>/api/v1/identity/users/me \
    -H "Authorization: Bearer <ACCESS_TOKEN>"
  ```
- [ ] Recibir datos del usuario

### 💾 Base de Datos
- [ ] Conectar a PostgreSQL:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP>
  sudo -u postgres psql devprofile_db
  ```
- [ ] Verificar tablas:
  ```sql
  \dt
  SELECT * FROM users;
  ```
- [ ] Salir con `\q`

---

## Monitoreo

### 📊 Logs y Estado
- [ ] Ver logs de API:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "cd ~/devprofile-api && docker-compose logs -f"
  ```
- [ ] Ver estado de contenedores:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "docker ps"
  ```
- [ ] Verificar recursos del sistema:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "free -h && df -h"
  ```

### 💰 Costos
- [ ] Configurar AWS Budget:
  - Budget mensual: $10-15
  - Email alert al 80%
- [ ] Revisar AWS Cost Explorer semanal
- [ ] Verificar Free Tier usage

### 🔔 CloudWatch (Opcional)
- [ ] Abrir AWS Console > CloudWatch
- [ ] Ver alarma: `devprofile-api-high-cpu`
- [ ] Configurar SNS topic para notificaciones

---

## Seguridad

### 🔒 Firewall y Accesos
- [ ] Security Group solo permite tu IP para SSH
- [ ] Puertos HTTP (80) y HTTPS (443) abiertos al público
- [ ] Puerto 8000 cerrado al público (solo Nginx accede)
- [ ] PostgreSQL (5432) solo accesible desde localhost

### 🔐 Secrets y Keys
- [ ] Passwords son fuertes (>20 caracteres aleatorios)
- [ ] Secrets no están en git
- [ ] SSH key tiene permisos correctos (`chmod 600`)
- [ ] GitHub Secrets configurados correctamente

### 🛡️ SSL/TLS (Opcional)
- [ ] Dominio configurado en Route53
- [ ] Certificado SSL instalado (Let's Encrypt)
- [ ] Nginx configurado para HTTPS
- [ ] Redirect HTTP → HTTPS activo

---

## Backup y Recuperación

### 💾 Backup Automático
- [ ] Cron job configurado (daily backup):
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "crontab -l | grep backup-db"
  ```
- [ ] Verificar backups existen:
  ```bash
  ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "ls -lh ~/backups/"
  ```

### 🔄 Probar Restauración (Opcional)
- [ ] Descargar backup más reciente
- [ ] Crear base de datos de prueba
- [ ] Restaurar backup
- [ ] Verificar datos

---

## Documentación

### 📚 Completar Docs
- [ ] Actualizar README.md con:
  - [ ] URL de producción
  - [ ] Instrucciones de acceso
  - [ ] Contacto de soporte
- [ ] Documentar cambios en CHANGELOG.md
- [ ] Actualizar diagramas de arquitectura
- [ ] Documentar endpoints en Swagger

---

## Troubleshooting

### ❌ Si algo falla...

#### API no responde
- [ ] Verificar contenedor: `docker ps`
- [ ] Ver logs: `docker-compose logs`
- [ ] Reiniciar: `docker-compose restart`

#### Error de base de datos
- [ ] Verificar PostgreSQL: `sudo systemctl status postgresql`
- [ ] Ver logs: `tail -f /var/log/postgresql/postgresql-*.log`
- [ ] Reiniciar: `sudo systemctl restart postgresql`

#### SSH no conecta
- [ ] Verificar IP en Security Group
- [ ] Probar telnet: `telnet <EC2_IP> 22`
- [ ] Verificar instancia está corriendo en AWS Console

#### Espacio en disco
- [ ] Ver uso: `df -h`
- [ ] Limpiar Docker: `docker system prune -a`
- [ ] Eliminar backups antiguos: `find ~/backups -mtime +30 -delete`

---

## Post-Deployment Tasks

### 📋 Tareas Adicionales
- [ ] Configurar monitoring adicional (opcional)
- [ ] Setup alertas de email/SMS
- [ ] Documentar procedimientos de actualización
- [ ] Planificar mantenimientos
- [ ] Configurar CI/CD para otros ambientes (staging, dev)

### 🎯 Siguientes Pasos
- [ ] Implementar cache (Redis) si es necesario
- [ ] Configurar CDN para assets estáticos
- [ ] Optimizar queries de base de datos
- [ ] Implementar rate limiting
- [ ] Agregar métricas de negocio

---

## 🎉 Deployment Completado

**¡Felicitaciones!** Si todos los checks están marcados, tu API está deployada y funcionando en AWS.

### URLs Importantes:
- **API Base:** `http://<EC2_IP>`
- **Swagger Docs:** `http://<EC2_IP>/docs`
- **ReDoc:** `http://<EC2_IP>/redoc`

### Comandos Rápidos:
```bash
# SSH
ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP>

# Ver logs
ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "cd ~/devprofile-api && docker-compose logs -f"

# Reiniciar API
ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "cd ~/devprofile-api && docker-compose restart"

# Ver recursos
ssh -i ~/.ssh/devprofile-aws ubuntu@<EC2_IP> "htop"
```

---

**Deployment Date:** ___________  
**Deployed By:** ___________  
**Environment:** Production  
**Version:** ___________

---

**⚠️ Recordatorio de Costos:**
- Monitorear costos semanalmente
- Detener instancia cuando no se use en desarrollo
- Revisar Free Tier limits
- Budget estimado: ~$5.55/mes (~$33/6 meses)
