# DevProfile API

## Descripción
API REST para la creación y gestión de perfiles profesionales. Permite a los usuarios registrarse, autenticarse y gestionar sus perfiles con información profesional completa incluyendo experiencia laboral, educación, habilidades, proyectos y contactos.

## Características

- 🔐 Sistema de autenticación JWT
- 👤 Gestión de usuarios
- 📋 Perfiles profesionales completos
- 💼 Experiencia laboral
- 🎓 Información educativa
- 🛠️ Habilidades técnicas
- 📱 Múltiples contactos (email, teléfono)
- 🌐 Redes sociales
- 🚀 Proyectos

## Tecnologías

- **Framework**: FastAPI
- **Base de Datos**: SQL Server
- **ORM**: SQLAlchemy
- **Autenticación**: JWT (JSON Web Tokens)
- **Validación**: Pydantic
- **Hash de Contraseñas**: Passlib con bcrypt
- **CORS**: FastAPI CORS Middleware

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
│   ├── database.py            # Configuración de base de datos
│   └── settings.py            # Variables de entorno
├── middleware/                 # Middlewares personalizados
│   └── jwt_middleware.py      # Middleware de autenticación JWT
├── common/                     # Dependencias compartidas
│   └── dependencies.py        # Inyección de dependencias
└── context/                    # Contextos de dominio
    ├── auth/                   # Contexto de Autenticación
    │   ├── api/
    │   │   ├── routes/         # Rutas/Controladores
    │   │   └── schemas/        # DTOs/Esquemas de validación
    │   ├── application/
    │   │   └── usecases/       # Casos de uso
    │   └── domain/
    │       └── services/       # Servicios de dominio
    ├── identity/               # Contexto de Identidad/Usuarios
    │   ├── api/
    │   │   ├── routes/
    │   │   └── schemas/
    │   ├── application/
    │   │   └── usecases/
    │   ├── domain/
    │   │   ├── models/         # Entidades del dominio
    │   │   └── repositories/   # Interfaces de repositorio
    │   └── infrastructure/
    │       └── repositories/   # Implementación de repositorios
    └── user_profile/           # Contexto de Perfiles de Usuario
        └── domain/
            └── models/         # Modelos de perfil profesional
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
- SQL Server
- Driver ODBC 17 para SQL Server

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/cadm1414/devprofile-api.git
   cd devprofile-api
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install sqlalchemy
   pip install pydantic-settings
   pip install fastapi uvicorn[standard] python-dotenv
   pip install pyodbc
   pip install pydantic[email]
   pip install passlib[bcrypt]
   pip install python-jose[cryptography]
   ```

4. **Configurar variables de entorno**:
   
   Crear archivo `.env` en la raíz del proyecto:
   ```env
   # PREFIX ROUTE
   API_PREFIX=/api/v1
   ORIGINS=*

   # DATABASE
   DB_DRIVER=ODBC+Driver+17+for+SQL+Server
   DB_HOST=localhost
   DB_NAME=profile_db
   DB_AUTH=trusted_connection=yes

   # JWT
   SECRET_KEY=tu_clave_secreta_aqui
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Ejecutar la aplicación**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Endpoints Principales

### Autenticación
- `POST /api/v1/auth/access` - Iniciar sesión

### Gestión de Usuarios
- `POST /api/v1/identity/register` - Registrar usuario
- `GET /api/v1/identity/users/{user_id}` - Obtener usuario
- `PUT /api/v1/identity/users/{user_id}` - Actualizar usuario
- `DELETE /api/v1/identity/users/{user_id}` - Eliminar usuario

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

## Estructura de Base de Datos

La base de datos se crea automáticamente al iniciar la aplicación. Las tablas principales son:

- `users` - Usuarios del sistema
- `profiles` - Perfiles profesionales
- `educations` - Formación académica
- `work_experiences` - Experiencia laboral
- `skills` - Habilidades
- `projects` - Proyectos
- `emails` - Emails de contacto
- `phones` - Teléfonos
- `social_networks` - Redes sociales

## Seguridad

- **Autenticación JWT**: Tokens seguros con expiración configurable
- **Hash de Contraseñas**: bcrypt para almacenamiento seguro
- **Middleware de Autenticación**: Protección automática de rutas
- **CORS**: Configuración de orígenes permitidos
- **Validación de Datos**: Pydantic para validación automática

## Autor

**CARLOS ALBERTO DIAZ MINAYA**
- Email: cdiazm14@gmail.com
- LinkedIn: www.linkedin.com/in/cdiazm14
- GitHub: [cadm1414](https://github.com/cadm1414)

## Repositorio

🔗 **GitHub**: https://github.com/cadm1414/devprofile-api.git

---

*Desarrollado aplicando principios de abstracción, POO, SOLID, código limpio y Domain Driven Design (DDD)*
