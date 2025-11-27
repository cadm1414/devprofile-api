# 🚀 Referencia Rápida - DevProfile API

## 📋 Índice Rápido
- [Comandos Terraform](#comandos-terraform)
- [Comandos Docker](#comandos-docker)
- [Comandos AWS CLI](#comandos-aws-cli)
- [Comandos SSH](#comandos-ssh)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Variables de Entorno](#variables-de-entorno)

---

## Comandos Terraform

### Inicialización y Deploy
```bash
# Inicializar (primera vez)
cd terraform
terraform init

# Validar sintaxis
terraform validate

# Ver plan sin aplicar
terraform plan

# Aplicar infraestructura
terraform apply

# Aplicar sin confirmación
terraform apply -auto-approve

# Destruir todo
terraform destroy
terraform destroy -auto-approve
```

### Ver Outputs
```bash
# Ver todos los outputs
terraform output

# Output específico
terraform output instance_public_ip
terraform output ssh_connection
terraform output api_url
terraform output db_name

# Output en formato JSON
terraform output -json

# Guardar IP en variable
export EC2_IP=$(terraform output -raw instance_public_ip)
echo $EC2_IP
```

### Estado y Formato
```bash
# Ver estado actual
terraform show

# Listar recursos
terraform state list

# Ver recurso específico
terraform state show aws_instance.devprofile_api

# Formatear archivos .tf
terraform fmt

# Validar y formatear
terraform fmt -recursive && terraform validate
```

---

## Comandos Docker

### Build y Gestión de Imágenes
```bash
# Build imagen
docker build -t devprofile-api:latest .

# Build con nombre específico
docker build -t devprofile-api:v1.0.0 .

# Build sin cache
docker build --no-cache -t devprofile-api:latest .

# Listar imágenes
docker images

# Eliminar imagen
docker rmi devprofile-api:latest

# Guardar imagen a archivo
docker save devprofile-api:latest | gzip > devprofile-api.tar.gz

# Cargar imagen desde archivo
docker load < devprofile-api.tar.gz
gunzip -c devprofile-api.tar.gz | docker load
```

### Docker Compose
```bash
# Iniciar servicios
docker-compose up -d

# Iniciar y ver logs
docker-compose up

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver logs
docker-compose logs
docker-compose logs -f          # Follow mode
docker-compose logs --tail=100  # Últimas 100 líneas
docker-compose logs api         # Solo servicio api

# Ver estado
docker-compose ps

# Reconstruir y reiniciar
docker-compose up -d --build
```

### Limpieza
```bash
# Limpiar contenedores detenidos
docker container prune

# Limpiar imágenes sin usar
docker image prune

# Limpiar todo (⚠️ cuidado)
docker system prune -a

# Ver espacio usado
docker system df
```

---

## Comandos AWS CLI

### EC2 Instances
```bash
# Listar instancias
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]' --output table

# Detener instancia
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Iniciar instancia
aws ec2 start-instances --instance-ids i-1234567890abcdef0

# Ver estado
aws ec2 describe-instance-status --instance-ids i-1234567890abcdef0

# Obtener IP pública
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
```

### Security Groups
```bash
# Listar security groups
aws ec2 describe-security-groups --query 'SecurityGroups[*].[GroupId,GroupName]' --output table

# Ver reglas de un SG
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Agregar regla SSH para nueva IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/32
```

### AMI (Amazon Machine Images)
```bash
# Buscar AMI de Ubuntu 22.04 ARM64
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*" \
  --region us-east-1 \
  --query 'sort_by(Images, &CreationDate)[-1].[ImageId,Name,CreationDate]' \
  --output table
```

### CloudWatch
```bash
# Ver alarmas
aws cloudwatch describe-alarms

# Ver métricas de CPU
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-xxxxx \
  --start-time 2025-01-15T00:00:00Z \
  --end-time 2025-01-15T23:59:59Z \
  --period 3600 \
  --statistics Average
```

### Costos
```bash
# Ver costos del mes actual
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Ver forecast
aws ce get-cost-forecast \
  --time-period Start=2025-01-15,End=2025-01-31 \
  --metric UNBLENDED_COST \
  --granularity MONTHLY
```

---

## Comandos SSH

### Conexión
```bash
# Conectar a EC2
ssh -i ~/.ssh/devprofile-aws ubuntu@54.123.45.67

# Conectar con variable
export EC2_IP=$(cd terraform && terraform output -raw instance_public_ip)
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP

# Conectar sin verificar host key (primera vez)
ssh -i ~/.ssh/devprofile-aws -o StrictHostKeyChecking=no ubuntu@$EC2_IP
```

### SCP (Copiar archivos)
```bash
# Copiar archivo local a EC2
scp -i ~/.ssh/devprofile-aws archivo.txt ubuntu@$EC2_IP:~/

# Copiar directorio
scp -i ~/.ssh/devprofile-aws -r ./directorio ubuntu@$EC2_IP:~/

# Copiar desde EC2 a local
scp -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP:~/archivo.txt ./

# Copiar backup desde EC2
scp -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP:~/backups/devprofile_db_*.sql.gz ./backups/
```

### Comandos Remotos
```bash
# Ejecutar comando remoto
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "ls -la"

# Ver logs remotos
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "cd ~/devprofile-api && docker-compose logs --tail=50"

# Reiniciar API remotamente
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "cd ~/devprofile-api && docker-compose restart"

# Ver estado de servicios
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "systemctl status postgresql docker nginx"
```

---

## Testing

### pytest
```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Test específico
pytest tests/unit/test_password_service.py

# Con verbosidad
pytest -v

# Solo tests que fallen
pytest --lf

# Parallel execution (requiere pytest-xdist)
pytest -n auto
```

### Locust (Performance)
```bash
# Iniciar Locust
locust -f locustfile.py

# Con parámetros
locust -f locustfile.py --host=http://localhost:8000

# Headless mode
locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 60s --headless
```

### Newman (Postman)
```bash
# Ejecutar colección
newman run devprofile-postman.json -e environment.json

# Con reporte HTML
newman run devprofile-postman.json --reporters cli,html --reporter-html-export newman-report.html

# Con delay entre requests
newman run devprofile-postman.json --delay-request 1000
```

---

## Troubleshooting

### API no responde
```bash
# 1. Ver logs
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "cd ~/devprofile-api && docker-compose logs --tail=100"

# 2. Ver contenedores
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "docker ps -a"

# 3. Verificar puerto
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "netstat -tlnp | grep 8000"

# 4. Health check local
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "curl http://localhost:8000/health"

# 5. Reiniciar
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "cd ~/devprofile-api && docker-compose restart"
```

### Error PostgreSQL
```bash
# Ver estado
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "sudo systemctl status postgresql"

# Ver logs
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "sudo tail -f /var/log/postgresql/postgresql-*.log"

# Reiniciar
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "sudo systemctl restart postgresql"

# Verificar conexión
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP 'sudo -u postgres psql -c "SELECT version();"'

# Ver bases de datos
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP 'sudo -u postgres psql -c "\l"'
```

### Nginx problemas
```bash
# Ver configuración
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "sudo nginx -t"

# Ver logs
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "sudo tail -f /var/log/nginx/error.log"

# Reiniciar
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "sudo systemctl restart nginx"

# Ver estado
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "sudo systemctl status nginx"
```

### Espacio en disco
```bash
# Ver uso
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "df -h"

# Ver archivos grandes
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "du -sh /home/ubuntu/* | sort -h"

# Limpiar Docker
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "docker system prune -a -f"

# Limpiar backups antiguos
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "find ~/backups -name '*.sql.gz' -mtime +7 -delete"

# Limpiar logs
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "sudo journalctl --vacuum-time=7d"
```

### SSH no conecta
```bash
# 1. Verificar IP
cd terraform && terraform output instance_public_ip

# 2. Verificar instancia corriendo
aws ec2 describe-instances --instance-ids $(terraform output -raw instance_id) --query 'Reservations[0].Instances[0].State.Name'

# 3. Verificar Security Group
aws ec2 describe-security-groups --group-ids $(terraform output -raw security_group_id)

# 4. Obtener tu IP
curl ifconfig.me

# 5. Actualizar terraform.tfvars con tu IP y aplicar
terraform apply -auto-approve

# 6. Test conexión
telnet $EC2_IP 22
```

---

## Variables de Entorno

### Generar Secrets
```bash
# Secret key (32 bytes base64)
openssl rand -base64 32

# Password seguro (24 bytes base64)
openssl rand -base64 24

# Password alfanumérico (32 chars)
openssl rand -hex 16

# UUID
uuidgen
```

### Obtener tu IP pública
```bash
# Linux/Mac/WSL
curl ifconfig.me
curl ipinfo.io/ip
curl icanhazip.com

# PowerShell
(Invoke-WebRequest -Uri "http://ifconfig.me/ip").Content.Trim()
```

### GitHub Secrets (gh CLI)
```bash
# Instalar gh CLI
# Mac: brew install gh
# Windows: choco install gh
# Linux: https://github.com/cli/cli#installation

# Autenticar
gh auth login

# Configurar secrets
gh secret set EC2_HOST --body "54.123.45.67"
gh secret set EC2_SSH_KEY < ~/.ssh/devprofile-aws
gh secret set DB_NAME --body "devprofile_db"
gh secret set DB_USER --body "devprofile_user"
gh secret set DB_PASSWORD --body "$(openssl rand -base64 24)"
gh secret set API_SECRET_KEY --body "$(openssl rand -base64 32)"

# Listar secrets
gh secret list

# Ver secret (solo muestra si existe, no el valor)
gh secret set EC2_HOST
```

---

## URLs Importantes

### Desarrollo Local
- API Base: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

### Producción (AWS)
- API Base: `http://54.xxx.xxx.xxx`
- Swagger: `http://54.xxx.xxx.xxx/docs`
- ReDoc: `http://54.xxx.xxx.xxx/redoc`
- Health: `http://54.xxx.xxx.xxx/health`

### AWS Console
- EC2 Dashboard: https://console.aws.amazon.com/ec2/
- CloudWatch: https://console.aws.amazon.com/cloudwatch/
- Cost Explorer: https://console.aws.amazon.com/cost-management/
- Billing: https://console.aws.amazon.com/billing/

### Documentación
- FastAPI: https://fastapi.tiangolo.com
- Terraform AWS: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Docker: https://docs.docker.com
- PostgreSQL: https://www.postgresql.org/docs/

---

## One-Liners Útiles

```bash
# Deploy completo en un comando
cd terraform && terraform apply -auto-approve && cd .. && ./deploy-manual.sh

# Ver estado completo de la API en producción
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "docker-compose ps && docker-compose logs --tail=20 && free -h && df -h"

# Backup manual y descargar
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "~/backup-db.sh" && scp -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP:~/backups/devprofile_db_*.sql.gz ./

# Actualizar API rápido
docker build -t devprofile-api:latest . && docker save devprofile-api:latest | gzip > api.tar.gz && scp -i ~/.ssh/devprofile-aws api.tar.gz ubuntu@$EC2_IP:~/devprofile-api/ && ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "cd ~/devprofile-api && docker load < api.tar.gz && docker-compose up -d && rm api.tar.gz"

# Ver todos los logs importantes
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "echo '=== Docker Logs ===' && docker-compose logs --tail=20 && echo '\n=== Nginx Error Log ===' && sudo tail -20 /var/log/nginx/error.log && echo '\n=== PostgreSQL Log ===' && sudo tail -20 /var/log/postgresql/postgresql-*.log"

# Monitoreo continuo (requiere Ctrl+C para salir)
watch -n 5 'ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "docker stats --no-stream && echo && free -h && echo && df -h /"'
```

---

## Checklist Deployment Rápido

```bash
# 1. Configurar terraform.tfvars
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
nano terraform/terraform.tfvars  # Editar valores

# 2. Deploy infraestructura
cd terraform && terraform init && terraform apply -auto-approve

# 3. Esperar inicialización (5-10 min)
export EC2_IP=$(terraform output -raw instance_public_ip)
ssh -i ~/.ssh/devprofile-aws ubuntu@$EC2_IP "tail -f /var/log/user-data.log"

# 4. Deploy aplicación
cd .. && ./deploy-manual.sh

# 5. Verificar
curl http://$EC2_IP/health
curl http://$EC2_IP/docs

# ✅ Done!
```

---

**💡 Tip:** Guarda este archivo en tu escritorio o bookmarks para acceso rápido.

**📚 Documentación completa:**
- `terraform/README.md` - Guía detallada de deployment
- `DEPLOYMENT_CHECKLIST.md` - Checklist completo
- `ARCHITECTURE.md` - Diagramas y arquitectura
- `GITHUB_SECRETS.md` - Configuración de CI/CD

---

**Autor:** Carlos Alberto Diaz Minaya  
**Última Actualización:** 2025-01-15  
**Versión:** 2.1.0
