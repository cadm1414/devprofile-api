## CASOS DE PRUEBA DISEÑADOS

### 1. JWT Generator Service
- ✅ Generar token válido con datos correctos
- ✅ Token contiene payload correcto (user_id, exp)
- ✅ Token expira en el tiempo configurado
- ✅ Algoritmo de firma es correcto
- ❌ Fallar con user_id inválido
- ❌ Fallar con configuración JWT incorrecta

### 2. Password Hasher Service  
- ✅ Hash password correctamente
- ✅ Verificar password correcto
- ❌ Fallar verificación con password incorrecto
- ❌ Fallar con password vacío
- ✅ Hashes diferentes para misma password (salt único)

### 3. User Model
- ✅ Crear usuario con datos válidos
- ✅ Validar email formato correcto
- ❌ Fallar con email inválido
- ❌ Fallar con campos requeridos vacíos
- ✅ Representación string correcta

### 4. Authentication Endpoints
- ✅ Login exitoso con credenciales válidas
- ❌ Login fallido con credenciales incorrectas
- ❌ Login fallido con usuario inexistente
- ✅ Registro exitoso con datos válidos
- ❌ Registro fallido con email duplicado

### 5. User Repository
- ✅ Crear usuario en base de datos
- ✅ Obtener usuario por ID
- ✅ Obtener usuario por email
- ❌ Retornar None con ID inexistente
- ✅ Actualizar datos de usuario
- ✅ Eliminar usuario