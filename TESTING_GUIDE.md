# Guía de Testing: DevProfile API

Esta guía describe cómo ejecutar, extender y analizar las pruebas unitarias, de integración y de performance del proyecto.

---

## 1. Pruebas Unitarias y de Integración (pytest + pydantic)

### Estructura

- `tests/unit/` — Pruebas unitarias de servicios, lógica y utilidades
- `tests/integration/` — Pruebas de endpoints y flujos completos

### Ejemplo de prueba unitaria (servicio JWT)
```python
from app.context.auth.domain.services.jwt_generator_service import generate_jwt
def test_generate_jwt_returns_string():
	token = generate_jwt(1, "Test", "test@test.com")
	assert isinstance(token, str)
	assert len(token) > 0
```

### Ejemplo de prueba de settings con Pydantic
```python
from app.config.settings import Settings
def test_settings_database_url():
	s = Settings(DB_HOST="localhost", DB_PORT=5432, DB_NAME="test", DB_USER="u", DB_PASSWORD="p", API_PREFIX="/api", ORIGINS="*", SECRET_KEY="x", ALGORITHM="HS256", ACCESS_TOKEN_EXPIRE_MINUTES=10)
	assert s.DATABASE_URL.startswith("postgresql://")
```

### Comandos útiles
```bash
# Ejecutar todas las pruebas
pytest
# Ejecutar solo unitarias
pytest tests/unit/ -v
# Ejecutar solo integración
pytest tests/integration/ -v
```

---

## 2. Cobertura de Código (pytest-cov / coverage.py)

### Ejecutar con cobertura
```bash
pytest --cov=app --cov-report=term-missing
pytest --cov=app --cov-report=html
start htmlcov/index.html  # Windows
```

### Meta de cobertura
- 80%+ (fallo si es menor, ver pytest.ini)
- Reporte HTML en `htmlcov/index.html`

---

## 3. Pruebas de Performance (Locust)

### Estructura
- `performance/locustfile_login_test.py` — Stress test de login
- `performance/locustfile_identity_test.py` — Stress test de endpoints de usuario

### Ejemplo de archivo Locust
```python
from locust import HttpUser, task
class LoginUser(HttpUser):
	@task
	def login(self):
		self.client.post("/api/v1/auth/access", json={"email": "test@test.com", "password": "123"})
```

### Ejecutar pruebas de carga
```bash
pip install locust
locust -f performance/locustfile_login_test.py --host http://localhost:8000
locust -f performance/locustfile_identity_test.py --host http://localhost:8000
```

### Consejos para Locust
- Usa múltiples usuarios y contraseñas para simular concurrencia real
- Valida respuestas y maneja errores (401, 500, etc)
- Ajusta `wait_time` para simular usuarios reales

---

## 4. Pruebas de API con Newman (Postman CLI)

### Estructura
- `newman/tests/DEVPROFILE-API.postman_collection.json` — Colección Postman con endpoints

### Ejecutar pruebas de API
```bash
npm install -g newman
newman run newman/tests/DEVPROFILE-API.postman_collection.json --host http://localhost:8000
```

### Ejemplo de test en Postman
```javascript
// Test en la pestaña "Tests" de Postman
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has access_token", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access_token');
});
```

---

## 5. Integración Continua con GitHub Actions

### Workflows implementados

#### 🔬 **Pruebas Unitarias** (`.github/workflows/test.yml`)
```yaml
# Se ejecuta en push/PR a main, develop, feature/test-unitarios
# Pasos:
1. Setup Python 3.11
2. Instalar dependencias (requirements.txt) 
3. Crear .env desde secrets de GitHub
4. Ejecutar pytest con cobertura
```

#### 🌐 **Pruebas de API** (`.github/workflows/newman-test.yml`)
```yaml
# Se ejecuta en push/PR a main, develop
# Pasos:
1. Setup Python 3.11 + Node.js 20
2. Instalar dependencias Python y Newman
3. Crear .env desde secrets
4. Levantar FastAPI server en background
5. Ejecutar tests Newman
6. Generar reporte HTML
```

### Configurar secrets en GitHub
1. Ve a tu repo → Settings → Secrets and variables → Actions
2. Agrega `ENV_TEST` con el contenido de tu archivo `.env`

### Ejecutar workflows localmente
```bash
# Simular workflow de pytest
pytest --cov=app --cov-report=term-missing

# Simular workflow de newman
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
newman run newman/tests/DEVPROFILE-API.postman_collection.json
```

---

## 6. Configuración de pytest.ini

```ini
[pytest]
pythonpath = .
addopts = --cov=app --cov-report=term-missing
norecursedirs = performance  # Excluye carpeta de Locust
```

---

## 7. Buenas Prácticas

- **Testing:** Usa nombres descriptivos para los tests
- **Isolación:** Aísla dependencias externas (mocks/fakes)  
- **Performance:** Mantén las pruebas rápidas (<1s)
- **Assertions:** Usa asserts claros y específicos
- **Documentación:** Documenta casos de prueba complejos
- **CI/CD:** Automatiza la ejecución en todos los PRs
- **Secrets:** No hardcodees credenciales, usa GitHub Secrets
- **Reports:** Genera reportes HTML para análisis visual

---

## 8. Recursos

- [pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [coverage.py](https://coverage.readthedocs.io/)
- [pydantic](https://docs.pydantic.dev/)
- [locust](https://docs.locust.io/)
- [newman](https://learning.postman.com/docs/running-collections/using-newman-cli/)
- [GitHub Actions](https://docs.github.com/en/actions)
