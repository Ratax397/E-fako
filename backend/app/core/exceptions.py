"""Exceptions personnalisées pour l'application."""

from fastapi import HTTPException
from typing import Optional, Dict, Any


class BaseAPIException(HTTPException):
    """Exception de base pour l'API."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationError(BaseAPIException):
    """Erreur de validation des données."""
    
    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code=error_code
        )


class AuthenticationError(BaseAPIException):
    """Erreur d'authentification."""
    
    def __init__(self, detail: str = "Authentication failed", error_code: str = "AUTH_ERROR"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code=error_code
        )


class AuthorizationError(BaseAPIException):
    """Erreur d'autorisation."""
    
    def __init__(self, detail: str = "Not authorized", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code=error_code
        )


class NotFoundError(BaseAPIException):
    """Erreur de ressource non trouvée."""
    
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=404,
            detail=detail,
            error_code=error_code
        )


class ConflictError(BaseAPIException):
    """Erreur de conflit."""
    
    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT"):
        super().__init__(
            status_code=409,
            detail=detail,
            error_code=error_code
        )


class RateLimitError(BaseAPIException):
    """Erreur de limitation du taux de requêtes."""
    
    def __init__(self, detail: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT"):
        super().__init__(
            status_code=429,
            detail=detail,
            error_code=error_code
        )


class InternalServerError(BaseAPIException):
    """Erreur interne du serveur."""
    
    def __init__(self, detail: str = "Internal server error", error_code: str = "INTERNAL_ERROR"):
        super().__init__(
            status_code=500,
            detail=detail,
            error_code=error_code
        )


class DatabaseError(InternalServerError):
    """Erreur de base de données."""
    
    def __init__(self, detail: str = "Database error", error_code: str = "DATABASE_ERROR"):
        super().__init__(detail=detail, error_code=error_code)


class FileUploadError(BaseAPIException):
    """Erreur d'upload de fichier."""
    
    def __init__(self, detail: str = "File upload error", error_code: str = "FILE_UPLOAD_ERROR"):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code=error_code
        )


class FaceRecognitionError(BaseAPIException):
    """Erreur de reconnaissance faciale."""
    
    def __init__(self, detail: str = "Face recognition error", error_code: str = "FACE_RECOGNITION_ERROR"):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code=error_code
        )


class NotificationError(InternalServerError):
    """Erreur de notification."""
    
    def __init__(self, detail: str = "Notification error", error_code: str = "NOTIFICATION_ERROR"):
        super().__init__(detail=detail, error_code=error_code)


class SocketIOError(InternalServerError):
    """Erreur Socket.IO."""
    
    def __init__(self, detail: str = "Socket.IO error", error_code: str = "SOCKETIO_ERROR"):
        super().__init__(detail=detail, error_code=error_code)