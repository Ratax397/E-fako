"""Endpoints pour la gestion des notifications."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.database import get_async_db
from app.core.exceptions import NotFoundError, AuthorizationError
from app.core.logging import get_logger
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse, NotificationList,
    NotificationMarkRead, NotificationBulkCreate, NotificationBroadcast,
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateResponse,
    NotificationDeviceCreate, NotificationDeviceUpdate, NotificationDeviceResponse,
    NotificationStatistics, NotificationSettings
)
from app.models.notification import Notification, NotificationTemplate, NotificationDevice
from app.models.user import User
from app.api.deps import (
    get_current_user, get_current_admin_user,
    get_pagination_params, get_search_params
)
from app.services.notification_service import notification_service

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=NotificationList)
async def get_notifications(
    db: AsyncSession = Depends(get_async_db),
    pagination: dict = Depends(get_pagination_params),
    search: dict = Depends(get_search_params),
    unread_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Obtenir les notifications de l'utilisateur actuel."""
    try:
        result = await notification_service.get_user_notifications(
            db, 
            str(current_user.id), 
            pagination["page"], 
            pagination["size"],
            unread_only
        )
        
        return NotificationList(
            notifications=[
                NotificationResponse.from_orm(notification) 
                for notification in result["notifications"]
            ],
            total=result["total"],
            page=result["page"],
            size=result["size"],
            has_next=result["has_next"],
            has_previous=result["has_previous"],
            unread_count=result["unread_count"]
        )
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir une notification par ID."""
    try:
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise NotFoundError("Notification not found")
        
        # Vérifier les permissions
        if not current_user.is_admin and notification.user_id != current_user.id:
            raise AuthorizationError("You can only access your own notifications")
        
        return NotificationResponse.from_orm(notification)
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error fetching notification {notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification"
        )


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Créer une nouvelle notification (admins seulement)."""
    try:
        notification = await notification_service.create_notification(db, notification_data)
        return NotificationResponse.from_orm(notification)
        
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def create_bulk_notifications(
    notification_data: NotificationBulkCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Créer plusieurs notifications (admins seulement)."""
    try:
        notifications = await notification_service.create_bulk_notifications(db, notification_data)
        
        return {
            "message": f"Created {len(notifications)} notifications successfully",
            "count": len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Error creating bulk notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bulk notifications"
        )


@router.post("/broadcast", status_code=status.HTTP_201_CREATED)
async def broadcast_notification(
    notification_data: NotificationBroadcast,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Diffuser une notification à tous les utilisateurs (admins seulement)."""
    try:
        notifications = await notification_service.broadcast_notification(db, notification_data)
        
        return {
            "message": f"Broadcasted notification to {len(notifications)} users",
            "count": len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to broadcast notification"
        )


@router.post("/mark-read")
async def mark_notifications_read(
    notification_data: NotificationMarkRead,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Marquer les notifications comme lues."""
    try:
        count = await notification_service.mark_as_read(
            db, 
            [str(nid) for nid in notification_data.notification_ids], 
            str(current_user.id)
        )
        
        return {
            "message": f"Marked {count} notifications as read",
            "count": count
        }
        
    except Exception as e:
        logger.error(f"Error marking notifications as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notifications as read"
        )


@router.post("/devices", response_model=NotificationDeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    device_data: NotificationDeviceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistrer un appareil pour les notifications push."""
    try:
        device = await notification_service.register_device(
            db,
            str(current_user.id),
            device_data.device_token,
            device_data.device_type,
            device_data.device_name
        )
        
        return NotificationDeviceResponse.from_orm(device)
        
    except Exception as e:
        logger.error(f"Error registering device: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register device"
        )


@router.get("/devices/", response_model=List[NotificationDeviceResponse])
async def get_user_devices(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir les appareils de l'utilisateur."""
    try:
        result = await db.execute(
            select(NotificationDevice).where(
                NotificationDevice.user_id == current_user.id
            )
        )
        devices = result.scalars().all()
        
        return [NotificationDeviceResponse.from_orm(device) for device in devices]
        
    except Exception as e:
        logger.error(f"Error fetching user devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user devices"
        )


@router.put("/devices/{device_id}", response_model=NotificationDeviceResponse)
async def update_device(
    device_id: UUID,
    device_update: NotificationDeviceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un appareil."""
    try:
        result = await db.execute(
            select(NotificationDevice).where(
                and_(
                    NotificationDevice.id == device_id,
                    NotificationDevice.user_id == current_user.id
                )
            )
        )
        device = result.scalar_one_or_none()
        
        if not device:
            raise NotFoundError("Device not found")
        
        # Mettre à jour les champs fournis
        update_data = device_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(device, field):
                setattr(device, field, value)
        
        await db.commit()
        await db.refresh(device)
        
        return NotificationDeviceResponse.from_orm(device)
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating device {device_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update device"
        )


@router.delete("/devices/{device_id}")
async def delete_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un appareil."""
    try:
        result = await db.execute(
            select(NotificationDevice).where(
                and_(
                    NotificationDevice.id == device_id,
                    NotificationDevice.user_id == current_user.id
                )
            )
        )
        device = result.scalar_one_or_none()
        
        if not device:
            raise NotFoundError("Device not found")
        
        await db.delete(device)
        await db.commit()
        
        return {"message": "Device deleted successfully"}
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting device {device_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete device"
        )


@router.get("/templates/", response_model=List[NotificationTemplateResponse])
async def get_notification_templates(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir les modèles de notification (admins seulement)."""
    try:
        result = await db.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.is_active == True
            )
        )
        templates = result.scalars().all()
        
        return [NotificationTemplateResponse.from_orm(template) for template in templates]
        
    except Exception as e:
        logger.error(f"Error fetching notification templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification templates"
        )


@router.post("/templates/", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_template(
    template_data: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Créer un modèle de notification (admins seulement)."""
    try:
        template = NotificationTemplate(**template_data.dict())
        
        db.add(template)
        await db.commit()
        await db.refresh(template)
        
        return NotificationTemplateResponse.from_orm(template)
        
    except Exception as e:
        logger.error(f"Error creating notification template: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification template"
        )


@router.put("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def update_notification_template(
    template_id: UUID,
    template_update: NotificationTemplateUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Mettre à jour un modèle de notification (admins seulement)."""
    try:
        result = await db.execute(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise NotFoundError("Notification template not found")
        
        # Mettre à jour les champs fournis
        update_data = template_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        await db.commit()
        await db.refresh(template)
        
        return NotificationTemplateResponse.from_orm(template)
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating notification template {template_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification template"
        )


@router.delete("/templates/{template_id}")
async def delete_notification_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprimer un modèle de notification (admins seulement)."""
    try:
        result = await db.execute(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise NotFoundError("Notification template not found")
        
        await db.delete(template)
        await db.commit()
        
        return {"message": "Notification template deleted successfully"}
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification template {template_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification template"
        )


@router.get("/settings/", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: User = Depends(get_current_user)
):
    """Obtenir les paramètres de notification de l'utilisateur."""
    try:
        # Obtenir les paramètres depuis les préférences utilisateur
        settings = NotificationSettings()
        
        if current_user.notification_preferences:
            import json
            prefs = json.loads(current_user.notification_preferences)
            settings = NotificationSettings(**prefs)
        
        return settings
        
    except Exception as e:
        logger.error(f"Error fetching notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification settings"
        )


@router.put("/settings/", response_model=NotificationSettings)
async def update_notification_settings(
    settings: NotificationSettings,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour les paramètres de notification de l'utilisateur."""
    try:
        import json
        
        # Sauvegarder les paramètres dans les préférences utilisateur
        current_user.notification_preferences = json.dumps(settings.dict())
        
        await db.commit()
        
        return settings
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification settings"
        )