"""Schémas Pydantic pour les notifications."""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.notification import NotificationType, NotificationPriority, NotificationStatus


class NotificationBase(BaseModel):
    """Schéma de base pour les notifications."""
    title: str = Field(..., max_length=255)
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    scheduled_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    """Schéma pour créer une notification."""
    user_id: UUID


class NotificationUpdate(BaseModel):
    """Schéma pour mettre à jour une notification."""
    title: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = None
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    scheduled_at: Optional[datetime] = None
    is_read: Optional[bool] = None


class NotificationInDB(NotificationBase):
    """Schéma pour les notifications en base de données."""
    id: UUID
    user_id: UUID
    status: NotificationStatus
    is_read: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        use_enum_values = True


class NotificationResponse(NotificationBase):
    """Schéma pour les réponses de notification."""
    id: UUID
    user_id: UUID
    status: NotificationStatus
    is_read: bool = False
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        orm_mode = True
        use_enum_values = True


class NotificationList(BaseModel):
    """Schéma pour la liste des notifications."""
    notifications: List[NotificationResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool
    unread_count: int
    
    class Config:
        orm_mode = True


class NotificationMarkRead(BaseModel):
    """Schéma pour marquer une notification comme lue."""
    notification_ids: List[UUID]


class NotificationBulkCreate(BaseModel):
    """Schéma pour créer plusieurs notifications."""
    user_ids: List[UUID]
    title: str = Field(..., max_length=255)
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    scheduled_at: Optional[datetime] = None


class NotificationBroadcast(BaseModel):
    """Schéma pour diffuser une notification à tous les utilisateurs."""
    title: str = Field(..., max_length=255)
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=100)
    scheduled_at: Optional[datetime] = None
    target_roles: Optional[List[str]] = None  # Rôles ciblés


class NotificationTemplateBase(BaseModel):
    """Schéma de base pour les modèles de notification."""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    title_template: str = Field(..., max_length=255)
    message_template: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    variables: Optional[Dict[str, Any]] = None


class NotificationTemplateCreate(NotificationTemplateBase):
    """Schéma pour créer un modèle de notification."""
    pass


class NotificationTemplateUpdate(BaseModel):
    """Schéma pour mettre à jour un modèle de notification."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    title_template: Optional[str] = Field(None, max_length=255)
    message_template: Optional[str] = None
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    variables: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    """Schéma pour les réponses de modèle de notification."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        use_enum_values = True


class NotificationDeviceBase(BaseModel):
    """Schéma de base pour les appareils de notification."""
    device_token: str = Field(..., max_length=255)
    device_type: str = Field(..., max_length=50)
    device_name: Optional[str] = Field(None, max_length=100)
    notification_settings: Optional[Dict[str, Any]] = None


class NotificationDeviceCreate(NotificationDeviceBase):
    """Schéma pour créer un appareil de notification."""
    pass


class NotificationDeviceUpdate(BaseModel):
    """Schéma pour mettre à jour un appareil de notification."""
    device_token: Optional[str] = Field(None, max_length=255)
    device_type: Optional[str] = Field(None, max_length=50)
    device_name: Optional[str] = Field(None, max_length=100)
    notification_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class NotificationDeviceResponse(NotificationDeviceBase):
    """Schéma pour les réponses d'appareil de notification."""
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class NotificationStatistics(BaseModel):
    """Schéma pour les statistiques des notifications."""
    total_notifications: int
    sent_notifications: int
    pending_notifications: int
    failed_notifications: int
    read_notifications: int
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]
    notifications_today: int
    notifications_this_week: int
    notifications_this_month: int
    
    class Config:
        orm_mode = True


class NotificationSettings(BaseModel):
    """Schéma pour les paramètres de notification utilisateur."""
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    waste_updates: bool = True
    system_notifications: bool = True
    promotions: bool = False
    achievements: bool = True
    
    class Config:
        orm_mode = True