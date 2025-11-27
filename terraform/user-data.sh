#!/bin/bash
# User Data Script para inicializar EC2 con PostgreSQL y Docker
# Este script se ejecuta automáticamente al crear la instancia

set -e

# Logging
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "=========================================="
echo "Iniciando configuración de DevProfile API"
echo "Fecha: $(date)"
echo "=========================================="

# Actualizar sistema
echo "📦 Actualizando sistema..."
apt-get update -y
apt-get upgrade -y

# Instalar utilidades básicas
echo "🛠️ Instalando utilidades..."
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools \
    ufw \
    unzip

# Configurar timezone
timedatectl set-timezone America/Lima

# ========================================
# INSTALAR POSTGRESQL
# ========================================
echo "🐘 Instalando PostgreSQL..."
apt-get install -y postgresql postgresql-contrib

# Iniciar y habilitar PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Configurar PostgreSQL
echo "⚙️ Configurando PostgreSQL..."
sudo -u postgres psql <<-EOSQL
    CREATE DATABASE ${db_name};
    CREATE USER ${db_user} WITH ENCRYPTED PASSWORD '${db_password}';
    GRANT ALL PRIVILEGES ON DATABASE ${db_name} TO ${db_user};
    ALTER DATABASE ${db_name} OWNER TO ${db_user};
EOSQL

# Configurar PostgreSQL para escuchar en localhost
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf

# Configurar autenticación
cat >> /etc/postgresql/*/main/pg_hba.conf <<EOF
# DevProfile API local connection
local   ${db_name}   ${db_user}   md5
host    ${db_name}   ${db_user}   127.0.0.1/32   md5
EOF

# Reiniciar PostgreSQL
systemctl restart postgresql

echo "✅ PostgreSQL configurado correctamente"

# ========================================
# INSTALAR DOCKER
# ========================================
echo "🐳 Instalando Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Agregar usuario ubuntu a grupo docker
usermod -aG docker ubuntu

# Instalar Docker Compose
echo "📦 Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Iniciar y habilitar Docker
systemctl start docker
systemctl enable docker

echo "✅ Docker instalado correctamente"

# ========================================
# CONFIGURAR FIREWALL (UFW)
# ========================================
echo "🔥 Configurando firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # FastAPI
ufw reload

echo "✅ Firewall configurado"

# ========================================
# CREAR ESTRUCTURA DE DIRECTORIOS
# ========================================
echo "📁 Creando estructura de directorios..."
mkdir -p /home/ubuntu/devprofile-api
mkdir -p /home/ubuntu/devprofile-api/logs
chown -R ubuntu:ubuntu /home/ubuntu/devprofile-api

# ========================================
# CREAR ARCHIVO .ENV
# ========================================
echo "📝 Creando archivo de configuración..."
cat > /home/ubuntu/devprofile-api/.env <<EOF
# API Configuration
API_PREFIX=/api/v1
ORIGINS=*

# Database Configuration (PostgreSQL)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=${db_name}
DB_USER=${db_user}
DB_PASSWORD=${db_password}

# JWT Configuration
SECRET_KEY=${api_secret_key}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Environment
ENVIRONMENT=production
EOF

chown ubuntu:ubuntu /home/ubuntu/devprofile-api/.env
chmod 600 /home/ubuntu/devprofile-api/.env

# ========================================
# CREAR DOCKER COMPOSE
# ========================================
echo "🐳 Creando docker-compose.yml..."
cat > /home/ubuntu/devprofile-api/docker-compose.yml <<'EOF'
version: '3.8'

services:
  api:
    image: devprofile-api:latest
    container_name: devprofile-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - API_PREFIX=/api/v1
      - ORIGINS=*
      - DB_HOST=host.docker.internal
    env_file:
      - .env
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
EOF

chown ubuntu:ubuntu /home/ubuntu/devprofile-api/docker-compose.yml

# ========================================
# CREAR SCRIPT DE DEPLOYMENT
# ========================================
echo "📜 Creando script de deployment..."
cat > /home/ubuntu/devprofile-api/deploy.sh <<'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "🚀 Iniciando deployment de DevProfile API..."

# Ir al directorio del proyecto
cd /home/ubuntu/devprofile-api

# Pull de la nueva imagen (cuando esté en registry)
# docker pull tu-registry/devprofile-api:latest

# Detener contenedores actuales
echo "🛑 Deteniendo contenedores..."
docker-compose down || true

# Limpiar imágenes antiguas
echo "🧹 Limpiando imágenes antiguas..."
docker image prune -f

# Levantar nuevos contenedores
echo "🚀 Levantando contenedores..."
docker-compose up -d

# Verificar estado
echo "✅ Verificando estado..."
sleep 5
docker-compose ps
docker-compose logs --tail=50

echo "✅ Deployment completado!"
DEPLOY_SCRIPT

chmod +x /home/ubuntu/devprofile-api/deploy.sh
chown ubuntu:ubuntu /home/ubuntu/devprofile-api/deploy.sh

# ========================================
# CREAR SYSTEMD SERVICE (opcional)
# ========================================
cat > /etc/systemd/system/devprofile-api.service <<EOF
[Unit]
Description=DevProfile API Service
Requires=docker.service postgresql.service
After=docker.service postgresql.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/devprofile-api
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
# No habilitamos aún porque necesitamos la imagen Docker primero
# systemctl enable devprofile-api.service

# ========================================
# INSTALAR NGINX (para proxy reverso)
# ========================================
echo "🌐 Instalando Nginx..."
apt-get install -y nginx

# Configurar Nginx como proxy reverso
cat > /etc/nginx/sites-available/devprofile-api <<'NGINX_CONFIG'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
NGINX_CONFIG

# Habilitar sitio
ln -sf /etc/nginx/sites-available/devprofile-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Probar y reiniciar Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx

echo "✅ Nginx configurado como proxy reverso"

# ========================================
# CONFIGURAR LOGROTATE
# ========================================
cat > /etc/logrotate.d/devprofile-api <<EOF
/home/ubuntu/devprofile-api/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
}
EOF

# ========================================
# CREAR SCRIPT DE BACKUP (PostgreSQL)
# ========================================
cat > /home/ubuntu/backup-db.sh <<'BACKUP_SCRIPT'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sudo -u postgres pg_dump ${db_name} | gzip > $BACKUP_DIR/devprofile_db_$TIMESTAMP.sql.gz
# Mantener solo últimos 7 backups
find $BACKUP_DIR -name "devprofile_db_*.sql.gz" -mtime +7 -delete
echo "Backup completado: devprofile_db_$TIMESTAMP.sql.gz"
BACKUP_SCRIPT

chmod +x /home/ubuntu/backup-db.sh
chown ubuntu:ubuntu /home/ubuntu/backup-db.sh

# Agregar cron para backup diario a las 2 AM
(crontab -u ubuntu -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup-db.sh >> /home/ubuntu/backup.log 2>&1") | crontab -u ubuntu -

# ========================================
# INFORMACIÓN FINAL
# ========================================
cat > /home/ubuntu/SETUP_INFO.txt <<EOF
========================================
🎉 SETUP COMPLETADO EXITOSAMENTE
========================================

📋 Información del Sistema:
- PostgreSQL: Instalado y corriendo
- Docker: Instalado y corriendo
- Nginx: Configurado como proxy reverso
- Firewall: Activo (puertos 22, 80, 443, 8000)

📂 Directorios:
- Proyecto: /home/ubuntu/devprofile-api
- Logs: /home/ubuntu/devprofile-api/logs
- Backups: /home/ubuntu/backups

🔑 Credenciales PostgreSQL:
- Database: ${db_name}
- User: ${db_user}
- Host: localhost
- Port: 5432

📝 Archivos importantes:
- .env: /home/ubuntu/devprofile-api/.env
- docker-compose: /home/ubuntu/devprofile-api/docker-compose.yml
- deploy script: /home/ubuntu/devprofile-api/deploy.sh
- backup script: /home/ubuntu/backup-db.sh

🚀 Próximos pasos:
1. Construir imagen Docker de la API
2. Ejecutar: cd /home/ubuntu/devprofile-api && ./deploy.sh
3. Verificar: curl http://localhost:8000/docs

📊 Monitoreo:
- Logs API: docker-compose logs -f
- Logs Nginx: tail -f /var/log/nginx/access.log
- Logs PostgreSQL: tail -f /var/log/postgresql/postgresql-*.log

🔧 Comandos útiles:
- Conectar a PostgreSQL: sudo -u postgres psql ${db_name}
- Reiniciar API: cd /home/ubuntu/devprofile-api && docker-compose restart
- Ver contenedores: docker ps
- Backup manual: /home/ubuntu/backup-db.sh

========================================
EOF

chown ubuntu:ubuntu /home/ubuntu/SETUP_INFO.txt

# Mostrar información
cat /home/ubuntu/SETUP_INFO.txt

echo ""
echo "=========================================="
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "=========================================="
echo "Revisar: /home/ubuntu/SETUP_INFO.txt"
echo "=========================================="
