"""Schémas Pydantic pour les utilisateurs."""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import re

from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^[\+]?[1-9][\d]{0,15}$', v):
            raise ValueError('Invalid phone number format')
        return v


class UserCreate(UserBase):
    """Schéma pour créer un utilisateur."""
    password: str = Field(..., min_length=8)
    confirm_password: str
    role: Optional[UserRole] = UserRole.USER
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    
    @validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^[\+]?[1-9][\d]{0,15}$', v):
            raise ValueError('Invalid phone number format')
        return v


class UserInDB(UserBase):
    """Schéma pour les utilisateurs en base de données."""
    id: UUID
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    notification_preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True
        use_enum_values = True


class UserResponse(UserBase):
    """Schéma pour les réponses utilisateur."""
    id: UUID
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    full_name: str
    
    class Config:
        orm_mode = True
        use_enum_values = True


class UserFaceRegister(BaseModel):
    """Schéma pour l'enregistrement facial."""
    user_id: UUID
    face_image: str  # Base64 encoded image
    
    @validator('face_image')
    def validate_face_image(cls, v):
        if not v.startswith('data:image/'):
            raise ValueError('Invalid image format')
        return v


class UserFaceLogin(BaseModel):
    """Schéma pour la connexion faciale."""
    face_image: str  # Base64 encoded image
    
    @validator('face_image')
    def validate_face_image(cls, v):
        if not v.startswith('data:image/'):
            raise ValueError('Invalid image format')
        return v


class UserLogin(BaseModel):
    """Schéma pour la connexion utilisateur."""
    username: str
    password: str


class UserPasswordReset(BaseModel):
    """Schéma pour la réinitialisation du mot de passe."""
    email: EmailStr


class UserPasswordResetConfirm(BaseModel):
    """Schéma pour confirmer la réinitialisation du mot de passe."""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserStatistics(BaseModel):
    """Schéma pour les statistiques utilisateur."""
    total_users: int
    active_users: int
    verified_users: int
    users_this_month: int
    users_by_role: Dict[str, int]
    users_by_status: Dict[str, int]
    
    class Config:
        orm_mode = True


class UserList(BaseModel):
    """Schéma pour la liste des utilisateurs."""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_previous: bool
    
    class Config:
        orm_mode = True