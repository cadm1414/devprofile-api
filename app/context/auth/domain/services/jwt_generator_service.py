from jose import jwt
from datetime import datetime, timedelta
from app.config.settings import settings

def generate_jwt(user_id: int, user_name: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_SECRET_KEY["expires"])
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY["key"], algorithm=settings.JWT_SECRET_KEY["algorithm"])