from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    API_PREFIX: str
    ORIGINS:str
    DB_DRIVER: str
    DB_HOST: str
    DB_NAME: str
    DB_AUTH: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def DATABASE_URL(self):
        return f"mssql+pyodbc://{self.DB_HOST}/{self.DB_NAME}?driver={self.DB_DRIVER}&{self.DB_AUTH}"
    
    @property
    def JWT_SECRET_KEY(self):
        return {"key": self.SECRET_KEY, "algorithm": self.ALGORITHM, "expires": self.ACCESS_TOKEN_EXPIRE_MINUTES}
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:               
        return self.ORIGINS.split(",")

    class Config:
        env_file = ".env"  

settings = Settings()