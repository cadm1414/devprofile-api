from pydantic_settings import BaseSettings
from typing import List, Optional
import urllib.parse
import os

class Settings(BaseSettings):
    API_PREFIX: str
    ORIGINS: str
    DB_DRIVER: str
    DB_HOST: str
    DB_PORT: int = 1433
    DB_NAME: str
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_AUTH: Optional[str] = None
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Detectar entorno
    ENVIRONMENT: str = os.getenv("FLY_APP_NAME", "development")

    @property
    def DATABASE_URL(self):        
        if self.DB_USER and self.DB_PASSWORD:
            password = urllib.parse.quote_plus(self.DB_PASSWORD)            
            user = urllib.parse.quote_plus(self.DB_USER)
                        
            driver = "ODBC+Driver+18+for+SQL+Server" if os.getenv("FLY_APP_NAME") else self.DB_DRIVER
            
            return f"mssql+pyodbc://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?driver={driver}&Encrypt=no&TrustServerCertificate=yes"
        
        return f"mssql+pyodbc://{self.DB_HOST}/{self.DB_NAME}?driver={self.DB_DRIVER}&{self.DB_AUTH}"
    
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