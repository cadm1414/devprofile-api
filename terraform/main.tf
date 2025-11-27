# DevProfile API - AWS Infrastructure SIMPLIFICADA
# Solo 3 valores obligatorios: IP, db_password, api_secret_key

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "DevProfile-API"
      Environment = "production"
      ManagedBy   = "Terraform"
    }
  }
}

# =============================================================================
# 1. GENERAR LLAVES SSH AUTOMÁTICAMENTE (NO necesitas crearlas manualmente)
# =============================================================================
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "devprofile" {
  key_name   = "devprofile-api-key"
  public_key = tls_private_key.ssh_key.public_key_openssh
}

# Guardar llave privada en archivo local
resource "local_file" "private_key" {
  content         = tls_private_key.ssh_key.private_key_pem
  filename        = "${path.module}/devprofile-aws-key.pem"
  file_permission = "0600"
}

# =============================================================================
# 2. NETWORKING (Usa VPC por defecto para ahorrar)
# =============================================================================
data "aws_vpc" "default" {
  default = true
}

# Security Group
resource "aws_security_group" "devprofile_api" {
  name        = "devprofile-api-sg"
  description = "Security group for DevProfile API"
  vpc_id      = data.aws_vpc.default.id

  # SSH solo desde tu IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr
    description = "SSH access from your IP"
  }

  # HTTP público
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  # HTTPS público (futuro)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  # Salida libre
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "devprofile-api-sg"
  }
}

# =============================================================================
# 3. EC2 INSTANCE (t4g.micro ARM - Free Tier)
# =============================================================================
resource "aws_instance" "devprofile_api" {
  ami           = var.ami_id
  instance_type = "t4g.micro" # Free Tier por 12 meses

  key_name               = aws_key_pair.devprofile.key_name
  vpc_security_group_ids = [aws_security_group.devprofile_api.id]

  # Storage mínimo
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  # Script de inicialización
  user_data = templatefile("${path.module}/user-data.sh", {
    db_name        = var.db_name
    db_user        = var.db_user
    db_password    = var.db_password
    api_secret_key = var.api_secret_key
  })

  tags = {
    Name = "devprofile-api-server"
  }
}

# =============================================================================
# 4. ELASTIC IP (IP fija)
# =============================================================================
resource "aws_eip" "devprofile_api" {
  domain   = "vpc"
  instance = aws_instance.devprofile_api.id

  tags = {
    Name = "devprofile-api-ip"
  }
}

# =============================================================================
# 5. DESPLIEGUE INICIAL DE LA APLICACIÓN DOCKER
# =============================================================================
resource "null_resource" "deploy_app" {
  # Ejecutar después de que la instancia y Elastic IP estén listos
  depends_on = [
    aws_eip.devprofile_api,
    aws_instance.devprofile_api
  ]

  # Trigger: re-ejecutar si cambia la instancia
  triggers = {
    instance_id = aws_instance.devprofile_api.id
  }

  # Conexión SSH
  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = tls_private_key.ssh_key.private_key_pem
    host        = aws_eip.devprofile_api.public_ip
    timeout     = "10m"
  }

  # 1. Esperar a que el user-data termine (PostgreSQL y Docker instalados)
  provisioner "remote-exec" {
    inline = [
      "echo '⏳ Esperando a que termine la inicialización del servidor...'",
      "cloud-init status --wait",
      "echo '✅ Servidor inicializado'",
      "echo '🔍 Verificando Docker...'",
      "sudo docker --version",
      "echo '🔍 Verificando PostgreSQL...'",
      "sudo systemctl is-active postgresql",
      "echo '✅ Servicios listos'"
    ]
  }

  # 2. Copiar docker-compose.yml al servidor
  provisioner "file" {
    source      = "${path.module}/../docker-compose.yml"
    destination = "/home/ubuntu/devprofile-api/docker-compose.yml"
  }

  # 3. Copiar Dockerfile al servidor
  provisioner "file" {
    source      = "${path.module}/../Dockerfile"
    destination = "/home/ubuntu/devprofile-api/Dockerfile"
  }

  # 4. Copiar código fuente de la aplicación
  provisioner "file" {
    source      = "${path.module}/../app"
    destination = "/home/ubuntu/devprofile-api/"
  }

  # 5. Copiar requirements.txt
  provisioner "file" {
    source      = "${path.module}/../requirements.txt"
    destination = "/home/ubuntu/devprofile-api/requirements.txt"
  }

  # 6. Construir imagen Docker y desplegar
  provisioner "remote-exec" {
    inline = [
      "echo '🐳 Construyendo imagen Docker...'",
      "cd /home/ubuntu/devprofile-api",
      "sudo docker build -t devprofile-api:latest .",
      "echo '✅ Imagen construida'",
      "echo '🚀 Desplegando aplicación con docker-compose...'",
      "sudo docker-compose down 2>/dev/null || true",
      "sudo docker-compose up -d",
      "echo '⏳ Esperando a que la API inicie...'",
      "sleep 15",
      "echo '🔍 Verificando estado de los contenedores...'",
      "sudo docker-compose ps",
      "echo '📋 Logs recientes:'",
      "sudo docker-compose logs --tail=30",
      "echo '✅ Deployment completado!'",
      "echo '📍 API disponible en: http://${aws_eip.devprofile_api.public_ip}'",
      "echo '📚 Documentación: http://${aws_eip.devprofile_api.public_ip}/docs'"
    ]
  }
}

# =============================================================================
# 6. OUTPUTS (Información importante)
# =============================================================================
output "instance_id" {
  description = "ID de la instancia EC2"
  value       = aws_instance.devprofile_api.id
}

output "public_ip" {
  description = "IP pública de la API"
  value       = aws_eip.devprofile_api.public_ip
}

output "api_url" {
  description = "URL de la API"
  value       = "http://${aws_eip.devprofile_api.public_ip}"
}

output "api_docs_url" {
  description = "URL de la documentación Swagger"
  value       = "http://${aws_eip.devprofile_api.public_ip}/docs"
}

output "ssh_command" {
  description = "Comando para conectar por SSH"
  value       = "ssh -i ${path.module}/devprofile-aws-key.pem ubuntu@${aws_eip.devprofile_api.public_ip}"
}

output "ssh_key_location" {
  description = "Ubicación de la llave privada SSH"
  value       = "${path.module}/devprofile-aws-key.pem"
}

output "database_info" {
  description = "Información de la base de datos PostgreSQL"
  value = {
    host     = "localhost (dentro del EC2)"
    port     = "5432"
    database = var.db_name
    user     = var.db_user
  }
  sensitive = false
}

output "deployment_status" {
  description = "Estado del despliegue"
  value       = "✅ Aplicación desplegada automáticamente con Docker"
  depends_on  = [null_resource.deploy_app]
}

output "estimated_monthly_cost" {
  description = "Costo mensual estimado"
  value       = "$5.55/month (~$33 for 6 months) - Free Tier: $2/month for first 12 months"
}
