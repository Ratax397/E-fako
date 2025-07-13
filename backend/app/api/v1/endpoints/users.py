"""Endpoints pour la gestion des utilisateurs."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.core.database import get_async_db
from app.core.exceptions import NotFoundError, AuthorizationError
from app.core.logging import get_logger, log_database_event
from app.schemas.user import (
    UserResponse, UserUpdate, UserList, UserStatistics
)
from app.models.user import User, UserRole, UserStatus
from app.api.deps import (
    get_current_user, get_current_admin_user, get_current_super_admin_user,
    get_pagination_params, get_search_params
)
from app.services.socketio_service import socket_service

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=UserList)
async def get_users(
    db: AsyncSession = Depends(get_async_db),
    pagination: dict = Depends(get_pagination_params),
    search: dict = Depends(get_search_params),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir la liste des utilisateurs (admins seulement)."""
    try:
        # Construire la requête de base
        query = select(User)
        
        # Ajouter les filtres
        filters = []
        
        if role:
            filters.append(User.role == role)
        
        if status:
            filters.append(User.status == status)
        
        if search["search"]:
            search_term = f"%{search['search']}%"
            filters.append(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Ajouter le tri
        if search["sort_by"]:
            sort_column = getattr(User, search["sort_by"], None)
            if sort_column:
                if search["sort_order"] == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(User.created_at.desc())
        
        # Compter le total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Appliquer la pagination
        query = query.offset(pagination["offset"]).limit(pagination["limit"])
        
        # Exécuter la requête
        result = await db.execute(query)
        users = result.scalars().all()
        
        # Calculer les informations de pagination
        has_next = pagination["offset"] + pagination["limit"] < total
        has_previous = pagination["offset"] > 0
        
        log_database_event(
            operation="select",
            table="users",
            success=True,
            count=len(users)
        )
        
        return UserList(
            users=[UserResponse.from_orm(user) for user in users],
            total=total,
            page=pagination["page"],
            size=pagination["size"],
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Obtenir le profil de l'utilisateur actuel."""
    return UserResponse.from_orm(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir un utilisateur par ID."""
    try:
        # Vérifier les permissions
        if not current_user.is_admin and str(current_user.id) != str(user_id):
            raise AuthorizationError("You can only access your own profile")
        
        # Récupérer l'utilisateur
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User not found")
        
        log_database_event(
            operation="select",
            table="users",
            record_id=str(user_id),
            success=True
        )
        
        return UserResponse.from_orm(user)
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour le profil de l'utilisateur actuel."""
    try:
        # Mettre à jour les champs fournis
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        log_database_event(
            operation="update",
            table="users",
            record_id=str(current_user.id),
            success=True
        )
        
        return UserResponse.from_orm(current_user)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Mettre à jour un utilisateur (admins seulement)."""
    try:
        # Récupérer l'utilisateur
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Mettre à jour les champs fournis
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        log_database_event(
            operation="update",
            table="users",
            record_id=str(user_id),
            success=True
        )
        
        return UserResponse.from_orm(user)
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprimer un utilisateur (admins seulement)."""
    try:
        # Vérifier qu'on ne supprime pas soi-même
        if str(current_user.id) == str(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account"
            )
        
        # Récupérer l'utilisateur
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Supprimer l'utilisateur
        await db.delete(user)
        await db.commit()
        
        log_database_event(
            operation="delete",
            table="users",
            record_id=str(user_id),
            success=True
        )
        
        return {"message": "User deleted successfully"}
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Activer un utilisateur (admins seulement)."""
    try:
        # Récupérer l'utilisateur
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Activer l'utilisateur
        user.is_active = True
        user.status = UserStatus.ACTIVE
        
        await db.commit()
        
        log_database_event(
            operation="update",
            table="users",
            record_id=str(user_id),
            success=True,
            action="activate"
        )
        
        return {"message": "User activated successfully"}
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error activating user {user_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Désactiver un utilisateur (admins seulement)."""
    try:
        # Vérifier qu'on ne désactive pas soi-même
        if str(current_user.id) == str(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account"
            )
        
        # Récupérer l'utilisateur
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Désactiver l'utilisateur
        user.is_active = False
        user.status = UserStatus.INACTIVE
        
        await db.commit()
        
        log_database_event(
            operation="update",
            table="users",
            record_id=str(user_id),
            success=True,
            action="deactivate"
        )
        
        return {"message": "User deactivated successfully"}
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )


@router.get("/statistics/overview", response_model=UserStatistics)
async def get_user_statistics(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obtenir les statistiques des utilisateurs (admins seulement)."""
    try:
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
        
        # Utilisateurs ce mois
        from datetime import datetime, timedelta
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        users_this_month_result = await db.execute(
            select(func.count(User.id)).where(User.created_at >= start_of_month)
        )
        users_this_month = users_this_month_result.scalar()
        
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
        
        statistics = UserStatistics(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            users_this_month=users_this_month,
            users_by_role=users_by_role,
            users_by_status=users_by_status
        )
        
        # Diffuser les statistiques via Socket.IO
        await socket_service.broadcast_user_statistics(statistics.dict())
        
        log_database_event(
            operation="select",
            table="users",
            success=True,
            action="statistics"
        )
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error fetching user statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user statistics"
        )