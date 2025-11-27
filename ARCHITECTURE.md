# Arquitectura de Deployment en AWS

## 📐 Vista General

```
┌─────────────────────────────────────────────────────────────────────┐
│                            INTERNET                                  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ HTTP/HTTPS
                                 │
                    ┌────────────▼────────────┐
                    │   Elastic IP (Static)   │
                    │    52.xx.xx.xx         │
                    └────────────┬────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────┐
│                        AWS EC2 Instance                              │
│                     (t4g.micro - ARM64)                             │
│                      Ubuntu 22.04 LTS                                │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Security Group                             │  │
│  │  • SSH (22) - Solo tu IP                                      │  │
│  │  • HTTP (80) - 0.0.0.0/0                                      │  │
│  │  • HTTPS (443) - 0.0.0.0/0                                    │  │
│  │  • API (8000) - Bloqueado                                     │  │
│  │  • PostgreSQL (5432) - Bloqueado                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                │                                     │
│                                │                                     │
│  ┌────────────────────────────▼────────────────────────────────┐   │
│  │                    Nginx (Reverse Proxy)                     │   │
│  │                     Port 80/443 → 8000                       │   │
│  │  • SSL Termination (futuro)                                  │   │
│  │  • Static file serving                                       │   │
│  │  • Rate limiting                                             │   │
│  │  • Caching                                                   │   │
│  └────────────────────────────┬────────────────────────────────┘   │
│                                │                                     │
│                                │ Proxy Pass                          │
│                                │                                     │
│  ┌────────────────────────────▼────────────────────────────────┐   │
│  │              Docker Container (devprofile-api)               │   │
│  │                      Port 8000                               │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │                FastAPI Application                      │ │   │
│  │  │  • Uvicorn ASGI Server                                  │ │   │
│  │  │  • 2 workers                                            │ │   │
│  │  │  • Auto-reload disabled                                 │ │   │
│  │  │  • Resource limits:                                     │ │   │
│  │  │    - CPU: 0.5 cores                                     │ │   │
│  │  │    - Memory: 512MB                                      │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  │                                │                              │   │
│  │                                │ network_mode: host           │   │
│  │                                │                              │   │
│  └────────────────────────────────┼──────────────────────────────┘   │
│                                   │                                  │
│                                   │ localhost:5432                   │
│                                   │                                  │
│  ┌────────────────────────────────▼──────────────────────────────┐  │
│  │                    PostgreSQL 14                               │  │
│  │                     Port 5432 (localhost only)                 │  │
│  │  • Database: devprofile_db                                     │  │
│  │  • User: devprofile_user                                       │  │
│  │  • Automated daily backups                                     │  │
│  │  • Backup retention: 7 days                                    │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                       Filesystem                                │ │
│  │  /home/ubuntu/devprofile-api/                                  │ │
│  │  ├── docker-compose.yml                                        │ │
│  │  ├── .env (secrets)                                            │ │
│  │  ├── deploy.sh (deployment script)                             │ │
│  │  └── backups/ (PostgreSQL dumps)                               │ │
│  │      └── devprofile_db_YYYYMMDD_HHMMSS.sql.gz                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                        AWS CloudWatch                                 │
│  • CPU Utilization Alarm (>80%)                                      │
│  • Memory metrics                                                     │
│  • Disk usage                                                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Request

### 1. Request del Cliente
```
Usuario → http://52.xx.xx.xx/api/v1/auth/access
```

### 2. Procesamiento
```
Elastic IP (52.xx.xx.xx)
    ↓
Security Group (verifica puerto 80)
    ↓
Nginx (puerto 80)
    ↓ proxy_pass
Docker Container (FastAPI en puerto 8000)
    ↓
API procesa request
    ↓
PostgreSQL (localhost:5432)
    ↓
Respuesta ← Usuario
```

---

## 🏗️ CI/CD Pipeline

```
┌──────────────────────┐
│  Developer Commits   │
│   git push origin    │
│        main          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│     GitHub Repository        │
│  github.com/user/repo        │
└──────────┬───────────────────┘
           │
           │ Webhook triggers
           │
           ▼
┌─────────────────────────────────────────────┐
│         GitHub Actions Runner                │
│                                              │
│  Step 1: Run Tests                          │
│  ├── pytest (unit + integration)            │
│  ├── coverage report                        │
│  └── newman API tests                       │
│                                              │
│  Step 2: Build Docker Image                 │
│  ├── docker build                           │
│  └── docker save → .tar.gz                  │
│                                              │
│  Step 3: Deploy to EC2                      │
│  ├── SCP files to EC2                       │
│  ├── SSH to EC2                             │
│  ├── docker load                            │
│  ├── docker-compose down                    │
│  ├── docker-compose up -d                   │
│  └── health check verification              │
│                                              │
└─────────────────┬───────────────────────────┘
                  │
                  │ SSH Connection
                  │ (using EC2_SSH_KEY secret)
                  │
                  ▼
         ┌────────────────┐
         │   AWS EC2      │
         │   Instance     │
         └────────────────┘
```

---

## 💰 Estructura de Costos

### Desglose Mensual (región us-east-1)

| Recurso | Tipo | Costo/mes | Notas |
|---------|------|-----------|-------|
| **EC2 Instance** | t4g.micro | $6.13 | Free Tier: 750 hrs/mes (12 meses) |
| **EBS Storage** | 30 GB gp3 | $2.40 | OS + App + DB + Backups |
| **Elastic IP** | Static IP | $0.00 | Sin cargo si está asociada |
| **Data Transfer** | Out to internet | $0.90 | ~10GB/mes estimado |
| **CloudWatch** | Metrics/Alarms | $0.00 | Free Tier: 10 alarmas |
| **Backups** | gp3 storage | $0.12 | 1.5GB backups (7 días) |
| | | | |
| **TOTAL (sin Free Tier)** | | **~$9.55/mes** | |
| **TOTAL (con Free Tier)** | | **~$3.42/mes** | Primeros 12 meses |

### Proyección 6 Meses

- **Escenario 1 (Free Tier nuevo):** 6 meses × $3.42 = **~$20.52** ✅ Dentro del presupuesto
- **Escenario 2 (Free Tier expirado):** 6 meses × $9.55 = **~$57.30** ⚠️ Sobre presupuesto

### 💡 Optimizaciones de Costo

1. **Detener instancia fuera de horario:**
   - Trabajas 8hrs/día? → Detén la instancia 16hrs
   - Ahorro: ~60% del costo de compute
   - Comando: `aws ec2 stop-instances --instance-ids <id>`

2. **Reducir backups:**
   - Mantener solo 3 días en lugar de 7
   - Ahorro: ~$0.07/mes

3. **Comprimir y limpiar Docker:**
   - `docker system prune -a` regularmente
   - Libera espacio de EBS

4. **Monitorear Data Transfer:**
   - Usar CloudFront para cacheo (Free Tier: 1TB/mes)
   - Comprimir responses con gzip

---

## 🔐 Configuración de Seguridad

### Security Group Rules

```yaml
Inbound:
  - Port 22 (SSH):
      Source: Mi_IP_Publica/32
      Descripción: "SSH desde mi red"
  
  - Port 80 (HTTP):
      Source: 0.0.0.0/0
      Descripción: "Acceso público HTTP"
  
  - Port 443 (HTTPS):
      Source: 0.0.0.0/0
      Descripción: "Acceso público HTTPS (futuro)"

Outbound:
  - All traffic:
      Destination: 0.0.0.0/0
      Descripción: "Permitir todas las salidas"
```

### Variables de Entorno (.env en EC2)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db
DB_NAME=devprofile_db
DB_USER=devprofile_user
DB_PASSWORD=********** (32+ chars random)

# API
API_SECRET_KEY=********** (base64 32 bytes)
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# CORS
CORS_ORIGINS=*
```

### GitHub Secrets

```
EC2_HOST           # IP pública de EC2
EC2_SSH_KEY        # Llave privada SSH completa
DB_NAME            # Nombre de la BD
DB_USER            # Usuario de PostgreSQL
DB_PASSWORD        # Password de PostgreSQL
API_SECRET_KEY     # Secret para JWT
DATABASE_URL       # URL completa de conexión (testing)
SECRET_KEY         # Secret para JWT (testing)
```

---

## 📊 Monitoreo y Alertas

### CloudWatch Alarms Configuradas

1. **CPU High (>80%)**
   - Condición: CPUUtilization > 80% por 2 períodos de 5 minutos
   - Acción: Enviar alerta (requiere SNS topic configurado)

### Logs Importantes

```bash
# API Application Logs
/home/ubuntu/devprofile-api/
  └── docker-compose logs

# Nginx Logs
/var/log/nginx/
  ├── access.log
  └── error.log

# PostgreSQL Logs
/var/log/postgresql/
  └── postgresql-14-main.log

# System Initialization
/var/log/user-data.log
```

### Comandos de Monitoreo

```bash
# Ver uso de recursos
htop

# Ver logs en tiempo real
docker-compose logs -f

# Ver estado de servicios
systemctl status postgresql docker nginx

# Ver espacio en disco
df -h

# Ver backups
ls -lh ~/backups/
```

---

## 🔄 Proceso de Actualización

### Opción 1: GitHub Actions (Automático)
```bash
git add .
git commit -m "Update: descripción del cambio"
git push origin main
# GitHub Actions despliega automáticamente
```

### Opción 2: Manual
```bash
# Local
./deploy-manual.sh

# O paso a paso
docker build -t devprofile-api:latest .
docker save devprofile-api:latest | gzip > api.tar.gz
scp -i ~/.ssh/devprofile-aws api.tar.gz ubuntu@EC2_IP:~/
ssh -i ~/.ssh/devprofile-aws ubuntu@EC2_IP
cd ~/devprofile-api
docker load < api.tar.gz
docker-compose up -d
```

---

## 📈 Escalabilidad Futura

### Vertical (Misma arquitectura, más recursos)
- Upgrade a t4g.small ($0.0168/hr → ~$12.26/mes)
- Aumentar EBS storage según necesidad

### Horizontal (Arquitectura distribuida)
```
┌─────────────────────┐
│  Application Load   │
│     Balancer        │
└──────────┬──────────┘
           │
     ┌─────┼─────┐
     │     │     │
   EC2-1 EC2-2 EC2-3
     │     │     │
     └─────┼─────┘
           │
    ┌──────▼──────┐
    │  RDS        │
    │  PostgreSQL │
    └─────────────┘
```

Costo estimado: ~$50-80/mes

---

## 🆘 Disaster Recovery

### Backups Automáticos
- **Frecuencia:** Diario (2 AM UTC)
- **Retención:** 7 días
- **Ubicación:** `/home/ubuntu/backups/`
- **Formato:** `devprofile_db_YYYYMMDD_HHMMSS.sql.gz`

### Restauración
```bash
# Conectar a EC2
ssh -i ~/.ssh/devprofile-aws ubuntu@EC2_IP

# Listar backups
ls -lh ~/backups/

# Restaurar
gunzip < ~/backups/devprofile_db_20250115_020000.sql.gz | \
  sudo -u postgres psql devprofile_db

# Reiniciar API
cd ~/devprofile-api
docker-compose restart
```

### Reconstrucción Completa
```bash
# Destruir y recrear infraestructura
cd terraform
terraform destroy -auto-approve
terraform apply -auto-approve

# Esperar inicialización (5-10 min)
# Desplegar aplicación
cd ..
./deploy-manual.sh
```

---

**Última Actualización:** 2025-01-15  
**Versión:** 2.1.0  
**Autor:** Carlos Alberto Diaz Minaya
