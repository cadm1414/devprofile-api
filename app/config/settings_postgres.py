from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    API_PREFIX: str
    ORIGINS: str
    
    # PostgreSQL Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    # JWT Configuration  
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Detectar entorno
    ENVIRONMENT: str = os.getenv("FLY_APP_NAME", os.getenv("RENDER", "development"))

    @property
    def DATABASE_URL(self):
        # URL de conexión PostgreSQL optimizada para version 9.6
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode=prefer&application_name=devprofile-api"
    
    @property
    def JWT_SECRET_KEY(self):
        return {"key": self.SECRET_KEY, "algorithm": self.ALGORITHM, "expires": self.ACCESS_TOKEN_EXPIRE_MINUTES}
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:               
        return [origin.strip() for origin in self.ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
