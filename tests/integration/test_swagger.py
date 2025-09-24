from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import settings

client = TestClient(app)

def test_docs_swagger_ui():
    """Verifica que Swagger UI (docs) esté disponible"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text

def test_docs_redoc():
    """Verifica que ReDoc esté disponible"""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "ReDoc" in response.text

def test_openapi_schema():
    """Verifica que el esquema OpenAPI JSON esté disponible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    expected_path = f"{settings.API_PREFIX}/auth/access"
    assert expected_path in schema["paths"]
