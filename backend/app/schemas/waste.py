"""Schémas Pydantic pour les déchets."""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.waste import WasteType, WasteStatus


class WasteRecordBase(BaseModel):
    """Schéma de base pour les enregistrements de déchets."""
    waste_type: WasteType
    description: Optional[str] = None
    quantity: float = Field(..., gt=0)
    unit: str = Field(default="kg", max_length=20)
    location: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = None


class WasteRecordCreate(WasteRecordBase):
    """Schéma pour créer un enregistrement de déchets."""
    image_files: Optional[List[str]] = None  # Base64 encoded images
    
    @validator('image_files')
    def validate_image_files(cls, v):
        if v:
            for image in v:
                if not image.startswith('data:image/'):
                    raise ValueError('Invalid image format')
        return v
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        if v > 1000:  # Maximum 1000 kg per record
            raise ValueError('Quantity too large')
        return v


class WasteRecordUpdate(BaseModel):
    """Schéma pour mettre à jour un enregistrement de déchets."""
    waste_type: Optional[WasteType] = None
    description: Optional[str] = None
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = None
    status: Optional[WasteStatus] = None
    processing_notes: Optional[str] = None
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be positive')
        return v


class WasteRecordInDB(WasteRecordBase):
    """Schéma pour les enregistrements de déchets en base de données."""
    id: UUID
    user_id: UUID
    status: WasteStatus
    collection_date: Optional[datetime] = None
    processing_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processor_id: Optional[UUID] = None
    processing_notes: Optional[str] = None
    environmental_score: float = 0.0
    points_awarded: int = 0
    is_validated: bool = False
    validated_by: Optional[UUID] = None
    validation_date: Optional[datetime] = None
    validation_notes: Optional[str] = None
    image_paths: Optional[List[str]] = None
    
    class Config:
        orm_mode = True
        use_enum_values = True


class WasteRecordResponse(WasteRecordBase):
    """Schéma pour les réponses d'enregistrement de déchets."""
    id: UUID
    user_id: UUID
    status: WasteStatus
    collection_date: Optional[datetime] = None
    processing_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    created_at: datetime
    environmental_score: float = 0.0
    points_awarded: int = 0
    is_validated: bool = False
    image_paths: Optional[List[str]] = None
    duration_days: Optional[int] = None
    
    class Config:
        orm_mode = True
        use_enum_values = True


class WasteRecordList(BaseModel):
    """Schéma pour la liste des enregistrements de déchets."""
    waste_records: List[WasteRecordResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool
    
    class Config:
        orm_mode = True


class WasteRecordValidation(BaseModel):
    """Schéma pour valider un enregistrement de déchets."""
    is_valid: bool
    validation_notes: Optional[str] = None
    environmental_score: Optional[float] = Field(None, ge=0, le=100)
    points_awarded: Optional[int] = Field(None, ge=0)


class WasteRecordProcessing(BaseModel):
    """Schéma pour traiter un enregistrement de déchets."""
    status: WasteStatus
    processing_notes: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = [
            WasteStatus.COLLECTED,
            WasteStatus.PROCESSED,
            WasteStatus.RECYCLED,
            WasteStatus.DISPOSED,
            WasteStatus.REJECTED
        ]
        if v not in allowed_statuses:
            raise ValueError('Invalid processing status')
        return v


class WasteStatisticsResponse(BaseModel):
    """Schéma pour les statistiques des déchets."""
    total_waste_kg: float
    total_records: int
    total_users: int
    waste_by_type: Dict[str, float]
    waste_by_status: Dict[str, int]
    recycled_percentage: float
    environmental_score_avg: float
    top_contributors: List[Dict[str, Any]]
    monthly_trends: List[Dict[str, Any]]
    
    class Config:
        orm_mode = True


class WasteCategoryBase(BaseModel):
    """Schéma de base pour les catégories de déchets."""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    color_code: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    base_points: int = Field(default=1, ge=0)
    environmental_multiplier: float = Field(default=1.0, ge=0)
    
    @validator('color_code')
    def validate_color_code(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color code must start with #')
        return v


class WasteCategoryCreate(WasteCategoryBase):
    """Schéma pour créer une catégorie de déchets."""
    pass


class WasteCategoryUpdate(BaseModel):
    """Schéma pour mettre à jour une catégorie de déchets."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    color_code: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    base_points: Optional[int] = Field(None, ge=0)
    environmental_multiplier: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    
    @validator('color_code')
    def validate_color_code(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color code must start with #')
        return v


class WasteCategoryResponse(WasteCategoryBase):
    """Schéma pour les réponses de catégorie de déchets."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class WasteImageUpload(BaseModel):
    """Schéma pour l'upload d'images de déchets."""
    image: str  # Base64 encoded image
    
    @validator('image')
    def validate_image(cls, v):
        if not v.startswith('data:image/'):
            raise ValueError('Invalid image format')
        return v


class WasteImageResponse(BaseModel):
    """Schéma pour les réponses d'images de déchets."""
    image_url: str
    image_path: str
    
    class Config:
        orm_mode = True