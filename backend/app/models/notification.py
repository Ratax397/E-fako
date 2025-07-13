"""Modèle Notification pour la base de données MySQL."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from typing import Optional

from app.core.database import Base


class NotificationType(enum.Enum):
    """Types de notifications."""
    SYSTEM = "system"
    WASTE_UPDATE = "waste_update"
    COLLECTION_REMINDER = "collection_reminder"
    ACHIEVEMENT = "achievement"
    ADMIN_MESSAGE = "admin_message"
    VERIFICATION = "verification"
    SECURITY = "security"
    PROMOTION = "promotion"


class NotificationPriority(enum.Enum):
    """Priorités des notifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(enum.Enum):
    """Statuts des notifications."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Notification(Base):
    """Modèle de notification."""
    
    __tablename__ = "notifications"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    
    # Contenu
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    
    # Métadonnées
    data = Column(Text, nullable=True)  # JSON string pour données supplémentaires
    action_url = Column(String(500), nullable=True)
    icon = Column(String(100), nullable=True)
    
    # Statut
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    is_read = Column(Boolean, default=False)
    
    # Planification
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Retry mechanism
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id} - {self.title}>"
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si la notification est expirée."""
        if self.scheduled_at:
            return datetime.utcnow() > self.scheduled_at
        return False
    
    @property
    def can_retry(self) -> bool:
        """Vérifie si la notification peut être retentée."""
        return self.retry_count < self.max_retries


class NotificationTemplate(Base):
    """Modèles de notifications."""
    
    __tablename__ = "notification_templates"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Template
    title_template = Column(String(255), nullable=False)
    message_template = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    variables = Column(Text, nullable=True)  # JSON string des variables disponibles
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationTemplate {self.name}>"


class NotificationDevice(Base):
    """Appareils pour les notifications push."""
    
    __tablename__ = "notification_devices"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    
    # Informations de l'appareil
    device_token = Column(String(255), unique=True, nullable=False)
    device_type = Column(String(50), nullable=False)  # ios, android, web
    device_name = Column(String(100), nullable=True)
    
    # Préférences
    is_active = Column(Boolean, default=True)
    notification_settings = Column(Text, nullable=True)  # JSON string
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    user = relationship("User")
    
    def __repr__(self):
        return f"<NotificationDevice {self.device_token[:20]}...>"