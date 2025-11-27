# =============================================================================
# VARIABLES SIMPLIFICADAS - Solo 3 obligatorias
# =============================================================================

# ⚠️ OBLIGATORIO 1: Tu IP pública
variable "allowed_ssh_cidr" {
  description = "Tu IP pública para acceso SSH (formato: [IP/32])"
  type        = list(string)
}

# ⚠️ OBLIGATORIO 2: Password de PostgreSQL
variable "db_password" {
  description = "Password de PostgreSQL (mínimo 20 caracteres)"
  type        = string
  sensitive   = true
}

# ⚠️ OBLIGATORIO 3: Secret Key para JWT
variable "api_secret_key" {
  description = "Secret key para JWT (mínimo 32 caracteres)"
  type        = string
  sensitive   = true
}

# =============================================================================
# Variables con valores por defecto (NO necesitas cambiarlas)
# =============================================================================

variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "db_name" {
  description = "Nombre de la base de datos"
  type        = string
  default     = "devprofile_db"
}

variable "db_user" {
  description = "Usuario de PostgreSQL"
  type        = string
  default     = "devprofile_user"
}

variable "ami_id" {
  description = "AMI de Ubuntu 22.04 ARM64 en us-east-1"
  type        = string
  default     = "ami-0c02fb55b5c460776"
}
