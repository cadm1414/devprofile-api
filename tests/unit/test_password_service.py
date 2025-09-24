# tests/unit/test_password_service.py
import pytest
from app.context.auth.domain.services import password_service

class TestPasswordService:

    def test_hash_password_correctly(self):
        """
        CASO: Hash password correctamente
        ENTRADA: "mypassword"
        ESPERADO: Devuelve un string distinto al original
        """
        password = "mypassword"
        hashed = password_service.hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  

    def test_verify_password_correct(self):
        """
        CASO: Verificar password correcto
        ENTRADA: password="mypassword"
        ESPERADO: verify_password devuelve True
        """
        password = "mypassword"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """
        CASO: Fallar verificación con password incorrecto
        ENTRADA: password="mypassword", intento="wrongpass"
        ESPERADO: verify_password devuelve False
        """
        password = "mypassword"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password("wrongpass", hashed) is False

    def test_verify_password_empty(self):
        """
        CASO: Fallar con password vacío
        ENTRADA: password=""
        ESPERADO: verify_password devuelve False
        """
        password = "mypassword"
        hashed = password_service.hash_password(password)

        assert password_service.verify_password("", hashed) is False

    def test_hashes_are_different_for_same_password(self):
        """
        CASO: Hashes diferentes para misma password (salt único)
        ENTRADA: dos veces el mismo password
        ESPERADO: hashes distintos
        """
        password = "mypassword"
        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)

        assert hash1 != hash2
