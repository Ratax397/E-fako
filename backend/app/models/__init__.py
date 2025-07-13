"""Modèles de base de données."""

from app.models.user import User, UserRole, UserStatus
from app.models.waste import (
    WasteRecord, WasteType, WasteStatus, 
    WasteCategory, WasteStatistics
)
from app.models.notification import (
    Notification, NotificationType, NotificationPriority, NotificationStatus,
    NotificationTemplate, NotificationDevice
)

__all__ = [
    # User models
    "User",
    "UserRole", 
    "UserStatus",
    
    # Waste models
    "WasteRecord",
    "WasteType",
    "WasteStatus",
    "WasteCategory",
    "WasteStatistics",
    
    # Notification models
    "Notification",
    "NotificationType",
    "NotificationPriority",
    "NotificationStatus",
    "NotificationTemplate",
    "NotificationDevice",
]