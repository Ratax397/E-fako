"""Endpoints d'authentification avec reconnaissance faciale."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.logging import get_logger, log_auth_event
from app.schemas.user import (
    UserCreate, UserResponse, UserLogin, UserFaceLogin, UserFaceRegister,
    UserPasswordReset, UserPasswordResetConfirm
)
from app.services.auth_service import auth_service
from app.api.deps import get_current_user
from app.models.user import User

logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Enregistrer un nouvel utilisateur."""
    try:
        # Créer l'utilisateur
        user = await auth_service.register_user(db, user_data)
        
        log_auth_event(
            event_type="user_register",
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            success=True
        )
        
        return UserResponse.from_orm(user)
        
    except ValidationError as e:
        log_auth_event(
            event_type="user_register",
            email=user_data.email,
            success=False,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login")
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_async_db)
):
    """Connexion par nom d'utilisateur et mot de passe."""
    try:
        # Authentifier l'utilisateur
        login_result = await auth_service.login_user(db, user_data)
        
        log_auth_event(
            event_type="user_login",
            user_id=str(login_result["user"].id),
            username=login_result["user"].username,
            success=True
        )
        
        return {
            "access_token": login_result["access_token"],
            "refresh_token": login_result["refresh_token"],
            "token_type": login_result["token_type"],
            "user": UserResponse.from_orm(login_result["user"])
        }
        
    except AuthenticationError as e:
        log_auth_event(
            event_type="user_login",
            username=user_data.username,
            success=False,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/face-register")
async def register_face(
    face_data: UserFaceRegister,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistrer les données faciales pour un utilisateur."""
    try:
        # Vérifier que l'utilisateur peut enregistrer des données faciales
        if str(current_user.id) != str(face_data.user_id) and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only register face data for yourself"
            )
        
        # Enregistrer les données faciales
        success = await auth_service.register_face(db, face_data)
        
        log_auth_event(
            event_type="face_register",
            user_id=str(face_data.user_id),
            success=success
        )
        
        return {
            "success": success,
            "message": "Face data registered successfully"
        }
        
    except ValidationError as e:
        log_auth_event(
            event_type="face_register",
            user_id=str(face_data.user_id),
            success=False,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Face registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face registration failed"
        )


@router.post("/face-login")
async def login_face(
    face_data: UserFaceLogin,
    db: AsyncSession = Depends(get_async_db)
):
    """Connexion par reconnaissance faciale."""
    try:
        # Authentifier par reconnaissance faciale
        login_result = await auth_service.login_face(db, face_data)
        
        log_auth_event(
            event_type="face_login",
            user_id=str(login_result["user"].id),
            username=login_result["user"].username,
            success=True
        )
        
        return {
            "access_token": login_result["access_token"],
            "refresh_token": login_result["refresh_token"],
            "token_type": login_result["token_type"],
            "user": UserResponse.from_orm(login_result["user"])
        }
        
    except AuthenticationError as e:
        log_auth_event(
            event_type="face_login",
            success=False,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Face login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face login failed"
        )


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
):
    """Rafraîchir le token d'accès."""
    try:
        # Rafraîchir le token
        result = await auth_service.refresh_token(db, credentials.credentials)
        
        log_auth_event(
            event_type="token_refresh",
            success=True
        )
        
        return result
        
    except AuthenticationError as e:
        log_auth_event(
            event_type="token_refresh",
            success=False,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/password-reset")
async def request_password_reset(
    reset_data: UserPasswordReset,
    db: AsyncSession = Depends(get_async_db)
):
    """Demander une réinitialisation de mot de passe."""
    try:
        # TODO: Implémenter la logique de réinitialisation
        # Cela inclurait l'envoi d'un email avec un token
        
        log_auth_event(
            event_type="password_reset_request",
            email=reset_data.email,
            success=True
        )
        
        return {
            "message": "Password reset instructions sent to your email"
        }
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )


@router.post("/password-reset-confirm")
async def confirm_password_reset(
    reset_data: UserPasswordResetConfirm,
    db: AsyncSession = Depends(get_async_db)
):
    """Confirmer la réinitialisation de mot de passe."""
    try:
        # TODO: Implémenter la logique de confirmation de réinitialisation
        
        log_auth_event(
            event_type="password_reset_confirm",
            success=True
        )
        
        return {
            "message": "Password reset successful"
        }
        
    except Exception as e:
        logger.error(f"Password reset confirmation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Déconnexion (invalider le token côté client)."""
    try:
        # La déconnexion côté serveur nécessiterait une blacklist de tokens
        # Pour l'instant, on log simplement l'événement
        
        log_auth_event(
            event_type="user_logout",
            user_id=str(current_user.id),
            username=current_user.username,
            success=True
        )
        
        return {
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Obtenir les informations de l'utilisateur actuel."""
    return UserResponse.from_orm(current_user)


@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """Vérifier la validité du token."""
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "username": current_user.username,
        "role": current_user.role.value
    }