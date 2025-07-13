"""Modèle WasteRecord pour la base de données MySQL."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from typing import Optional

from app.core.database import Base


class WasteType(enum.Enum):
    """Types de déchets."""
    ORGANIC = "organic"
    PLASTIC = "plastic"
    PAPER = "paper"
    GLASS = "glass"
    METAL = "metal"
    ELECTRONIC = "electronic"
    HAZARDOUS = "hazardous"
    TEXTILE = "textile"
    OTHER = "other"


class WasteStatus(enum.Enum):
    """Statuts des déchets."""
    PENDING = "pending"
    COLLECTED = "collected"
    PROCESSED = "processed"
    RECYCLED = "recycled"
    DISPOSED = "disposed"
    REJECTED = "rejected"


class WasteRecord(Base):
    """Modèle d'enregistrement de déchets."""
    
    __tablename__ = "waste_records"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    
    # Informations sur le déchet
    waste_type = Column(Enum(WasteType), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Float, nullable=False)  # en kg
    unit = Column(String(20), default="kg", nullable=False)
    
    # Localisation
    location = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(Text, nullable=True)
    
    # Images
    image_paths = Column(Text, nullable=True)  # JSON string array
    
    # Statut et traçabilité
    status = Column(Enum(WasteStatus), default=WasteStatus.PENDING, nullable=False)
    collection_date = Column(DateTime(timezone=True), nullable=True)
    processing_date = Column(DateTime(timezone=True), nullable=True)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Informations de traitement
    processor_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    processing_notes = Column(Text, nullable=True)
    
    # Score et points
    environmental_score = Column(Float, default=0.0)
    points_awarded = Column(Integer, default=0)
    
    # Validation
    is_validated = Column(Boolean, default=False)
    validated_by = Column(CHAR(36), ForeignKey("users.id"), nullable=True)
    validation_date = Column(DateTime(timezone=True), nullable=True)
    validation_notes = Column(Text, nullable=True)
    
    # Relations
    user = relationship("User", back_populates="waste_records", foreign_keys=[user_id])
    processor = relationship("User", foreign_keys=[processor_id])
    validator = relationship("User", foreign_keys=[validated_by])
    
    def __repr__(self):
        return f"<WasteRecord {self.id} - {self.waste_type.value}>"
    
    @property
    def is_completed(self) -> bool:
        """Vérifie si l'enregistrement est terminé."""
        return self.status in [WasteStatus.RECYCLED, WasteStatus.DISPOSED]
    
    @property
    def duration_days(self) -> Optional[int]:
        """Calcule la durée en jours depuis la création."""
        if self.completion_date:
            return (self.completion_date - self.created_at).days
        return (datetime.utcnow() - self.created_at).days


class WasteCategory(Base):
    """Catégories de déchets configurables."""
    
    __tablename__ = "waste_categories"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color_code = Column(String(7), nullable=True)  # Hex color
    icon = Column(String(50), nullable=True)
    
    # Points et scoring
    base_points = Column(Integer, default=1)
    environmental_multiplier = Column(Float, default=1.0)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<WasteCategory {self.name}>"


class WasteStatistics(Base):
    """Statistiques agrégées des déchets."""
    
    __tablename__ = "waste_statistics"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Période
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Statistiques globales
    total_waste_kg = Column(Float, default=0.0)
    total_records = Column(Integer, default=0)
    total_users = Column(Integer, default=0)
    
    # Par type de déchet
    organic_kg = Column(Float, default=0.0)
    plastic_kg = Column(Float, default=0.0)
    paper_kg = Column(Float, default=0.0)
    glass_kg = Column(Float, default=0.0)
    metal_kg = Column(Float, default=0.0)
    electronic_kg = Column(Float, default=0.0)
    hazardous_kg = Column(Float, default=0.0)
    textile_kg = Column(Float, default=0.0)
    other_kg = Column(Float, default=0.0)
    
    # Taux de recyclage
    recycled_percentage = Column(Float, default=0.0)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<WasteStatistics {self.period_start} - {self.period_end}>"