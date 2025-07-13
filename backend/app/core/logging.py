"""Configuration du logging structuré avec structlog."""

import sys
import logging
from typing import Any, Dict
from pathlib import Path
import structlog
from structlog.stdlib import filter_by_level
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer, TimeStamper, add_logger_name, add_log_level

from app.core.config import settings


def setup_logging() -> None:
    """Configurer le logging de l'application."""
    
    # Configuration du logging standard
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Processeurs communs
    shared_processors = [
        filter_by_level,
        add_logger_name,
        add_log_level,
        TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Choisir le renderer selon l'environnement
    if settings.DEBUG:
        # En développement, utiliser le renderer console coloré
        renderer = ConsoleRenderer(colors=True)
    else:
        # En production, utiliser JSON
        renderer = JSONRenderer()
    
    # Configuration de structlog
    structlog.configure(
        processors=shared_processors + [renderer],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        cache_logger_on_first_use=True,
    )
    
    # Désactiver certains loggers trop verbeux
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Obtenir un logger configuré."""
    return structlog.get_logger(name)


class LoggerAdapter:
    """Adaptateur pour ajouter du contexte aux logs."""
    
    def __init__(self, logger: structlog.stdlib.BoundLogger):
        self.logger = logger
    
    def bind(self, **kwargs) -> "LoggerAdapter":
        """Lier du contexte au logger."""
        return LoggerAdapter(self.logger.bind(**kwargs))
    
    def info(self, msg: str, **kwargs) -> None:
        """Log info avec contexte."""
        self.logger.info(msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log warning avec contexte."""
        self.logger.warning(msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log error avec contexte."""
        self.logger.error(msg, **kwargs)
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log debug avec contexte."""
        self.logger.debug(msg, **kwargs)
    
    def exception(self, msg: str, **kwargs) -> None:
        """Log exception avec contexte."""
        self.logger.exception(msg, **kwargs)


def log_request(
    request_id: str,
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: str = None,
    **kwargs
) -> None:
    """Logger une requête HTTP."""
    logger = get_logger("http.request")
    logger.info(
        "HTTP Request",
        request_id=request_id,
        method=method,
        path=path,
        status_code=status_code,
        duration=duration,
        user_id=user_id,
        **kwargs
    )


def log_auth_event(
    event_type: str,
    user_id: str = None,
    username: str = None,
    email: str = None,
    success: bool = True,
    **kwargs
) -> None:
    """Logger un événement d'authentification."""
    logger = get_logger("auth")
    logger.info(
        "Authentication Event",
        event_type=event_type,
        user_id=user_id,
        username=username,
        email=email,
        success=success,
        **kwargs
    )


def log_database_event(
    operation: str,
    table: str,
    record_id: str = None,
    duration: float = None,
    success: bool = True,
    **kwargs
) -> None:
    """Logger un événement de base de données."""
    logger = get_logger("database")
    logger.info(
        "Database Event",
        operation=operation,
        table=table,
        record_id=record_id,
        duration=duration,
        success=success,
        **kwargs
    )


def log_face_recognition_event(
    event_type: str,
    user_id: str = None,
    success: bool = True,
    confidence: float = None,
    **kwargs
) -> None:
    """Logger un événement de reconnaissance faciale."""
    logger = get_logger("face_recognition")
    logger.info(
        "Face Recognition Event",
        event_type=event_type,
        user_id=user_id,
        success=success,
        confidence=confidence,
        **kwargs
    )


def log_notification_event(
    event_type: str,
    notification_id: str = None,
    user_id: str = None,
    notification_type: str = None,
    success: bool = True,
    **kwargs
) -> None:
    """Logger un événement de notification."""
    logger = get_logger("notification")
    logger.info(
        "Notification Event",
        event_type=event_type,
        notification_id=notification_id,
        user_id=user_id,
        notification_type=notification_type,
        success=success,
        **kwargs
    )


def log_socketio_event(
    event_type: str,
    event_name: str = None,
    user_id: str = None,
    room: str = None,
    success: bool = True,
    **kwargs
) -> None:
    """Logger un événement Socket.IO."""
    logger = get_logger("socketio")
    logger.info(
        "Socket.IO Event",
        event_type=event_type,
        event_name=event_name,
        user_id=user_id,
        room=room,
        success=success,
        **kwargs
    )


def log_security_event(
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    severity: str = "medium",
    **kwargs
) -> None:
    """Logger un événement de sécurité."""
    logger = get_logger("security")
    logger.warning(
        "Security Event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        severity=severity,
        **kwargs
    )


def log_error(
    error_type: str,
    error_message: str,
    user_id: str = None,
    request_id: str = None,
    **kwargs
) -> None:
    """Logger une erreur."""
    logger = get_logger("error")
    logger.error(
        "Application Error",
        error_type=error_type,
        error_message=error_message,
        user_id=user_id,
        request_id=request_id,
        **kwargs
    )


# Initialiser le logging au démarrage
setup_logging()