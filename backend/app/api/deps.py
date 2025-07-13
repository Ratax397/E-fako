"""Dépendances FastAPI pour l'authentification et la base de données."""

from typing import Optional, Generator, AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, get_async_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User, UserRole
from app.services.auth_service import auth_service
from app.core.logging import get_logger

logger = get_logger(__name__)

# Schéma de sécurité Bearer
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Obtenir l'utilisateur actuel à partir du token JWT."""
    try:
        # Vérifier le token
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        
        # Récupérer l'utilisateur
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise AuthenticationError("Could not validate credentials")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtenir l'utilisateur actuel actif."""
    if not current_user.is_active:
        raise AuthenticationError("User account is inactive")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtenir l'utilisateur actuel admin."""
    if not current_user.is_admin:
        raise AuthorizationError("Admin access required")
    return current_user


async def get_current_super_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Obtenir l'utilisateur actuel super admin."""
    if not current_user.is_super_admin:
        raise AuthorizationError("Super admin access required")
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Obtenir l'utilisateur actuel de manière optionnelle."""
    if not credentials:
        return None
    
    try:
        # Cette fonction est synchrone, donc on ne peut pas utiliser la DB async
        # On laisse cela aux endpoints qui en ont besoin
        payload = auth_service.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        return user_id
    except Exception:
        return None


class RoleChecker:
    """Vérificateur de rôles pour les endpoints."""
    
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise AuthorizationError(
                f"Access denied. Required roles: {[role.value for role in self.allowed_roles]}"
            )
        return current_user


# Fonctions utilitaires pour les vérifications de permissions
def require_admin():
    """Décorateur pour exiger les droits admin."""
    return RoleChecker([UserRole.ADMIN, UserRole.SUPER_ADMIN])


def require_super_admin():
    """Décorateur pour exiger les droits super admin."""
    return RoleChecker([UserRole.SUPER_ADMIN])


def require_user_or_admin():
    """Décorateur pour exiger les droits utilisateur ou admin."""
    return RoleChecker([UserRole.USER, UserRole.ADMIN, UserRole.SUPER_ADMIN])


async def get_pagination_params(
    page: int = 1,
    size: int = 10,
    max_size: int = 100
) -> dict:
    """Obtenir les paramètres de pagination."""
    if page < 1:
        page = 1
    if size < 1:
        size = 10
    if size > max_size:
        size = max_size
    
    offset = (page - 1) * size
    
    return {
        "page": page,
        "size": size,
        "offset": offset,
        "limit": size
    }


async def verify_resource_owner(
    resource_user_id: str,
    current_user: User = Depends(get_current_user)
) -> bool:
    """Vérifier que l'utilisateur actuel est le propriétaire de la ressource."""
    if current_user.is_admin:
        return True
    
    if str(current_user.id) != resource_user_id:
        raise AuthorizationError("You can only access your own resources")
    
    return True


class RequestLoggingDep:
    """Dépendance pour logger les requêtes avec contexte utilisateur."""
    
    def __init__(self, request: Request):
        self.request = request
        self.user_id = None
        self.username = None
    
    def set_user_context(self, user: User):
        """Définir le contexte utilisateur."""
        self.user_id = str(user.id)
        self.username = user.username
        
        # Ajouter à l'état de la requête pour le middleware
        self.request.state.user_id = self.user_id
        self.request.state.username = self.username


def get_request_logging_dep(request: Request) -> RequestLoggingDep:
    """Obtenir la dépendance de logging de requête."""
    return RequestLoggingDep(request)


# Middleware pour injecter le contexte utilisateur dans les logs
async def inject_user_context(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> User:
    """Injecter le contexte utilisateur dans la requête."""
    request.state.user_id = str(current_user.id)
    request.state.username = current_user.username
    return current_user


# Dépendances pour les filtres communs
async def get_search_params(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> dict:
    """Obtenir les paramètres de recherche et de tri."""
    if sort_order not in ["asc", "desc"]:
        sort_order = "asc"
    
    return {
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    }


async def get_date_range_params(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """Obtenir les paramètres de plage de dates."""
    return {
        "start_date": start_date,
        "end_date": end_date
    }