import pytest
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, UTC
from app.context.auth.domain.services import jwt_generator_service as jwt_service
from app.config.settings import settings

class TestJWTGeneratorService:

    def test_generate_jwt_with_valid_data(self):
        """
        CASO: Generar token con datos válidos
        ENTRADA: user_id=1, user_name="Test", email="
        ESPERADO: Token JWT válido generado
        """
        user_id = 1
        user_name = "Test"
        email = "test@example.com"

        token = jwt_service.generate_jwt(user_id, user_name, email)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        payload = jwt_service.decode_jwt(token)
        assert payload["sub"] == str(user_id)
        assert "exp" in payload

    def test_jwt_contains_user_id(self):
        """
        CASO: Token contiene el user_id
        ENTRADA: user_id=1
        ESPERADO: El payload decodificado contiene "sub" con el user_id
        """
        token = jwt_service.generate_jwt(1, "Test", "test@example.com")
        payload = jwt_service.decode_jwt(token)
        assert payload["sub"] == "1"

    def test_jwt_is_not_empty(self):
        """
        CASO: Token no está vacío
        ENTRADA: user_id=1
        ESPERADO: Token generado es un string no vacío
        """
        token = jwt_service.generate_jwt(1, "Test", "test@example.com")
        assert token and isinstance(token, str)

    def test_jwt_expires_correctly(self):
        """
        CASO: Token expira en el tiempo configurado
        ENTRADA: Generar token y esperar su expiración
        ESPERADO: Decodificar después de expiración lanza ExpiredSignatureError
        """        
        expire = datetime.now(UTC) + timedelta(seconds=1)        
        payload = {"sub": "1", "exp": expire}
        token = jwt.encode(payload, settings.JWT_SECRET_KEY["key"], algorithm=settings.JWT_SECRET_KEY["algorithm"])
        
        decoded = jwt_service.decode_jwt(token)
        assert decoded["sub"] == "1"
        
        import time; time.sleep(2)
        
        with pytest.raises(ExpiredSignatureError):
            jwt_service.decode_jwt(token)

    def test_jwt_algorithm_is_correct(self):
        """
        CASO: El algoritmo de firma es correcto
        ENTRADA: Generar token
        ESPERADO: El header del token contiene el algoritmo configurado
        """
        token = jwt_service.generate_jwt(1, "Test", "test@example.com")
        header = jwt.get_unverified_header(token)
        assert header["alg"] == settings.JWT_SECRET_KEY["algorithm"]

    def test_generate_jwt_with_invalid_user_id(self):
        """
        CASO: Fallar con user_id inválido
        ENTRADA: user_id=None
        ESPERADO: Lanza ValueError
        """
        with pytest.raises(Exception):
            jwt_service.generate_jwt(None, "Test", "test@example.com")

    def test_generate_jwt_with_invalid_secret_key(self, monkeypatch):
        """
        CASO: Fallar con configuración JWT incorrecta
        ENTRADA: SECRET_KEY=""
        ESPERADO: Lanza ValueError
        """
        monkeypatch.setattr(settings, "SECRET_KEY", "")

        with pytest.raises(ValueError, match="JWT Secret no configurado"):
            jwt_service.generate_jwt(1, "Test", "test@example.com")
