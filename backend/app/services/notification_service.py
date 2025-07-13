"""Service de notifications push avec FCM."""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pyfcm import FCMNotification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from celery import Celery

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger, log_notification_event
from app.models.notification import (
    Notification, NotificationTemplate, NotificationDevice,
    NotificationType, NotificationPriority, NotificationStatus
)
from app.models.user import User, UserRole
from app.schemas.notification import (
    NotificationCreate, NotificationBulkCreate, NotificationBroadcast
)
from app.services.socketio_service import socket_service

logger = get_logger(__name__)

# Configuration Celery pour les tâches asynchrones
celery_app = Celery(
    "notifications",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


class NotificationService:
    """Service de gestion des notifications."""
    
    def __init__(self):
        self.fcm = FCMNotification(api_key=settings.FCM_SERVER_KEY)
    
    async def create_notification(
        self, 
        db: AsyncSession, 
        notification_data: NotificationCreate
    ) -> Notification:
        """Créer une nouvelle notification."""
        try:
            # Créer la notification
            notification = Notification(
                user_id=notification_data.user_id,
                title=notification_data.title,
                message=notification_data.message,
                notification_type=notification_data.notification_type,
                priority=notification_data.priority,
                data=json.dumps(notification_data.data) if notification_data.data else None,
                action_url=notification_data.action_url,
                icon=notification_data.icon,
                scheduled_at=notification_data.scheduled_at
            )
            
            db.add(notification)
            await db.commit()
            await db.refresh(notification)
            
            # Envoyer la notification si elle n'est pas planifiée
            if not notification.scheduled_at:
                await self.send_notification(db, notification)
            
            log_notification_event(
                event_type="notification_created",
                notification_id=str(notification.id),
                user_id=str(notification.user_id),
                notification_type=notification.notification_type.value,
                success=True
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            await db.rollback()
            raise
    
    async def create_bulk_notifications(
        self, 
        db: AsyncSession, 
        notification_data: NotificationBulkCreate
    ) -> List[Notification]:
        """Créer plusieurs notifications."""
        try:
            notifications = []
            
            for user_id in notification_data.user_ids:
                notification = Notification(
                    user_id=user_id,
                    title=notification_data.title,
                    message=notification_data.message,
                    notification_type=notification_data.notification_type,
                    priority=notification_data.priority,
                    data=json.dumps(notification_data.data) if notification_data.data else None,
                    action_url=notification_data.action_url,
                    icon=notification_data.icon,
                    scheduled_at=notification_data.scheduled_at
                )
                notifications.append(notification)
                db.add(notification)
            
            await db.commit()
            
            # Envoyer les notifications si elles ne sont pas planifiées
            if not notification_data.scheduled_at:
                for notification in notifications:
                    await self.send_notification(db, notification)
            
            log_notification_event(
                event_type="bulk_notifications_created",
                notification_type=notification_data.notification_type.value,
                success=True,
                count=len(notifications)
            )
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error creating bulk notifications: {e}")
            await db.rollback()
            raise
    
    async def broadcast_notification(
        self, 
        db: AsyncSession, 
        notification_data: NotificationBroadcast
    ) -> List[Notification]:
        """Diffuser une notification à tous les utilisateurs ou rôles spécifiques."""
        try:
            # Construire la requête pour obtenir les utilisateurs
            query = select(User).where(User.is_active == True)
            
            # Filtrer par rôles si spécifié
            if notification_data.target_roles:
                roles = [UserRole(role) for role in notification_data.target_roles]
                query = query.where(User.role.in_(roles))
            
            result = await db.execute(query)
            users = result.scalars().all()
            
            notifications = []
            
            for user in users:
                notification = Notification(
                    user_id=user.id,
                    title=notification_data.title,
                    message=notification_data.message,
                    notification_type=notification_data.notification_type,
                    priority=notification_data.priority,
                    data=json.dumps(notification_data.data) if notification_data.data else None,
                    action_url=notification_data.action_url,
                    icon=notification_data.icon,
                    scheduled_at=notification_data.scheduled_at
                )
                notifications.append(notification)
                db.add(notification)
            
            await db.commit()
            
            # Envoyer les notifications si elles ne sont pas planifiées
            if not notification_data.scheduled_at:
                for notification in notifications:
                    await self.send_notification(db, notification)
            
            log_notification_event(
                event_type="broadcast_notification",
                notification_type=notification_data.notification_type.value,
                success=True,
                count=len(notifications)
            )
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error broadcasting notification: {e}")
            await db.rollback()
            raise
    
    async def send_notification(self, db: AsyncSession, notification: Notification) -> bool:
        """Envoyer une notification."""
        try:
            # Récupérer l'utilisateur
            result = await db.execute(
                select(User).where(User.id == notification.user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User not found for notification {notification.id}")
                return False
            
            # Récupérer les appareils de l'utilisateur
            devices_result = await db.execute(
                select(NotificationDevice).where(
                    and_(
                        NotificationDevice.user_id == user.id,
                        NotificationDevice.is_active == True
                    )
                )
            )
            devices = devices_result.scalars().all()
            
            sent_successfully = False
            
            # Envoyer via FCM
            if devices:
                device_tokens = [device.device_token for device in devices]
                
                # Préparer les données de notification
                fcm_data = {
                    "notification_id": str(notification.id),
                    "type": notification.notification_type.value,
                    "action_url": notification.action_url
                }
                
                if notification.data:
                    try:
                        data_dict = json.loads(notification.data)
                        fcm_data.update(data_dict)
                    except json.JSONDecodeError:
                        pass
                
                # Envoyer la notification push
                result = self.fcm.notify_multiple_devices(
                    registration_ids=device_tokens,
                    message_title=notification.title,
                    message_body=notification.message,
                    data_message=fcm_data
                )
                
                sent_successfully = result.get('success', 0) > 0
            
            # Envoyer via Socket.IO
            await socket_service.broadcast_notification({
                "id": str(notification.id),
                "user_id": str(notification.user_id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.notification_type.value,
                "priority": notification.priority.value,
                "data": json.loads(notification.data) if notification.data else None,
                "action_url": notification.action_url,
                "icon": notification.icon,
                "created_at": notification.created_at.isoformat()
            })
            
            # Mettre à jour le statut de la notification
            if sent_successfully:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = NotificationStatus.FAILED
                notification.retry_count += 1
                
                # Programmer une nouvelle tentative si possible
                if notification.retry_count < notification.max_retries:
                    notification.next_retry_at = datetime.utcnow() + timedelta(minutes=5)
            
            await db.commit()
            
            log_notification_event(
                event_type="notification_sent",
                notification_id=str(notification.id),
                user_id=str(notification.user_id),
                notification_type=notification.notification_type.value,
                success=sent_successfully
            )
            
            return sent_successfully
            
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {e}")
            
            # Marquer comme échec
            notification.status = NotificationStatus.FAILED
            notification.retry_count += 1
            
            if notification.retry_count < notification.max_retries:
                notification.next_retry_at = datetime.utcnow() + timedelta(minutes=5)
            
            await db.commit()
            
            log_notification_event(
                event_type="notification_sent",
                notification_id=str(notification.id),
                user_id=str(notification.user_id),
                notification_type=notification.notification_type.value,
                success=False,
                error=str(e)
            )
            
            return False
    
    async def mark_as_read(
        self, 
        db: AsyncSession, 
        notification_ids: List[str], 
        user_id: str
    ) -> int:
        """Marquer les notifications comme lues."""
        try:
            # Mettre à jour les notifications
            result = await db.execute(
                select(Notification).where(
                    and_(
                        Notification.id.in_(notification_ids),
                        Notification.user_id == user_id
                    )
                )
            )
            notifications = result.scalars().all()
            
            count = 0
            for notification in notifications:
                if not notification.is_read:
                    notification.is_read = True
                    notification.read_at = datetime.utcnow()
                    count += 1
            
            await db.commit()
            
            log_notification_event(
                event_type="notifications_marked_read",
                user_id=user_id,
                success=True,
                count=count
            )
            
            return count
            
        except Exception as e:
            logger.error(f"Error marking notifications as read: {e}")
            await db.rollback()
            raise
    
    async def get_user_notifications(
        self, 
        db: AsyncSession, 
        user_id: str, 
        page: int = 1, 
        size: int = 10,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """Obtenir les notifications d'un utilisateur."""
        try:
            # Construire la requête
            query = select(Notification).where(Notification.user_id == user_id)
            
            if unread_only:
                query = query.where(Notification.is_read == False)
            
            query = query.order_by(Notification.created_at.desc())
            
            # Compter le total
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # Compter les non lues
            unread_query = select(func.count()).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            unread_result = await db.execute(unread_query)
            unread_count = unread_result.scalar()
            
            # Pagination
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)
            
            result = await db.execute(query)
            notifications = result.scalars().all()
            
            return {
                "notifications": notifications,
                "total": total,
                "page": page,
                "size": size,
                "has_next": offset + size < total,
                "has_previous": offset > 0,
                "unread_count": unread_count
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            raise
    
    async def register_device(
        self, 
        db: AsyncSession, 
        user_id: str, 
        device_token: str, 
        device_type: str,
        device_name: str = None
    ) -> NotificationDevice:
        """Enregistrer un appareil pour les notifications."""
        try:
            # Vérifier si l'appareil existe déjà
            existing_result = await db.execute(
                select(NotificationDevice).where(
                    NotificationDevice.device_token == device_token
                )
            )
            existing_device = existing_result.scalar_one_or_none()
            
            if existing_device:
                # Mettre à jour l'appareil existant
                existing_device.user_id = user_id
                existing_device.device_type = device_type
                existing_device.device_name = device_name
                existing_device.is_active = True
                existing_device.last_used = datetime.utcnow()
                
                await db.commit()
                return existing_device
            
            # Créer un nouvel appareil
            device = NotificationDevice(
                user_id=user_id,
                device_token=device_token,
                device_type=device_type,
                device_name=device_name,
                last_used=datetime.utcnow()
            )
            
            db.add(device)
            await db.commit()
            await db.refresh(device)
            
            log_notification_event(
                event_type="device_registered",
                user_id=user_id,
                success=True,
                device_type=device_type
            )
            
            return device
            
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            await db.rollback()
            raise
    
    async def process_scheduled_notifications(self, db: AsyncSession) -> int:
        """Traiter les notifications planifiées."""
        try:
            # Récupérer les notifications planifiées pour maintenant
            now = datetime.utcnow()
            
            result = await db.execute(
                select(Notification).where(
                    and_(
                        Notification.scheduled_at <= now,
                        Notification.status == NotificationStatus.PENDING
                    )
                )
            )
            notifications = result.scalars().all()
            
            count = 0
            for notification in notifications:
                if await self.send_notification(db, notification):
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {e}")
            return 0
    
    async def retry_failed_notifications(self, db: AsyncSession) -> int:
        """Réessayer les notifications échouées."""
        try:
            now = datetime.utcnow()
            
            result = await db.execute(
                select(Notification).where(
                    and_(
                        Notification.status == NotificationStatus.FAILED,
                        Notification.retry_count < Notification.max_retries,
                        Notification.next_retry_at <= now
                    )
                )
            )
            notifications = result.scalars().all()
            
            count = 0
            for notification in notifications:
                if await self.send_notification(db, notification):
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error retrying failed notifications: {e}")
            return 0


# Instance globale du service
notification_service = NotificationService()


# Tâches Celery pour le traitement asynchrone
@celery_app.task
def process_scheduled_notifications():
    """Tâche Celery pour traiter les notifications planifiées."""
    async def run():
        async with AsyncSessionLocal() as db:
            count = await notification_service.process_scheduled_notifications(db)
            logger.info(f"Processed {count} scheduled notifications")
    
    asyncio.run(run())


@celery_app.task
def retry_failed_notifications():
    """Tâche Celery pour réessayer les notifications échouées."""
    async def run():
        async with AsyncSessionLocal() as db:
            count = await notification_service.retry_failed_notifications(db)
            logger.info(f"Retried {count} failed notifications")
    
    asyncio.run(run())


# Configuration des tâches périodiques
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'process-scheduled-notifications': {
        'task': 'app.services.notification_service.process_scheduled_notifications',
        'schedule': crontab(minute='*/1'),  # Chaque minute
    },
    'retry-failed-notifications': {
        'task': 'app.services.notification_service.retry_failed_notifications',
        'schedule': crontab(minute='*/5'),  # Toutes les 5 minutes
    },
}

celery_app.conf.timezone = 'UTC'