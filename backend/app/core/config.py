"""Configuration de l'application avec Pydantic Settings."""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from pydantic import BaseSettings, validator
from pathlib import Path
import os


class Settings(BaseSettings):
    """Configuration de l'application."""
    
    # Configuration de base
    APP_NAME: str = "Waste Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Base de données
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    
    # JWT et sécurité
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Chiffrement biométrique
    BIOMETRIC_ENCRYPTION_KEY: str
    
    # Redis
    REDIS_URL: str
    
    # Socket.IO
    SOCKETIO_SECRET_KEY: str
    
    # Notifications push
    FCM_SERVER_KEY: str
    FCM_SENDER_ID: str
    
    # CORS
    CORS_ORIGINS: List[str] = []
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Reconnaissance faciale
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    FACE_RECOGNITION_MODEL: str = "large"
    
    # Répertoires
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    FACE_ENCODINGS_DIR: Path = BASE_DIR / "face_encodings"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Assembler les origines CORS."""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("UPLOAD_DIR", "FACE_ENCODINGS_DIR", "LOGS_DIR", pre=True)
    def ensure_directories_exist(cls, v):
        """Créer les répertoires s'ils n'existent pas."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale de configuration
settings = Settings()