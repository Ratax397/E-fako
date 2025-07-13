"""Modèle User pour la base de données."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, LargeBinary, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from typing import Optional

from app.core.database import Base


class UserRole(enum.Enum):
    """Rôles des utilisateurs."""
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    USER = "user"


class UserStatus(enum.Enum):
    """Statuts des utilisateurs."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """Modèle utilisateur."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Informations personnelles
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    
    # Données biométriques (chiffrées)
    face_encoding = Column(LargeBinary, nullable=True)
    face_encoding_hash = Column(String(255), nullable=True)
    face_image_path = Column(String(500), nullable=True)
    
    # Statut et rôle
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_attempts = Column(Integer, default=0)
    
    # Token de vérification
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Tokens de réinitialisation
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Préférences de notification
    notification_preferences = Column(Text, nullable=True)  # JSON string
    
    # Relations
    waste_records = relationship("WasteRecord", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    @property
    def full_name(self) -> str:
        """Nom complet de l'utilisateur."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est admin."""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    @property
    def is_super_admin(self) -> bool:
        """Vérifie si l'utilisateur est super admin."""
        return self.role == UserRole.SUPER_ADMIN