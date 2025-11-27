#!/bin/bash

# =============================================================================
# Script de Deployment Manual a AWS EC2
# =============================================================================
# Este script automatiza el proceso de deployment cuando GitHub Actions
# no está disponible o se prefiere deployment manual.
#
# Prerrequisitos:
# - Terraform aplicado (terraform apply)
# - Docker instalado localmente
# - SSH key configurada (~/.ssh/devprofile-aws)
# - Variables de entorno configuradas (ver más abajo)
#
# Uso:
#   ./deploy-manual.sh
# =============================================================================

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Configuración
# =============================================================================

# Obtener IP de EC2 desde Terraform
if [ -d "terraform" ]; then
    cd terraform
    EC2_HOST=$(terraform output -raw instance_public_ip 2>/dev/null || echo "")
    DB_NAME=$(terraform output -raw db_name 2>/dev/null || echo "devprofile_db")
    DB_USER=$(terraform output -raw db_user 2>/dev/null || echo "devprofile_user")
    cd ..
else
    echo -e "${RED}❌ Directorio terraform no encontrado${NC}"
    exit 1
fi

# Validar que tenemos la IP
if [ -z "$EC2_HOST" ]; then
    echo -e "${RED}❌ No se pudo obtener la IP de EC2${NC}"
    echo "Asegúrate de haber ejecutado 'terraform apply' primero"
    exit 1
fi

# Variables de entorno requeridas (cargar desde .env.deploy si existe)
if [ -f ".env.deploy" ]; then
    echo -e "${BLUE}📝 Cargando variables desde .env.deploy${NC}"
    source .env.deploy
fi

# Validar variables requeridas
: ${DB_PASSWORD:?"❌ Variable DB_PASSWORD no definida"}
: ${API_SECRET_KEY:?"❌ Variable API_SECRET_KEY no definida"}

SSH_KEY="${SSH_KEY:-$HOME/.ssh/devprofile-aws}"
DOCKER_IMAGE="${DOCKER_IMAGE:-devprofile-api:latest}"
REMOTE_DIR="/home/ubuntu/devprofile-api"

# =============================================================================
# Funciones
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar conectividad SSH
check_ssh_connection() {
    print_info "Verificando conexión SSH a $EC2_HOST..."
    
    if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@$EC2_HOST "echo 'SSH OK'" &> /dev/null; then
        print_success "Conexión SSH establecida"
        return 0
    else
        print_error "No se pudo conectar vía SSH"
        print_warning "Verifica que:"
        echo "  - La instancia EC2 está corriendo"
        echo "  - Tu IP está en el Security Group"
        echo "  - El archivo SSH key existe: $SSH_KEY"
        return 1
    fi
}

# Construir imagen Docker
build_docker_image() {
    print_header "CONSTRUIR IMAGEN DOCKER"
    
    print_info "Construyendo imagen: $DOCKER_IMAGE"
    
    if docker build -t "$DOCKER_IMAGE" .; then
        print_success "Imagen construida exitosamente"
        
        # Guardar imagen a archivo
        print_info "Guardando imagen a archivo..."
        docker save "$DOCKER_IMAGE" | gzip > devprofile-api.tar.gz
        print_success "Imagen guardada: devprofile-api.tar.gz ($(du -h devprofile-api.tar.gz | cut -f1))"
    else
        print_error "Fallo al construir imagen Docker"
        exit 1
    fi
}

# Copiar archivos a EC2
copy_files_to_ec2() {
    print_header "COPIAR ARCHIVOS A EC2"
    
    print_info "Copiando archivos a $EC2_HOST:$REMOTE_DIR"
    
    # Crear directorio remoto si no existe
    ssh -i "$SSH_KEY" ubuntu@$EC2_HOST "mkdir -p $REMOTE_DIR"
    
    # Copiar archivos
    local files=(
        "devprofile-api.tar.gz"
        "docker-compose.yml"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_info "Copiando $file..."
            if scp -i "$SSH_KEY" "$file" ubuntu@$EC2_HOST:$REMOTE_DIR/; then
                print_success "$file copiado"
            else
                print_error "Fallo al copiar $file"
                exit 1
            fi
        else
            print_warning "$file no encontrado, omitiendo..."
        fi
    done
}

# Desplegar en EC2
deploy_on_ec2() {
    print_header "DESPLEGAR EN EC2"
    
    print_info "Conectando a EC2 para deployment..."
    
    ssh -i "$SSH_KEY" ubuntu@$EC2_HOST << ENDSSH
        set -e
        cd $REMOTE_DIR
        
        echo "📦 Cargando imagen Docker..."
        docker load < devprofile-api.tar.gz
        
        echo "📝 Configurando variables de entorno..."
        cat > .env << EOF
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}
API_SECRET_KEY=${API_SECRET_KEY}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME}
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
EOF
        
        echo "🔄 Deteniendo contenedor anterior..."
        docker-compose down || true
        
        echo "🚀 Iniciando nuevo contenedor..."
        docker-compose up -d
        
        echo "⏳ Esperando a que la API inicie..."
        for i in {1..30}; do
            if curl -f http://localhost:8000/health > /dev/null 2>&1; then
                echo "✅ API está respondiendo!"
                break
            fi
            echo "Intento \$i/30..."
            sleep 2
        done
        
        echo "📊 Estado del contenedor:"
        docker-compose ps
        
        echo "📋 Logs recientes:"
        docker-compose logs --tail=30
        
        echo "🧹 Limpiando archivos temporales..."
        rm -f devprofile-api.tar.gz
        
        echo "🧹 Limpiando imágenes Docker antiguas..."
        docker image prune -f
        
        echo "✅ Deployment completado!"
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "Deployment exitoso"
    else
        print_error "Deployment falló"
        exit 1
    fi
}

# Verificar deployment
verify_deployment() {
    print_header "VERIFICAR DEPLOYMENT"
    
    print_info "Verificando salud de la API..."
    
    ssh -i "$SSH_KEY" ubuntu@$EC2_HOST << 'ENDSSH'
        # Health check
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Health check: OK"
        else
            echo "❌ Health check: FAILED"
            docker-compose logs --tail=50
            exit 1
        fi
        
        # Verificar endpoints
        echo ""
        echo "📡 Verificando endpoints:"
        
        if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
            echo "  ✅ /docs"
        else
            echo "  ❌ /docs"
        fi
        
        if curl -f http://localhost:8000/redoc > /dev/null 2>&1; then
            echo "  ✅ /redoc"
        else
            echo "  ❌ /redoc"
        fi
        
        # Estado de recursos
        echo ""
        echo "💻 Recursos del sistema:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        free -h | grep -E "Mem|Swap"
        echo ""
        df -h / | grep -v Filesystem
        
        # Logs finales
        echo ""
        echo "📋 Últimos logs:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker-compose logs --tail=20
ENDSSH
    
    if [ $? -eq 0 ]; then
        print_success "Verificación completada"
    else
        print_error "Verificación falló"
        exit 1
    fi
}

# Limpiar archivos locales
cleanup_local() {
    print_header "LIMPIEZA LOCAL"
    
    print_info "Eliminando archivos temporales..."
    
    if [ -f "devprofile-api.tar.gz" ]; then
        rm -f devprofile-api.tar.gz
        print_success "devprofile-api.tar.gz eliminado"
    fi
}

# Mostrar información post-deployment
show_deployment_info() {
    print_header "INFORMACIÓN DE DEPLOYMENT"
    
    echo -e "${GREEN}✅ API desplegada exitosamente!${NC}"
    echo ""
    echo "🌐 URLs de acceso:"
    echo "   • API Base:       http://$EC2_HOST"
    echo "   • Swagger Docs:   http://$EC2_HOST/docs"
    echo "   • ReDoc:          http://$EC2_HOST/redoc"
    echo "   • Health Check:   http://$EC2_HOST/health"
    echo ""
    echo "🔗 Conexión SSH:"
    echo "   ssh -i $SSH_KEY ubuntu@$EC2_HOST"
    echo ""
    echo "📊 Comandos útiles:"
    echo "   • Ver logs:       ssh -i $SSH_KEY ubuntu@$EC2_HOST 'cd $REMOTE_DIR && docker-compose logs -f'"
    echo "   • Reiniciar:      ssh -i $SSH_KEY ubuntu@$EC2_HOST 'cd $REMOTE_DIR && docker-compose restart'"
    echo "   • Estado:         ssh -i $SSH_KEY ubuntu@$EC2_HOST 'cd $REMOTE_DIR && docker-compose ps'"
    echo ""
}

# =============================================================================
# Main
# =============================================================================

main() {
    print_header "🚀 DEPLOYMENT MANUAL A AWS EC2"
    
    echo "Configuración:"
    echo "  • EC2 Host:     $EC2_HOST"
    echo "  • SSH Key:      $SSH_KEY"
    echo "  • Image:        $DOCKER_IMAGE"
    echo "  • Remote Dir:   $REMOTE_DIR"
    echo ""
    
    # Confirmar deployment
    read -p "¿Continuar con el deployment? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelado"
        exit 0
    fi
    
    # Ejecutar pasos del deployment
    check_ssh_connection || exit 1
    build_docker_image
    copy_files_to_ec2
    deploy_on_ec2
    verify_deployment
    cleanup_local
    show_deployment_info
    
    print_success "🎉 DEPLOYMENT COMPLETADO EXITOSAMENTE!"
}

# Ejecutar main
main "$@"
