"""Application FastAPI principale pour la gestion des déchets."""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import socketio

from app.core.config import settings
from app.core.database import init_db, close_db_connections, test_db_connection
from app.core.exceptions import BaseAPIException
from app.core.logging import get_logger, log_request, log_error
from app.api.v1 import api_router
from app.services.socketio_service import sio_app

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application."""
    # Startup
    logger.info("Starting Waste Management API")
    
    # Test de connexion à la base de données
    db_connected = await test_db_connection()
    if not db_connected:
        logger.error("Failed to connect to database")
        raise RuntimeError("Database connection failed")
    
    # Initialisation de la base de données
    await init_db()
    
    logger.info("Application started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down Waste Management API")
    await close_db_connections()
    logger.info("Application shut down successfully")


# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API complète pour la gestion des déchets avec authentification faciale",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
)

# Intégrer Socket.IO
socket_app = socketio.ASGIApp(sio_app, app)


# Middleware de sécurité
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # À configurer selon vos besoins
    )

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware de logging des requêtes
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware pour logger les requêtes HTTP."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Ajouter l'ID de requête aux headers
    request.state.request_id = request_id
    
    # Exécuter la requête
    response = await call_next(request)
    
    # Calculer la durée
    duration = time.time() - start_time
    
    # Logger la requête
    log_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=duration,
        user_id=getattr(request.state, 'user_id', None),
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent')
    )
    
    # Ajouter l'ID de requête à la réponse
    response.headers["X-Request-ID"] = request_id
    
    return response


# Gestionnaire d'erreurs global
@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """Gestionnaire pour les exceptions API personnalisées."""
    log_error(
        error_type=exc.__class__.__name__,
        error_message=exc.detail,
        request_id=getattr(request.state, 'request_id', None),
        user_id=getattr(request.state, 'user_id', None)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "request_id": getattr(request.state, 'request_id', None)
            }
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire pour les exceptions HTTP."""
    log_error(
        error_type="HTTPException",
        error_message=exc.detail,
        request_id=getattr(request.state, 'request_id', None),
        user_id=getattr(request.state, 'user_id', None)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "request_id": getattr(request.state, 'request_id', None)
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'erreurs global."""
    log_error(
        error_type="UnhandledException",
        error_message=str(exc),
        request_id=getattr(request.state, 'request_id', None),
        user_id=getattr(request.state, 'user_id', None)
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, 'request_id', None)
            }
        }
    )


# Routes de base
@app.get("/")
async def root():
    """Route racine."""
    return {
        "message": "Waste Management API",
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Contrôle de santé de l'application."""
    db_healthy = await test_db_connection()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "version": settings.APP_VERSION,
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": time.time()
    }


# Inclure les routes API
app.include_router(api_router, prefix="/api/v1")


# Documentation OpenAPI personnalisée
def custom_openapi():
    """Génération d'OpenAPI personnalisée."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API complète pour la gestion des déchets avec authentification faciale",
        routes=app.routes,
    )
    
    # Ajouter des informations de sécurité
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # Ajouter les tags
    openapi_schema["tags"] = [
        {
            "name": "Authentication",
            "description": "Endpoints d'authentification avec support de reconnaissance faciale"
        },
        {
            "name": "Users",
            "description": "Gestion des utilisateurs"
        },
        {
            "name": "Waste Records",
            "description": "Gestion des enregistrements de déchets"
        },
        {
            "name": "Statistics",
            "description": "Statistiques et tableaux de bord"
        },
        {
            "name": "Notifications",
            "description": "Système de notifications push"
        },
        {
            "name": "Admin",
            "description": "Fonctionnalités d'administration"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        access_log=False,  # Nous utilisons notre propre logging
        log_config=None
    )