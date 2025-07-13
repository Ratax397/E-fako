"""Endpoints pour les statistiques et le dashboard admin."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta
import json

from app.core.database import get_async_db
from app.core.logging import get_logger
from app.schemas.waste import WasteStatisticsResponse
from app.schemas.user import UserStatistics
from app.schemas.notification import NotificationStatistics
from app.models.user import User, UserRole, UserStatus
from app.models.waste import WasteRecord, WasteType, WasteStatus
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.api.deps import get_current_admin_user, get_current_super_admin_user, get_date_range_params
from app.services.socketio_service import socket_service

logger = get_logger(__name__)
router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_statistics(
    db: AsyncSession = Depends(get_async_db),
    date_range: dict = Depends(get_date_range_params),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir les statistiques du dashboard admin."""
    try:
        # Définir la plage de dates
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)  # 30 jours par défaut
        
        if date_range["start_date"]:
            start_date = datetime.fromisoformat(date_range["start_date"])
        if date_range["end_date"]:
            end_date = datetime.fromisoformat(date_range["end_date"])
        
        # Statistiques des utilisateurs
        user_stats = await get_user_statistics_data(db, start_date, end_date)
        
        # Statistiques des déchets
        waste_stats = await get_waste_statistics_data(db, start_date, end_date)
        
        # Statistiques des notifications
        notification_stats = await get_notification_statistics_data(db, start_date, end_date)
        
        # Statistiques en temps réel
        realtime_stats = await get_realtime_statistics()
        
        # Tendances
        trends = await get_trends_data(db, start_date, end_date)
        
        dashboard_data = {
            "overview": {
                "total_users": user_stats["total_users"],
                "active_users": user_stats["active_users"],
                "total_waste_records": waste_stats["total_records"],
                "total_waste_kg": waste_stats["total_waste_kg"],
                "recycled_percentage": waste_stats["recycled_percentage"],
                "pending_validations": waste_stats["pending_validations"],
                "connected_users": realtime_stats["connected_users"],
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat()
            },
            "user_statistics": user_stats,
            "waste_statistics": waste_stats,
            "notification_statistics": notification_stats,
            "trends": trends,
            "realtime": realtime_stats
        }
        
        # Diffuser les statistiques via Socket.IO
        await socket_service.broadcast_waste_statistics(dashboard_data)
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error fetching dashboard statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )


@router.get("/users", response_model=UserStatistics)
async def get_user_statistics(
    db: AsyncSession = Depends(get_async_db),
    date_range: dict = Depends(get_date_range_params),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir les statistiques détaillées des utilisateurs."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        if date_range["start_date"]:
            start_date = datetime.fromisoformat(date_range["start_date"])
        if date_range["end_date"]:
            end_date = datetime.fromisoformat(date_range["end_date"])
        
        stats = await get_user_statistics_data(db, start_date, end_date)
        
        return UserStatistics(**stats)
        
    except Exception as e:
        logger.error(f"Error fetching user statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user statistics"
        )


@router.get("/waste", response_model=WasteStatisticsResponse)
async def get_waste_statistics(
    db: AsyncSession = Depends(get_async_db),
    date_range: dict = Depends(get_date_range_params),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir les statistiques détaillées des déchets."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        if date_range["start_date"]:
            start_date = datetime.fromisoformat(date_range["start_date"])
        if date_range["end_date"]:
            end_date = datetime.fromisoformat(date_range["end_date"])
        
        stats = await get_waste_statistics_data(db, start_date, end_date)
        
        return WasteStatisticsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error fetching waste statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch waste statistics"
        )


@router.get("/notifications", response_model=NotificationStatistics)
async def get_notification_statistics(
    db: AsyncSession = Depends(get_async_db),
    date_range: dict = Depends(get_date_range_params),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir les statistiques des notifications."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        if date_range["start_date"]:
            start_date = datetime.fromisoformat(date_range["start_date"])
        if date_range["end_date"]:
            end_date = datetime.fromisoformat(date_range["end_date"])
        
        stats = await get_notification_statistics_data(db, start_date, end_date)
        
        return NotificationStatistics(**stats)
        
    except Exception as e:
        logger.error(f"Error fetching notification statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification statistics"
        )


@router.get("/trends")
async def get_trends(
    db: AsyncSession = Depends(get_async_db),
    date_range: dict = Depends(get_date_range_params),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir les tendances sur une période."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        if date_range["start_date"]:
            start_date = datetime.fromisoformat(date_range["start_date"])
        if date_range["end_date"]:
            end_date = datetime.fromisoformat(date_range["end_date"])
        
        trends = await get_trends_data(db, start_date, end_date)
        
        return trends
        
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch trends"
        )


@router.get("/realtime")
async def get_realtime_stats(
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir les statistiques en temps réel."""
    try:
        stats = await get_realtime_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching realtime statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch realtime statistics"
        )


# Fonctions utilitaires
async def get_user_statistics_data(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> Dict[str, Any]:
    """Obtenir les données statistiques des utilisateurs."""
    
    # Statistiques de base
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar()
    
    verified_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_verified == True)
    )
    verified_users = verified_users_result.scalar()
    
    # Utilisateurs de la période
    users_period_result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.created_at >= start_date,
                User.created_at <= end_date
            )
        )
    )
    users_this_period = users_period_result.scalar()
    
    # Utilisateurs par rôle
    users_by_role_result = await db.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    )
    users_by_role = {role.value: count for role, count in users_by_role_result}
    
    # Utilisateurs par statut
    users_by_status_result = await db.execute(
        select(User.status, func.count(User.id)).group_by(User.status)
    )
    users_by_status = {status.value: count for status, count in users_by_status_result}
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "users_this_month": users_this_period,
        "users_by_role": users_by_role,
        "users_by_status": users_by_status
    }


async def get_waste_statistics_data(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> Dict[str, Any]:
    """Obtenir les données statistiques des déchets."""
    
    # Statistiques de base
    total_records_result = await db.execute(select(func.count(WasteRecord.id)))
    total_records = total_records_result.scalar()
    
    total_waste_result = await db.execute(select(func.sum(WasteRecord.quantity)))
    total_waste_kg = total_waste_result.scalar() or 0.0
    
    # Déchets par type
    waste_by_type_result = await db.execute(
        select(WasteRecord.waste_type, func.sum(WasteRecord.quantity))
        .group_by(WasteRecord.waste_type)
    )
    waste_by_type = {waste_type.value: float(quantity) for waste_type, quantity in waste_by_type_result}
    
    # Déchets par statut
    waste_by_status_result = await db.execute(
        select(WasteRecord.status, func.count(WasteRecord.id))
        .group_by(WasteRecord.status)
    )
    waste_by_status = {status.value: count for status, count in waste_by_status_result}
    
    # Taux de recyclage
    recycled_result = await db.execute(
        select(func.sum(WasteRecord.quantity))
        .where(WasteRecord.status == WasteStatus.RECYCLED)
    )
    recycled_kg = recycled_result.scalar() or 0.0
    recycled_percentage = (recycled_kg / total_waste_kg * 100) if total_waste_kg > 0 else 0.0
    
    # Score environnemental moyen
    avg_score_result = await db.execute(select(func.avg(WasteRecord.environmental_score)))
    environmental_score_avg = avg_score_result.scalar() or 0.0
    
    # Top contributeurs
    top_contributors_result = await db.execute(
        select(User.username, func.sum(WasteRecord.quantity))
        .join(WasteRecord)
        .group_by(User.username)
        .order_by(func.sum(WasteRecord.quantity).desc())
        .limit(10)
    )
    top_contributors = [
        {"username": username, "total_kg": float(total_kg)}
        for username, total_kg in top_contributors_result
    ]
    
    # Validations en attente
    pending_validations_result = await db.execute(
        select(func.count(WasteRecord.id))
        .where(WasteRecord.is_validated == False)
    )
    pending_validations = pending_validations_result.scalar()
    
    # Tendances mensuelles
    monthly_trends = await get_monthly_waste_trends(db, start_date, end_date)
    
    return {
        "total_waste_kg": total_waste_kg,
        "total_records": total_records,
        "total_users": len(set([record.user_id for record in await db.execute(select(WasteRecord.user_id))])),
        "waste_by_type": waste_by_type,
        "waste_by_status": waste_by_status,
        "recycled_percentage": recycled_percentage,
        "environmental_score_avg": environmental_score_avg,
        "top_contributors": top_contributors,
        "monthly_trends": monthly_trends,
        "pending_validations": pending_validations
    }


async def get_notification_statistics_data(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> Dict[str, Any]:
    """Obtenir les données statistiques des notifications."""
    
    # Statistiques de base
    total_notifications_result = await db.execute(select(func.count(Notification.id)))
    total_notifications = total_notifications_result.scalar()
    
    sent_notifications_result = await db.execute(
        select(func.count(Notification.id))
        .where(Notification.status == NotificationStatus.SENT)
    )
    sent_notifications = sent_notifications_result.scalar()
    
    pending_notifications_result = await db.execute(
        select(func.count(Notification.id))
        .where(Notification.status == NotificationStatus.PENDING)
    )
    pending_notifications = pending_notifications_result.scalar()
    
    failed_notifications_result = await db.execute(
        select(func.count(Notification.id))
        .where(Notification.status == NotificationStatus.FAILED)
    )
    failed_notifications = failed_notifications_result.scalar()
    
    read_notifications_result = await db.execute(
        select(func.count(Notification.id))
        .where(Notification.is_read == True)
    )
    read_notifications = read_notifications_result.scalar()
    
    # Notifications par type
    notifications_by_type_result = await db.execute(
        select(Notification.notification_type, func.count(Notification.id))
        .group_by(Notification.notification_type)
    )
    notifications_by_type = {
        notification_type.value: count 
        for notification_type, count in notifications_by_type_result
    }
    
    # Notifications par priorité
    notifications_by_priority_result = await db.execute(
        select(Notification.priority, func.count(Notification.id))
        .group_by(Notification.priority)
    )
    notifications_by_priority = {
        priority.value: count 
        for priority, count in notifications_by_priority_result
    }
    
    # Notifications par période
    today = datetime.utcnow().date()
    notifications_today_result = await db.execute(
        select(func.count(Notification.id))
        .where(func.date(Notification.created_at) == today)
    )
    notifications_today = notifications_today_result.scalar()
    
    week_start = today - timedelta(days=today.weekday())
    notifications_week_result = await db.execute(
        select(func.count(Notification.id))
        .where(func.date(Notification.created_at) >= week_start)
    )
    notifications_this_week = notifications_week_result.scalar()
    
    month_start = today.replace(day=1)
    notifications_month_result = await db.execute(
        select(func.count(Notification.id))
        .where(func.date(Notification.created_at) >= month_start)
    )
    notifications_this_month = notifications_month_result.scalar()
    
    return {
        "total_notifications": total_notifications,
        "sent_notifications": sent_notifications,
        "pending_notifications": pending_notifications,
        "failed_notifications": failed_notifications,
        "read_notifications": read_notifications,
        "notifications_by_type": notifications_by_type,
        "notifications_by_priority": notifications_by_priority,
        "notifications_today": notifications_today,
        "notifications_this_week": notifications_this_week,
        "notifications_this_month": notifications_this_month
    }


async def get_trends_data(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> Dict[str, Any]:
    """Obtenir les données de tendances."""
    
    # Tendances des utilisateurs
    user_trends = await get_daily_user_registrations(db, start_date, end_date)
    
    # Tendances des déchets
    waste_trends = await get_daily_waste_records(db, start_date, end_date)
    
    # Tendances des notifications
    notification_trends = await get_daily_notifications(db, start_date, end_date)
    
    return {
        "user_registrations": user_trends,
        "waste_records": waste_trends,
        "notifications": notification_trends
    }


async def get_realtime_statistics() -> Dict[str, Any]:
    """Obtenir les statistiques en temps réel."""
    
    # Utilisateurs connectés
    connected_users = await socket_service.get_connected_users_count()
    connected_admins = await socket_service.get_connected_admins_count()
    
    return {
        "connected_users": connected_users,
        "connected_admins": connected_admins,
        "timestamp": datetime.utcnow().isoformat()
    }


async def get_monthly_waste_trends(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> list:
    """Obtenir les tendances mensuelles des déchets."""
    
    # Simplification : retourner des données fictives pour l'exemple
    # Dans une implémentation réelle, on ferait une requête GROUP BY mois
    return [
        {"month": "2024-01", "total_kg": 120.5, "records": 45},
        {"month": "2024-02", "total_kg": 150.2, "records": 62},
        {"month": "2024-03", "total_kg": 180.8, "records": 78}
    ]


async def get_daily_user_registrations(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> list:
    """Obtenir les inscriptions d'utilisateurs par jour."""
    
    # Simplification : retourner des données fictives
    return [
        {"date": "2024-01-01", "count": 5},
        {"date": "2024-01-02", "count": 8},
        {"date": "2024-01-03", "count": 12}
    ]


async def get_daily_waste_records(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> list:
    """Obtenir les enregistrements de déchets par jour."""
    
    # Simplification : retourner des données fictives
    return [
        {"date": "2024-01-01", "count": 15, "total_kg": 45.2},
        {"date": "2024-01-02", "count": 22, "total_kg": 67.8},
        {"date": "2024-01-03", "count": 18, "total_kg": 52.1}
    ]


async def get_daily_notifications(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> list:
    """Obtenir les notifications par jour."""
    
    # Simplification : retourner des données fictives
    return [
        {"date": "2024-01-01", "sent": 25, "failed": 2},
        {"date": "2024-01-02", "sent": 32, "failed": 1},
        {"date": "2024-01-03", "sent": 28, "failed": 3}
    ]