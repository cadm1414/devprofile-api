# DevProfile API

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-9.6+-336791.svg)](https://postgresql.org)
[![Testing](https://img.shields.io/badge/Testing-pytest-green.svg)](https://pytest.org)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-success.svg)](https://coverage.readthedocs.io)

## Descripción
API REST para la creación y gestión de perfiles profesionales. Permite a los usuarios registrarse, autenticarse y gestionar sus perfiles con información profesional completa incluyendo experiencia laboral, educación, habilidades, proyectos y contactos.

## Características

- 🔐 Sistema de autenticación JWT con middleware personalizado
- 👤 Gestión completa de usuarios con roles
- 📋 Perfiles profesionales completos
- 💼 Experiencia laboral detallada
- 🎓 Información educativa y certificaciones
- 🛠️ Habilidades técnicas y profesionales
- 📱 Múltiples contactos (email, teléfono)
- 🌐 Redes sociales y portfolio
- 🚀 Proyectos con tecnologías utilizadas
- ✅ **Suite de Pruebas Unitarias** con pytest
- 📊 **Cobertura de Código** con coverage.py
- 🐘 **Base de datos PostgreSQL** para mejor escalabilidad
- 🚀 **Deployment ready** para múltiples plataformas cloud

## Tecnologías

- **Framework**: FastAPI 0.104.1
- **Base de Datos**: PostgreSQL 9.6+ (migrado desde SQL Server)
- **ORM**: SQLAlchemy 2.0.23
- **Autenticación**: JWT (JSON Web Tokens) con python-jose
- **Validación**: Pydantic 2.5.0 con Pydantic Settings
- **Hash de Contraseñas**: Passlib con bcrypt
- **CORS**: FastAPI CORS Middleware
- **Testing**: pytest 7.4.0 con pytest-cov 4.1.0
- **Database Driver**: psycopg2-binary 2.9.7
- **Deployment**: Docker + Fly.io/Render ready

## Arquitectura

El proyecto implementa **Domain Driven Design (DDD)** con los siguientes principios:

### Principios de Diseño Aplicados

- **🏗️ Abstracción**: Interfaces y clases abstractas para definir contratos claros
- **🎯 Programación Orientada a Objetos (POO)**: Encapsulación, herencia y polimorfismo
- **⚡ Principios SOLID**:
  - **S**ingle Responsibility: Cada clase tiene una responsabilidad única
  - **O**pen/Closed: Abierto para extensión, cerrado para modificación
  - **L**iskov Substitution: Los objetos derivados pueden sustituir a los base
  - **I**nterface Segregation: Interfaces específicas y pequeñas
  - **D**ependency Inversion: Dependencias hacia abstracciones
- **🧹 Código Limpio**: Nombres descriptivos, funciones pequeñas, estructura clara

### Estructura por Contextos

```
app/
├── main.py                     # Punto de entrada de la aplicación
├── config/                     # Configuración global
│   ├── database.py            # Configuración PostgreSQL con SQLAlchemy
│   └── settings.py            # Variables de entorno con Pydantic Settings
├── middleware/                 # Middlewares personalizados
│   └── jwt_middleware.py      # Middleware de autenticación JWT
├── common/                     # Dependencias compartidas
│   ├── dependencies.py        # Inyección de dependencias
│   └── security/              # Servicios de seguridad
│       └── password_hasher.py # Hash y verificación de contraseñas
└── context/                    # Contextos de dominio
    ├── auth/                   # Contexto de Autenticación
    │   ├── api/
    │   │   ├── routes/         # Rutas/Controladores
    │   │   └── schemas/        # DTOs/Esquemas de validación
    │   ├── application/
    │   │   └── usecases/       # Casos de uso
    │   └── domain/
    │       └── services/       # Servicios de dominio (JWT Generator)
    ├── identity/               # Contexto de Identidad/Usuarios
    │   ├── api/
    │   │   ├── routes/         # CRUD de usuarios con endpoints protegidos
    │   │   └── schemas/        # Esquemas de request/response
    │   ├── application/
    │   │   └── usecases/       # Casos de uso (registro, actualización)
    │   ├── domain/
    │   │   ├── models/         # Entidades del dominio (User)
    │   │   └── repositories/   # Interfaces de repositorio
    │   └── infrastructure/
    │       └── repositories/   # Implementación de repositorios
    └── user_profile/           # Contexto de Perfiles de Usuario
        └── domain/
            └── models/         # Modelos de perfil profesional

tests/                          # Suite de Pruebas Unitarias
├── unit/                      # Pruebas unitarias
│   ├── test_generator_service.py  # Pruebas JWT Generator
│   └── test_password_service.py   # Pruebas Password Hasher
└── integration/               # Pruebas de integración
    └── test_swagger.py        # Pruebas endpoints públicos
```

## Modelos de Datos

### Usuario (Identity Context)
- Información básica del usuario
- Email único
- Contraseña hasheada
- Estado activo/inactivo

### Perfil Profesional (User Profile Context)
- **Profile**: Información personal y profesional
- **Education**: Formación académica
- **WorkExperience**: Experiencia laboral
- **Skill**: Habilidades técnicas
- **Project**: Proyectos realizados
- **Email**: Emails de contacto
- **PhoneNumber**: Números telefónicos
- **SocialNetwork**: Redes sociales

## Instalación

### Prerrequisitos
- Python 3.11+
- PostgreSQL 9.6+ (reemplazó SQL Server para mejor compatibilidad cloud)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/cadm1414/devprofile-api.git
   cd devprofile-api
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   
   Crear archivo `.env` basado en `.env-example`:
   ```bash
   cp .env-example .env
   ```
   
   Editar `.env` con tus configuraciones:
   ```env
   # PREFIX ROUTE
   API_PREFIX=/api/v1
   ORIGINS=*

   # DATABASE - PostgreSQL Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=profile_db
   DB_USER=your_username
   DB_PASSWORD=your_password

   # JWT
   SECRET_KEY=your-super-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Configurar PostgreSQL**:
   ```sql
   -- Crear base de datos
   CREATE DATABASE profile_db;
   
   -- Crear usuario (opcional)
   CREATE USER your_username WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE profile_db TO your_username;
   ```

6. **Ejecutar la aplicación**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Testing y Cobertura

## Testing: Unitarias, Cobertura y Performance

### 🔬 Pruebas Unitarias y de Integración

- **Framework:** [pytest](https://pytest.org/) + [pytest-cov](https://pytest-cov.readthedocs.io/)
- **Validación:** [Pydantic](https://docs.pydantic.dev/) (modelos y settings)
- **Cobertura:** [coverage.py](https://coverage.readthedocs.io/)
- **Performance:** [Locust](https://locust.io/) (carga y stress)

#### Ejecución rápida
```bash
# Ejecutar todas las pruebas unitarias y de integración
pytest

# Ejecutar con cobertura de código
pytest --cov=app --cov-report=term-missing

# Reporte HTML de cobertura
pytest --cov=app --cov-report=html
start htmlcov/index.html  # Windows

# Pruebas unitarias específicas
pytest tests/unit/ -v
# Pruebas de integración
pytest tests/integration/ -v
```

#### Ejemplo de prueba unitaria con Pydantic
```python
from app.config.settings import Settings
def test_settings_database_url():
   s = Settings(DB_HOST="localhost", DB_PORT=5432, DB_NAME="test", DB_USER="u", DB_PASSWORD="p", API_PREFIX="/api", ORIGINS="*", SECRET_KEY="x", ALGORITHM="HS256", ACCESS_TOKEN_EXPIRE_MINUTES=10)
   assert s.DATABASE_URL.startswith("postgresql://")
```

#### Métricas de cobertura
- **Meta:** 80%+ (configurada en pytest.ini)
- **Reporte HTML:** `htmlcov/index.html`
- **Servicios de dominio:** 95%+
- **Configuración:** 90%+
- **Endpoints públicos:** 100%

---

### 🏋️‍♂️ Pruebas de Performance con Locust

**Ubicación:** `performance/locustfile_login_test.py`, `performance/locustfile_identity_test.py`

#### Ejecutar pruebas de carga
```bash
# Instalar locust si no lo tienes
pip install locust

# Ejecutar prueba de login
locust -f performance/locustfile_login_test.py --host http://localhost:8000

# Ejecutar prueba de endpoints de usuario
locust -f performance/locustfile_identity_test.py --host http://localhost:8000
```

#### Ejemplo de test Locust
```python
from locust import HttpUser, task
class LoginUser(HttpUser):
   @task
   def login(self):
      self.client.post("/api/v1/auth/access", json={"email": "test@test.com", "password": "123"})
```

---

### 📄 Más detalles y ejemplos en [TESTING_GUIDE.md](TESTING_GUIDE.md)

## Endpoints Principales

### Autenticación
- `POST /api/v1/auth/access` - Iniciar sesión (devuelve JWT token)

### Gestión de Usuarios
- `POST /api/v1/identity/register` - Registrar nuevo usuario
- `GET /api/v1/identity/me` - Obtener información del usuario autenticado 🔒
- `PUT /api/v1/identity/me/password` - Actualizar contraseña del usuario 🔒
- `GET /api/v1/identity/users/{user_id}` - Obtener usuario por ID 🔒
- `PUT /api/v1/identity/users/{user_id}` - Actualizar usuario 🔒
- `DELETE /api/v1/identity/users/{user_id}` - Eliminar usuario 🔒

### Documentación
- `GET /docs` - Swagger UI (Documentación interactiva)
- `GET /redoc` - ReDoc (Documentación alternativa)

🔒 = Requiere autenticación JWT

## Desarrollo y Testing

### Comandos de Desarrollo

```bash
# Ejecutar servidor en modo desarrollo
uvicorn app.main:app --reload

# Ejecutar pruebas con watch mode
pytest --watch

# Generar reporte de cobertura
pytest --cov=app --cov-report=html
open htmlcov/index.html  # Ver reporte

# Linting y formato (si está configurado)
black app/
flake8 app/
```

### Scripts Útiles

```bash
# Script para ejecutar todas las pruebas
python run_tests.py

# Verificar configuración de BD
python -c "from app.config.database import test_connection; test_connection()"

# Verificar variables de entorno
python -c "from app.config.settings import settings; print(settings.DATABASE_URL)"
```

## Uso

### Registrar Usuario
```bash
POST /api/v1/identity/register
{
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Completo",
  "password": "contraseña123"
}
```

### Iniciar Sesión
```bash
POST /api/v1/auth/access
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

### Acceder a Endpoints Protegidos
Incluir en las cabeceras:
```
Authorization: Bearer {token_jwt}
```

## Documentación API

Una vez ejecutada la aplicación, la documentación interactiva estará disponible en:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Estructura de Base de Datos (PostgreSQL)

La base de datos PostgreSQL se inicializa automáticamente al ejecutar la aplicación. Las tablas principales son:

### Tablas del Sistema
- `users` - Usuarios del sistema con autenticación
- `profiles` - Perfiles profesionales detallados
- `educations` - Formación académica y certificaciones
- `work_experiences` - Historia laboral profesional
- `skills` - Habilidades técnicas y profesionales
- `projects` - Proyectos desarrollados
- `emails` - Emails de contacto múltiples
- `phones` - Números telefónicos
- `social_networks` - Enlaces a redes sociales

### Migración de SQL Server a PostgreSQL

El proyecto fue migrado exitosamente de SQL Server a PostgreSQL para:
- ✅ **Mejor compatibilidad** con plataformas cloud
- ✅ **Costo reducido** en deployment
- ✅ **Rendimiento optimizado** para aplicaciones web
- ✅ **Facilidad de configuración** en contenedores
- ✅ **Ecosistema open source** robusto

## Deployment

### Plataformas Soportadas

El proyecto incluye configuraciones para múltiples plataformas:

#### Fly.io
```bash
# Deployment en Fly.io
fly deploy
```
Configuración en `fly.toml`

#### Render
```bash
# Auto-deploy desde GitHub
```
Configuración en `render.yaml`

#### Docker
```bash
# Build imagen
docker build -t devprofile-api .

# Ejecutar contenedor
docker run -p 8000:8000 devprofile-api
```

### Variables de Entorno para Producción

```env
# Configuración PostgreSQL en producción
DB_HOST=your-postgres-host
DB_PORT=5432
DB_NAME=devprofile_prod
DB_USER=postgres_user
DB_PASSWORD=secure_password

# JWT en producción
SECRET_KEY=super-secure-production-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API Configuration
ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Seguridad

- **Autenticación JWT**: Tokens seguros con expiración configurable
- **Middleware personalizado**: Verificación automática de tokens
- **Hash de Contraseñas**: bcrypt con salt para máxima seguridad
- **CORS configurado**: Control de orígenes permitidos
- **Validación robusta**: Pydantic para sanitización de datos
- **Variables de entorno**: Configuración sensible protegida
- **PostgreSQL**: Preparado para SSL en producción

## Documentos Adicionales

- 📋 [CASOS_PRUEBA_UNITARIOS.md](CASOS_PRUEBA_UNITARIOS.md) - Casos de prueba detallados
- 🧪 [TESTING_GUIDE.md](TESTING_GUIDE.md) - Guía completa de testing
- 🐘 [POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md) - Detalles de migración de BD
- 🚀 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Guía de deployment
- 📄 [devprofile-postman.json](devprofile-postman.json) - Colección Postman

## Autor

**CARLOS ALBERTO DIAZ MINAYA**
- Email: cdiazm14@gmail.com
- LinkedIn: www.linkedin.com/in/cdiazm14
- GitHub: [cadm1414](https://github.com/cadm1414)

## Repositorio

🔗 **GitHub**: https://github.com/cadm1414/devprofile-api.git

## Tecnologías y Versiones

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| FastAPI | 0.104.1 | Framework web principal |
| PostgreSQL | 9.6+ | Base de datos principal |
| SQLAlchemy | 2.0.23 | ORM y manejo de BD |
| Pydantic | 2.5.0 | Validación y serialización |
| pytest | 7.4.0 | Framework de testing |
| python-jose | 3.3.0 | Manejo de JWT tokens |
| psycopg2-binary | 2.9.7 | Driver PostgreSQL |
| bcrypt | - | Hash de contraseñas |

## Estado del Proyecto

### 🎯 Versión Actual: 2.0.0

#### ✅ Cambios Importantes (v2.0.0)
- **Migración completa** de SQL Server a PostgreSQL 9.6+
- **Suite de pruebas unitarias** implementada con pytest
- **Cobertura de código** configurada con coverage.py (meta: 80%)
- **Middleware JWT personalizado** mejorado con manejo de errores
- **Configuración Pydantic Settings** modernizada
- **Docker y deployment** optimizado para múltiples clouds
- **Documentación** completamente actualizada

#### 🔄 En Desarrollo
- Pruebas E2E completas
- CI/CD pipeline con GitHub Actions
- Monitoreo y logging avanzado
- Autenticación con roles y permisos

#### � Backlog
- API de perfiles profesionales completa
- Integración con servicios de terceros
- Panel de administración
- API versioning

---

*Desarrollado aplicando principios de abstracción, POO, SOLID, código limpio, Domain Driven Design (DDD) y mejores prácticas de testing*
