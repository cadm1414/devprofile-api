# Deployment en AWS con Terraform

## 🚀 Opción 1: Script Automático (Recomendado)

```powershell
.\deploy.ps1
```

El script hace todo automáticamente:
- ✅ Verifica pre-requisitos
- ✅ Obtiene tu IP y genera passwords
- ✅ Configura y despliega en AWS
- ✅ Te da la URL de tu API

⏱️ Tiempo: 5-10 minutos

---

## 🛠️ Opción 2: Manual

### Paso 1: Configurar terraform.tfvars
```powershell
# Obtener tu IP
(Invoke-WebRequest ifconfig.me).Content

# Copiar y editar configuración
Copy-Item terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars

# Editar solo 3 valores:
# - allowed_ssh_cidr (tu IP)
# - db_password (password seguro)
# - api_secret_key (secret key seguro)
```

### Paso 2: Desplegar
```powershell
terraform init
terraform plan
terraform apply
```

### Paso 3: Ver información
```powershell
terraform output public_ip
terraform output api_url
terraform output ssh_command
```

---

## 📋 Contenido Desplegado

---

## 📋 Recursos Desplegados

- **EC2 Instance:** t4g.micro ARM (Free Tier eligible)
- **Storage:** 20GB gp3
- **PostgreSQL:** 14 (instalado en EC2)
- **Docker + Nginx:** Configurados automáticamente
- **Elastic IP:** IP estática
- **Security Groups:** SSH (tu IP), HTTP/HTTPS (público)
- **CloudWatch:** Monitoreo básico

**Costo estimado:** ~$5.55/mes (~$33 por 6 meses)
**Con Free Tier:** ~$2/mes primeros 12 meses

---

## 🔧 Comandos Útiles

### Ver estado
```powershell
terraform output
terraform show
```

### Conectar a EC2
```powershell
terraform output ssh_command | Invoke-Expression
```

### Destruir todo
```powershell
terraform destroy
```

---

## 🆘 Troubleshooting

### Error de conexión SSH
```powershell
# Actualizar tu IP en terraform.tfvars
terraform apply
```

### Ver logs de inicialización
```powershell
ssh -i devprofile-aws-key.pem ubuntu@$(terraform output -raw public_ip)
tail -f /var/log/user-data.log
```

---

**💰 Costo:** ~$20-33 por 6 meses  
**📚 Docs completas:** Ver archivos en directorio raíz del proyecto
