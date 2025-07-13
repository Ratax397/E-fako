"""Schémas Pydantic pour la validation des données."""

from app.schemas.user import *
from app.schemas.waste import *
from app.schemas.notification import *

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserFaceRegister",
    "UserFaceLogin",
    "UserLogin",
    "UserPasswordReset",
    "UserPasswordResetConfirm",
    "UserStatistics",
    "UserList",
    
    # Waste schemas
    "WasteRecordBase",
    "WasteRecordCreate",
    "WasteRecordUpdate",
    "WasteRecordInDB",
    "WasteRecordResponse",
    "WasteRecordList",
    "WasteRecordValidation",
    "WasteRecordProcessing",
    "WasteStatisticsResponse",
    "WasteCategoryBase",
    "WasteCategoryCreate",
    "WasteCategoryUpdate",
    "WasteCategoryResponse",
    "WasteImageUpload",
    "WasteImageResponse",
    
    # Notification schemas
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationInDB",
    "NotificationResponse",
    "NotificationList",
    "NotificationMarkRead",
    "NotificationBulkCreate",
    "NotificationBroadcast",
    "NotificationTemplateBase",
    "NotificationTemplateCreate",
    "NotificationTemplateUpdate",
    "NotificationTemplateResponse",
    "NotificationDeviceBase",
    "NotificationDeviceCreate",
    "NotificationDeviceUpdate",
    "NotificationDeviceResponse",
    "NotificationStatistics",
    "NotificationSettings",
]