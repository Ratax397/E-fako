"""Endpoints pour la gestion des déchets."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import json
import os
import uuid as uuid_lib
from pathlib import Path

from app.core.database import get_async_db
from app.core.config import settings
from app.core.exceptions import NotFoundError, AuthorizationError, ValidationError
from app.core.logging import get_logger, log_database_event
from app.schemas.waste import (
    WasteRecordCreate, WasteRecordUpdate, WasteRecordResponse, WasteRecordList,
    WasteRecordValidation, WasteRecordProcessing, WasteStatisticsResponse,
    WasteCategoryCreate, WasteCategoryUpdate, WasteCategoryResponse,
    WasteImageUpload, WasteImageResponse
)
from app.models.waste import WasteRecord, WasteType, WasteStatus, WasteCategory
from app.models.user import User
from app.api.deps import (
    get_current_user, get_current_admin_user,
    get_pagination_params, get_search_params, get_date_range_params
)
from app.services.socketio_service import socket_service
from app.services.notification_service import notification_service
from app.schemas.notification import NotificationCreate
from app.models.notification import NotificationType

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=WasteRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_waste_record(
    waste_data: WasteRecordCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouvel enregistrement de déchets."""
    try:
        # Créer l'enregistrement
        waste_record = WasteRecord(
            user_id=current_user.id,
            waste_type=waste_data.waste_type,
            description=waste_data.description,
            quantity=waste_data.quantity,
            unit=waste_data.unit,
            location=waste_data.location,
            latitude=waste_data.latitude,
            longitude=waste_data.longitude,
            address=waste_data.address
        )
        
        # Traiter les images si fournies
        if waste_data.image_files:
            image_paths = []
            for i, image_data in enumerate(waste_data.image_files):
                # Sauvegarder l'image
                image_path = await save_waste_image(image_data, waste_record.id, i)
                image_paths.append(image_path)
            
            waste_record.image_paths = json.dumps(image_paths)
        
        db.add(waste_record)
        await db.commit()
        await db.refresh(waste_record)
        
        # Calculer le score environnemental initial
        environmental_score = calculate_environmental_score(waste_record)
        points = calculate_points(waste_record, environmental_score)
        
        waste_record.environmental_score = environmental_score
        waste_record.points_awarded = points
        
        await db.commit()
        
        # Notifier les admins via Socket.IO
        await socket_service.broadcast_waste_update({
            "id": str(waste_record.id),
            "user_id": str(current_user.id),
            "username": current_user.username,
            "waste_type": waste_record.waste_type.value,
            "quantity": waste_record.quantity,
            "status": waste_record.status.value,
            "created_at": waste_record.created_at.isoformat(),
            "action": "created"
        })
        
        # Créer une notification pour les admins
        await notification_service.broadcast_notification(db, {
            "title": "Nouvel enregistrement de déchets",
            "message": f"{current_user.username} a enregistré {waste_record.quantity}kg de {waste_record.waste_type.value}",
            "notification_type": NotificationType.WASTE_UPDATE,
            "target_roles": ["admin", "super_admin"],
            "data": {
                "waste_record_id": str(waste_record.id),
                "user_id": str(current_user.id)
            }
        })
        
        log_database_event(
            operation="create",
            table="waste_records",
            record_id=str(waste_record.id),
            success=True,
            user_id=str(current_user.id)
        )
        
        return WasteRecordResponse.from_orm(waste_record)
        
    except Exception as e:
        logger.error(f"Error creating waste record: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create waste record"
        )


@router.get("/", response_model=WasteRecordList)
async def get_waste_records(
    db: AsyncSession = Depends(get_async_db),
    pagination: dict = Depends(get_pagination_params),
    search: dict = Depends(get_search_params),
    date_range: dict = Depends(get_date_range_params),
    waste_type: Optional[WasteType] = None,
    status: Optional[WasteStatus] = None,
    current_user: User = Depends(get_current_user)
):
    """Obtenir la liste des enregistrements de déchets."""
    try:
        # Construire la requête de base
        query = select(WasteRecord).options(selectinload(WasteRecord.user))
        
        # Filtrer par utilisateur si pas admin
        if not current_user.is_admin:
            query = query.where(WasteRecord.user_id == current_user.id)
        
        # Ajouter les filtres
        filters = []
        
        if waste_type:
            filters.append(WasteRecord.waste_type == waste_type)
        
        if status:
            filters.append(WasteRecord.status == status)
        
        if date_range["start_date"]:
            start_date = datetime.fromisoformat(date_range["start_date"])
            filters.append(WasteRecord.created_at >= start_date)
        
        if date_range["end_date"]:
            end_date = datetime.fromisoformat(date_range["end_date"])
            filters.append(WasteRecord.created_at <= end_date)
        
        if search["search"]:
            search_term = f"%{search['search']}%"
            filters.append(
                or_(
                    WasteRecord.description.ilike(search_term),
                    WasteRecord.location.ilike(search_term)
                )
            )
        
        if filters:
            query = query.where(and_(*filters))
        
        # Ajouter le tri
        if search["sort_by"]:
            sort_column = getattr(WasteRecord, search["sort_by"], None)
            if sort_column:
                if search["sort_order"] == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(WasteRecord.created_at.desc())
        
        # Compter le total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Appliquer la pagination
        query = query.offset(pagination["offset"]).limit(pagination["limit"])
        
        # Exécuter la requête
        result = await db.execute(query)
        waste_records = result.scalars().all()
        
        # Calculer les informations de pagination
        has_next = pagination["offset"] + pagination["limit"] < total
        has_previous = pagination["offset"] > 0
        
        log_database_event(
            operation="select",
            table="waste_records",
            success=True,
            count=len(waste_records),
            user_id=str(current_user.id)
        )
        
        return WasteRecordList(
            waste_records=[WasteRecordResponse.from_orm(record) for record in waste_records],
            total=total,
            page=pagination["page"],
            size=pagination["size"],
            has_next=has_next,
            has_previous=has_previous
        )
        
    except Exception as e:
        logger.error(f"Error fetching waste records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch waste records"
        )


@router.get("/{record_id}", response_model=WasteRecordResponse)
async def get_waste_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir un enregistrement de déchets par ID."""
    try:
        # Récupérer l'enregistrement
        result = await db.execute(
            select(WasteRecord).options(selectinload(WasteRecord.user))
            .where(WasteRecord.id == record_id)
        )
        waste_record = result.scalar_one_or_none()
        
        if not waste_record:
            raise NotFoundError("Waste record not found")
        
        # Vérifier les permissions
        if not current_user.is_admin and waste_record.user_id != current_user.id:
            raise AuthorizationError("You can only access your own waste records")
        
        log_database_event(
            operation="select",
            table="waste_records",
            record_id=str(record_id),
            success=True,
            user_id=str(current_user.id)
        )
        
        return WasteRecordResponse.from_orm(waste_record)
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error fetching waste record {record_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch waste record"
        )


@router.put("/{record_id}", response_model=WasteRecordResponse)
async def update_waste_record(
    record_id: UUID,
    waste_update: WasteRecordUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un enregistrement de déchets."""
    try:
        # Récupérer l'enregistrement
        result = await db.execute(
            select(WasteRecord).where(WasteRecord.id == record_id)
        )
        waste_record = result.scalar_one_or_none()
        
        if not waste_record:
            raise NotFoundError("Waste record not found")
        
        # Vérifier les permissions
        if not current_user.is_admin and waste_record.user_id != current_user.id:
            raise AuthorizationError("You can only update your own waste records")
        
        # Mettre à jour les champs fournis
        update_data = waste_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(waste_record, field):
                setattr(waste_record, field, value)
        
        # Recalculer le score si nécessaire
        if any(field in update_data for field in ['waste_type', 'quantity']):
            environmental_score = calculate_environmental_score(waste_record)
            points = calculate_points(waste_record, environmental_score)
            
            waste_record.environmental_score = environmental_score
            waste_record.points_awarded = points
        
        await db.commit()
        await db.refresh(waste_record)
        
        # Notifier via Socket.IO
        await socket_service.broadcast_waste_update({
            "id": str(waste_record.id),
            "user_id": str(waste_record.user_id),
            "waste_type": waste_record.waste_type.value,
            "quantity": waste_record.quantity,
            "status": waste_record.status.value,
            "updated_at": waste_record.updated_at.isoformat() if waste_record.updated_at else None,
            "action": "updated"
        })
        
        log_database_event(
            operation="update",
            table="waste_records",
            record_id=str(record_id),
            success=True,
            user_id=str(current_user.id)
        )
        
        return WasteRecordResponse.from_orm(waste_record)
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error updating waste record {record_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update waste record"
        )


@router.delete("/{record_id}")
async def delete_waste_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un enregistrement de déchets."""
    try:
        # Récupérer l'enregistrement
        result = await db.execute(
            select(WasteRecord).where(WasteRecord.id == record_id)
        )
        waste_record = result.scalar_one_or_none()
        
        if not waste_record:
            raise NotFoundError("Waste record not found")
        
        # Vérifier les permissions
        if not current_user.is_admin and waste_record.user_id != current_user.id:
            raise AuthorizationError("You can only delete your own waste records")
        
        # Supprimer les images associées
        if waste_record.image_paths:
            try:
                image_paths = json.loads(waste_record.image_paths)
                for image_path in image_paths:
                    if os.path.exists(image_path):
                        os.remove(image_path)
            except (json.JSONDecodeError, OSError):
                pass
        
        # Supprimer l'enregistrement
        await db.delete(waste_record)
        await db.commit()
        
        log_database_event(
            operation="delete",
            table="waste_records",
            record_id=str(record_id),
            success=True,
            user_id=str(current_user.id)
        )
        
        return {"message": "Waste record deleted successfully"}
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error deleting waste record {record_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete waste record"
        )


@router.post("/{record_id}/process")
async def process_waste_record(
    record_id: UUID,
    processing_data: WasteRecordProcessing,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Traiter un enregistrement de déchets (admins seulement)."""
    try:
        # Récupérer l'enregistrement
        result = await db.execute(
            select(WasteRecord).options(selectinload(WasteRecord.user))
            .where(WasteRecord.id == record_id)
        )
        waste_record = result.scalar_one_or_none()
        
        if not waste_record:
            raise NotFoundError("Waste record not found")
        
        # Mettre à jour le statut et les informations de traitement
        waste_record.status = processing_data.status
        waste_record.processing_notes = processing_data.processing_notes
        waste_record.processor_id = current_user.id
        
        # Définir les dates selon le statut
        now = datetime.utcnow()
        if processing_data.status == WasteStatus.COLLECTED:
            waste_record.collection_date = now
        elif processing_data.status == WasteStatus.PROCESSED:
            waste_record.processing_date = now
        elif processing_data.status in [WasteStatus.RECYCLED, WasteStatus.DISPOSED]:
            waste_record.completion_date = now
        
        await db.commit()
        
        # Notifier l'utilisateur
        await notification_service.create_notification(db, NotificationCreate(
            user_id=waste_record.user_id,
            title="Mise à jour de votre déchet",
            message=f"Votre enregistrement de {waste_record.waste_type.value} a été {processing_data.status.value}",
            notification_type=NotificationType.WASTE_UPDATE,
            data={
                "waste_record_id": str(waste_record.id),
                "status": processing_data.status.value
            }
        ))
        
        # Notifier via Socket.IO
        await socket_service.broadcast_waste_update({
            "id": str(waste_record.id),
            "user_id": str(waste_record.user_id),
            "status": waste_record.status.value,
            "processor_id": str(current_user.id),
            "processing_notes": processing_data.processing_notes,
            "action": "processed"
        })
        
        log_database_event(
            operation="update",
            table="waste_records",
            record_id=str(record_id),
            success=True,
            user_id=str(current_user.id),
            action="process"
        )
        
        return {"message": "Waste record processed successfully"}
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error processing waste record {record_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process waste record"
        )


@router.post("/{record_id}/validate")
async def validate_waste_record(
    record_id: UUID,
    validation_data: WasteRecordValidation,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Valider un enregistrement de déchets (admins seulement)."""
    try:
        # Récupérer l'enregistrement
        result = await db.execute(
            select(WasteRecord).options(selectinload(WasteRecord.user))
            .where(WasteRecord.id == record_id)
        )
        waste_record = result.scalar_one_or_none()
        
        if not waste_record:
            raise NotFoundError("Waste record not found")
        
        # Mettre à jour la validation
        waste_record.is_validated = validation_data.is_valid
        waste_record.validated_by = current_user.id
        waste_record.validation_date = datetime.utcnow()
        waste_record.validation_notes = validation_data.validation_notes
        
        if validation_data.environmental_score is not None:
            waste_record.environmental_score = validation_data.environmental_score
        
        if validation_data.points_awarded is not None:
            waste_record.points_awarded = validation_data.points_awarded
        
        await db.commit()
        
        # Notifier l'utilisateur
        status_message = "validé" if validation_data.is_valid else "rejeté"
        await notification_service.create_notification(db, NotificationCreate(
            user_id=waste_record.user_id,
            title="Validation de votre déchet",
            message=f"Votre enregistrement de {waste_record.waste_type.value} a été {status_message}",
            notification_type=NotificationType.WASTE_UPDATE,
            data={
                "waste_record_id": str(waste_record.id),
                "is_valid": validation_data.is_valid,
                "points_awarded": validation_data.points_awarded
            }
        ))
        
        log_database_event(
            operation="update",
            table="waste_records",
            record_id=str(record_id),
            success=True,
            user_id=str(current_user.id),
            action="validate"
        )
        
        return {"message": "Waste record validated successfully"}
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error validating waste record {record_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate waste record"
        )


@router.post("/{record_id}/upload-image", response_model=WasteImageResponse)
async def upload_waste_image(
    record_id: UUID,
    image_data: WasteImageUpload,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Ajouter une image à un enregistrement de déchets."""
    try:
        # Récupérer l'enregistrement
        result = await db.execute(
            select(WasteRecord).where(WasteRecord.id == record_id)
        )
        waste_record = result.scalar_one_or_none()
        
        if not waste_record:
            raise NotFoundError("Waste record not found")
        
        # Vérifier les permissions
        if not current_user.is_admin and waste_record.user_id != current_user.id:
            raise AuthorizationError("You can only upload images to your own waste records")
        
        # Sauvegarder l'image
        image_path = await save_waste_image(image_data.image, record_id)
        
        # Mettre à jour l'enregistrement
        existing_paths = []
        if waste_record.image_paths:
            try:
                existing_paths = json.loads(waste_record.image_paths)
            except json.JSONDecodeError:
                existing_paths = []
        
        existing_paths.append(image_path)
        waste_record.image_paths = json.dumps(existing_paths)
        
        await db.commit()
        
        # Générer l'URL de l'image
        image_url = f"/api/v1/waste/images/{Path(image_path).name}"
        
        return WasteImageResponse(
            image_url=image_url,
            image_path=image_path
        )
        
    except (NotFoundError, AuthorizationError):
        raise
    except Exception as e:
        logger.error(f"Error uploading image for waste record {record_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )


# Fonctions utilitaires
async def save_waste_image(image_data: str, record_id: UUID, index: int = 0) -> str:
    """Sauvegarder une image de déchets."""
    try:
        # Décoder l'image base64
        header, encoded = image_data.split(',', 1)
        image_bytes = base64.b64decode(encoded)
        
        # Générer un nom de fichier unique
        file_extension = "jpg"  # Par défaut
        if "png" in header:
            file_extension = "png"
        elif "jpeg" in header or "jpg" in header:
            file_extension = "jpg"
        
        filename = f"{record_id}_{index}_{uuid_lib.uuid4().hex[:8]}.{file_extension}"
        file_path = settings.UPLOAD_DIR / "waste_images" / filename
        
        # Créer le répertoire si nécessaire
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder l'image
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Error saving waste image: {e}")
        raise


def calculate_environmental_score(waste_record: WasteRecord) -> float:
    """Calculer le score environnemental d'un enregistrement."""
    # Multiplieurs par type de déchet
    type_multipliers = {
        WasteType.ORGANIC: 1.0,
        WasteType.PLASTIC: 1.5,
        WasteType.PAPER: 1.2,
        WasteType.GLASS: 1.3,
        WasteType.METAL: 1.4,
        WasteType.ELECTRONIC: 2.0,
        WasteType.HAZARDOUS: 2.5,
        WasteType.TEXTILE: 1.1,
        WasteType.OTHER: 1.0
    }
    
    multiplier = type_multipliers.get(waste_record.waste_type, 1.0)
    base_score = waste_record.quantity * multiplier * 10
    
    # Bonus pour la géolocalisation
    if waste_record.latitude and waste_record.longitude:
        base_score *= 1.1
    
    # Bonus pour la description détaillée
    if waste_record.description and len(waste_record.description) > 20:
        base_score *= 1.05
    
    return min(base_score, 100.0)  # Score maximum de 100


def calculate_points(waste_record: WasteRecord, environmental_score: float) -> int:
    """Calculer les points attribués pour un enregistrement."""
    base_points = int(environmental_score / 10)
    
    # Bonus pour certains types de déchets
    bonus_points = 0
    if waste_record.waste_type in [WasteType.ELECTRONIC, WasteType.HAZARDOUS]:
        bonus_points = 5
    elif waste_record.waste_type in [WasteType.PLASTIC, WasteType.METAL]:
        bonus_points = 3
    
    return base_points + bonus_points