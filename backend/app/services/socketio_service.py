"""Service Socket.IO pour les mises à jour en temps réel."""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import socketio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger, log_socketio_event
from app.models.user import User, UserRole
from app.services.auth_service import auth_service

logger = get_logger(__name__)

# Instance Socket.IO
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.CORS_ORIGINS,
    logger=False,
    engineio_logger=False
)

# Application ASGI Socket.IO
sio_app = socketio.ASGIApp(sio, socketio_path="socket.io")


class SocketIOService:
    """Service pour gérer les connexions Socket.IO."""
    
    def __init__(self):
        self.connected_users: Dict[str, Dict[str, Any]] = {}
        self.admin_rooms: Dict[str, List[str]] = {}
        self.user_rooms: Dict[str, str] = {}
    
    async def authenticate_socket(self, token: str) -> Optional[User]:
        """Authentifier un utilisateur via Socket.IO."""
        try:
            payload = auth_service.verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                return None
            
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                return user
                
        except Exception as e:
            logger.error(f"Socket authentication failed: {e}")
            return None
    
    async def add_user_to_room(self, sid: str, user: User) -> None:
        """Ajouter un utilisateur à une room."""
        # Room générale pour tous les utilisateurs
        await sio.enter_room(sid, "users")
        
        # Room spécifique à l'utilisateur
        user_room = f"user_{user.id}"
        await sio.enter_room(sid, user_room)
        
        # Room admin si applicable
        if user.is_admin:
            await sio.enter_room(sid, "admins")
            
        if user.is_super_admin:
            await sio.enter_room(sid, "super_admins")
        
        # Stocker les informations de l'utilisateur
        self.connected_users[sid] = {
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "connected_at": datetime.utcnow().isoformat()
        }
        
        # Notifier les admins d'une nouvelle connexion
        if user.role == UserRole.USER:
            await self.emit_to_admins("user_connected", {
                "user_id": str(user.id),
                "username": user.username,
                "connected_at": datetime.utcnow().isoformat()
            })
    
    async def remove_user_from_rooms(self, sid: str) -> None:
        """Retirer un utilisateur de toutes les rooms."""
        if sid in self.connected_users:
            user_info = self.connected_users[sid]
            
            # Notifier les admins d'une déconnexion
            await self.emit_to_admins("user_disconnected", {
                "user_id": user_info["user_id"],
                "username": user_info["username"],
                "disconnected_at": datetime.utcnow().isoformat()
            })
            
            del self.connected_users[sid]
    
    async def emit_to_user(self, user_id: str, event: str, data: Dict[str, Any]) -> None:
        """Émettre un événement à un utilisateur spécifique."""
        await sio.emit(event, data, room=f"user_{user_id}")
        
        log_socketio_event(
            event_type="emit_to_user",
            event_name=event,
            user_id=user_id,
            success=True
        )
    
    async def emit_to_admins(self, event: str, data: Dict[str, Any]) -> None:
        """Émettre un événement à tous les admins."""
        await sio.emit(event, data, room="admins")
        
        log_socketio_event(
            event_type="emit_to_admins",
            event_name=event,
            success=True
        )
    
    async def emit_to_super_admins(self, event: str, data: Dict[str, Any]) -> None:
        """Émettre un événement aux super admins."""
        await sio.emit(event, data, room="super_admins")
        
        log_socketio_event(
            event_type="emit_to_super_admins",
            event_name=event,
            success=True
        )
    
    async def emit_to_all_users(self, event: str, data: Dict[str, Any]) -> None:
        """Émettre un événement à tous les utilisateurs connectés."""
        await sio.emit(event, data, room="users")
        
        log_socketio_event(
            event_type="emit_to_all_users",
            event_name=event,
            success=True
        )
    
    async def get_connected_users_count(self) -> int:
        """Obtenir le nombre d'utilisateurs connectés."""
        return len(self.connected_users)
    
    async def get_connected_admins_count(self) -> int:
        """Obtenir le nombre d'admins connectés."""
        return len([
            user for user in self.connected_users.values()
            if user["role"] in ["admin", "super_admin"]
        ])
    
    async def broadcast_waste_update(self, waste_data: Dict[str, Any]) -> None:
        """Diffuser une mise à jour de déchets."""
        await self.emit_to_admins("waste_update", waste_data)
        
        # Notifier l'utilisateur concerné
        user_id = waste_data.get("user_id")
        if user_id:
            await self.emit_to_user(user_id, "waste_status_update", waste_data)
    
    async def broadcast_user_statistics(self, stats: Dict[str, Any]) -> None:
        """Diffuser les statistiques utilisateur."""
        await self.emit_to_admins("user_statistics", stats)
    
    async def broadcast_waste_statistics(self, stats: Dict[str, Any]) -> None:
        """Diffuser les statistiques de déchets."""
        await self.emit_to_admins("waste_statistics", stats)
    
    async def broadcast_notification(self, notification_data: Dict[str, Any]) -> None:
        """Diffuser une notification."""
        user_id = notification_data.get("user_id")
        if user_id:
            await self.emit_to_user(user_id, "notification", notification_data)


# Instance globale du service
socket_service = SocketIOService()


# Événements Socket.IO
@sio.event
async def connect(sid, environ, auth):
    """Gestionnaire de connexion Socket.IO."""
    try:
        # Authentifier l'utilisateur
        token = auth.get("token") if auth else None
        if not token:
            logger.warning(f"Socket connection without token: {sid}")
            await sio.disconnect(sid)
            return False
        
        user = await socket_service.authenticate_socket(token)
        if not user:
            logger.warning(f"Socket authentication failed: {sid}")
            await sio.disconnect(sid)
            return False
        
        # Ajouter l'utilisateur aux rooms appropriées
        await socket_service.add_user_to_room(sid, user)
        
        logger.info(f"User connected via Socket.IO: {user.username} ({sid})")
        
        # Envoyer un message de bienvenue
        await sio.emit("welcome", {
            "message": "Connected successfully",
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role.value
        }, room=sid)
        
        log_socketio_event(
            event_type="connect",
            user_id=str(user.id),
            success=True
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Socket connection error: {e}")
        await sio.disconnect(sid)
        return False


@sio.event
async def disconnect(sid):
    """Gestionnaire de déconnexion Socket.IO."""
    try:
        user_info = socket_service.connected_users.get(sid)
        if user_info:
            logger.info(f"User disconnected: {user_info['username']} ({sid})")
            
            log_socketio_event(
                event_type="disconnect",
                user_id=user_info["user_id"],
                success=True
            )
        
        await socket_service.remove_user_from_rooms(sid)
        
    except Exception as e:
        logger.error(f"Socket disconnection error: {e}")


@sio.event
async def ping(sid):
    """Gestionnaire de ping pour maintenir la connexion."""
    await sio.emit("pong", {"timestamp": datetime.utcnow().isoformat()}, room=sid)


@sio.event
async def get_dashboard_data(sid):
    """Obtenir les données du tableau de bord."""
    try:
        user_info = socket_service.connected_users.get(sid)
        if not user_info:
            return
        
        # Vérifier les permissions
        if user_info["role"] not in ["admin", "super_admin"]:
            await sio.emit("error", {"message": "Unauthorized"}, room=sid)
            return
        
        # Obtenir les données du tableau de bord
        dashboard_data = {
            "connected_users": await socket_service.get_connected_users_count(),
            "connected_admins": await socket_service.get_connected_admins_count(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await sio.emit("dashboard_data", dashboard_data, room=sid)
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        await sio.emit("error", {"message": "Internal server error"}, room=sid)


@sio.event
async def join_room(sid, data):
    """Joindre une room personnalisée."""
    try:
        user_info = socket_service.connected_users.get(sid)
        if not user_info:
            return
        
        room_name = data.get("room")
        if not room_name:
            return
        
        # Vérifier les permissions pour certaines rooms
        if room_name.startswith("admin_") and user_info["role"] not in ["admin", "super_admin"]:
            await sio.emit("error", {"message": "Unauthorized"}, room=sid)
            return
        
        await sio.enter_room(sid, room_name)
        await sio.emit("room_joined", {"room": room_name}, room=sid)
        
        log_socketio_event(
            event_type="join_room",
            user_id=user_info["user_id"],
            room=room_name,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error joining room: {e}")


@sio.event
async def leave_room(sid, data):
    """Quitter une room personnalisée."""
    try:
        user_info = socket_service.connected_users.get(sid)
        if not user_info:
            return
        
        room_name = data.get("room")
        if not room_name:
            return
        
        await sio.leave_room(sid, room_name)
        await sio.emit("room_left", {"room": room_name}, room=sid)
        
        log_socketio_event(
            event_type="leave_room",
            user_id=user_info["user_id"],
            room=room_name,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error leaving room: {e}")


# Tâches de fond pour les mises à jour périodiques
async def periodic_dashboard_updates():
    """Envoyer des mises à jour périodiques du tableau de bord."""
    while True:
        try:
            await asyncio.sleep(30)  # Toutes les 30 secondes
            
            # Statistiques de base
            stats = {
                "connected_users": await socket_service.get_connected_users_count(),
                "connected_admins": await socket_service.get_connected_admins_count(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await socket_service.emit_to_admins("dashboard_update", stats)
            
        except Exception as e:
            logger.error(f"Error in periodic dashboard updates: {e}")


# Démarrer les tâches de fond
# Note: periodic_dashboard_updates() doit être démarré par l'application principale