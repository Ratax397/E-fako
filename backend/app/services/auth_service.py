"""Service d'authentification avec JWT et reconnaissance faciale."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import bcrypt
import secrets
try:
    import face_recognition
    import numpy as np
    from numpy import ndarray
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    face_recognition = None
    np = None
    # Type placeholders
    class ndarray:
        pass

from PIL import Image
import base64
import io
import os
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.config import settings
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserLogin, UserFaceLogin, UserFaceRegister
from app.core.database import get_db, get_async_db
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service d'authentification."""
    
    def __init__(self):
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        
        # Chiffrement pour les données biométriques
        self.cipher_suite = Fernet(settings.BIOMETRIC_ENCRYPTION_KEY.encode())
    
    def hash_password(self, password: str) -> str:
        """Hacher un mot de passe."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Créer un token d'accès JWT."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Créer un token de rafraîchissement JWT."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Vérifier un token JWT."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid token")
    
    def generate_verification_token(self) -> str:
        """Générer un token de vérification."""
        return secrets.token_urlsafe(32)
    
    def generate_reset_token(self) -> str:
        """Générer un token de réinitialisation."""
        return secrets.token_urlsafe(32)
    
    async def register_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Enregistrer un nouvel utilisateur."""
        # Vérifier que l'email n'existe pas déjà
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ValidationError("Email already registered")
        
        # Vérifier que le nom d'utilisateur n'existe pas déjà
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValidationError("Username already taken")
        
        # Créer l'utilisateur
        hashed_password = self.hash_password(user_data.password)
        verification_token = self.generate_verification_token()
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            address=user_data.address,
            role=user_data.role,
            verification_token=verification_token,
            verification_token_expires=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"User registered: {user_data.email}")
        return db_user
    
    async def authenticate_user(self, db: AsyncSession, user_data: UserLogin) -> Optional[User]:
        """Authentifier un utilisateur par nom d'utilisateur/mot de passe."""
        result = await db.execute(
            select(User).where(
                and_(
                    User.username == user_data.username,
                    User.is_active == True
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not self.verify_password(user_data.password, user.hashed_password):
            # Incrémenter le compteur de tentatives
            user.login_attempts += 1
            await db.commit()
            return None
        
        # Réinitialiser le compteur de tentatives et mettre à jour last_login
        user.login_attempts = 0
        user.last_login = datetime.utcnow()
        await db.commit()
        
        logger.info(f"User authenticated: {user.username}")
        return user
    
    def encode_face_data(self, face_encoding: ndarray) -> bytes:
        """Chiffrer les données faciales."""
        if not FACE_RECOGNITION_AVAILABLE:
            raise ImportError("Face recognition library not available")
        face_bytes = face_encoding.tobytes()
        encrypted_data = self.cipher_suite.encrypt(face_bytes)
        return encrypted_data
    
    def decode_face_data(self, encrypted_data: bytes) -> ndarray:
        """Déchiffrer les données faciales."""
        if not FACE_RECOGNITION_AVAILABLE:
            raise ImportError("Face recognition library not available")
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        face_encoding = np.frombuffer(decrypted_data, dtype=np.float64)
        return face_encoding
    
    def extract_face_encoding(self, image_data: str) -> Optional[ndarray]:
        """Extraire l'encodage facial d'une image."""
        if not FACE_RECOGNITION_AVAILABLE:
            raise ImportError("Face recognition library not available")
            
        try:
            # Décoder l'image base64
            header, encoded = image_data.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            
            # Charger l'image
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            
            # Extraire les encodages faciaux
            face_encodings = face_recognition.face_encodings(
                image_array, 
                model=settings.FACE_RECOGNITION_MODEL
            )
            
            if len(face_encodings) == 0:
                return None
            
            # Retourner le premier encodage trouvé
            return face_encodings[0]
            
        except Exception as e:
            logger.error(f"Error extracting face encoding: {e}")
            return None
    
    async def register_face(self, db: AsyncSession, face_data: UserFaceRegister) -> bool:
        """Enregistrer les données faciales d'un utilisateur."""
        # Vérifier que l'utilisateur existe
        result = await db.execute(
            select(User).where(User.id == face_data.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValidationError("User not found")
        
        # Extraire l'encodage facial
        face_encoding = self.extract_face_encoding(face_data.face_image)
        if face_encoding is None:
            raise ValidationError("No face detected in image")
        
        # Chiffrer et sauvegarder les données
        encrypted_encoding = self.encode_face_data(face_encoding)
        
        # Sauvegarder l'image (optionnel)
        face_image_path = None
        if settings.FACE_ENCODINGS_DIR:
            face_image_filename = f"{user.id}_face.jpg"
            face_image_path = os.path.join(settings.FACE_ENCODINGS_DIR, face_image_filename)
            
            # Sauvegarder l'image
            header, encoded = face_data.face_image.split(',', 1)
            image_bytes = base64.b64decode(encoded)
            with open(face_image_path, 'wb') as f:
                f.write(image_bytes)
        
        # Mettre à jour l'utilisateur
        user.face_encoding = encrypted_encoding
        user.face_encoding_hash = secrets.token_hex(32)
        user.face_image_path = face_image_path
        
        await db.commit()
        
        logger.info(f"Face registered for user: {user.username}")
        return True
    
    async def authenticate_face(self, db: AsyncSession, face_data: UserFaceLogin) -> Optional[User]:
        """Authentifier un utilisateur par reconnaissance faciale."""
        # Extraire l'encodage facial de l'image fournie
        login_face_encoding = self.extract_face_encoding(face_data.face_image)
        if login_face_encoding is None:
            return None
        
        # Récupérer tous les utilisateurs avec des données faciales
        result = await db.execute(
            select(User).where(
                and_(
                    User.face_encoding.is_not(None),
                    User.is_active == True
                )
            )
        )
        users = result.scalars().all()
        
        # Comparer avec chaque utilisateur
        for user in users:
            try:
                # Déchiffrer l'encodage facial stocké
                stored_face_encoding = self.decode_face_data(user.face_encoding)
                
                # Comparer les encodages
                matches = face_recognition.compare_faces(
                    [stored_face_encoding], 
                    login_face_encoding,
                    tolerance=settings.FACE_RECOGNITION_TOLERANCE
                )
                
                if matches[0]:
                    # Mettre à jour last_login
                    user.last_login = datetime.utcnow()
                    await db.commit()
                    
                    logger.info(f"User authenticated by face: {user.username}")
                    return user
                    
            except Exception as e:
                logger.error(f"Error comparing face for user {user.username}: {e}")
                continue
        
        return None
    
    async def login_user(self, db: AsyncSession, user_data: UserLogin) -> Dict[str, Any]:
        """Connecter un utilisateur et retourner les tokens."""
        user = await self.authenticate_user(db, user_data)
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Account is not active")
        
        # Créer les tokens
        access_token = self.create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value}
        )
        refresh_token = self.create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    
    async def login_face(self, db: AsyncSession, face_data: UserFaceLogin) -> Dict[str, Any]:
        """Connecter un utilisateur par reconnaissance faciale."""
        user = await self.authenticate_face(db, face_data)
        if not user:
            raise AuthenticationError("Face not recognized")
        
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Account is not active")
        
        # Créer les tokens
        access_token = self.create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value}
        )
        refresh_token = self.create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    
    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> Dict[str, Any]:
        """Rafraîchir un token d'accès."""
        try:
            payload = self.verify_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("Invalid token payload")
            
            # Vérifier que l'utilisateur existe toujours
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")
            
            # Créer un nouveau token d'accès
            access_token = self.create_access_token(
                data={"sub": str(user.id), "username": user.username, "role": user.role.value}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Refresh token expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid refresh token")


# Instance globale du service d'authentification
auth_service = AuthService()