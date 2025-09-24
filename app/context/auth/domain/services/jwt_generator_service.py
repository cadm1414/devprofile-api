from jose import jwt
from datetime import datetime, timedelta, UTC
from app.config.settings import settings

def generate_jwt(user_id: int, user_name: str, email: str) -> str:
    if not user_id:
        raise ValueError("User ID inválido")

    secret = settings.JWT_SECRET_KEY["key"]
    if not secret:
        raise ValueError("JWT Secret no configurado")
    
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_SECRET_KEY["expires"])
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, secret, algorithm=settings.JWT_SECRET_KEY["algorithm"])

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY["key"], algorithms=[settings.JWT_SECRET_KEY["algorithm"]])
