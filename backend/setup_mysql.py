#!/usr/bin/env python3
"""
Script de configuration de la base de données MySQL pour l'application de gestion des déchets.
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from pathlib import Path

# Configuration par défaut
DEFAULT_DB_NAME = "waste_management"
DEFAULT_DB_USER = "waste_user"
DEFAULT_DB_PASSWORD = "waste_password_2024"
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 3306


def create_database_and_user():
    """Créer la base de données et l'utilisateur MySQL."""
    
    # Connexion root (doit exister)
    try:
        connection = mysql.connector.connect(
            host=DEFAULT_DB_HOST,
            port=DEFAULT_DB_PORT,
            user="root",
            password=input("Entrez le mot de passe root MySQL (laissez vide si aucun): ").strip() or None
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Créer la base de données
            print(f"Création de la base de données '{DEFAULT_DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DEFAULT_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # Créer l'utilisateur
            print(f"Création de l'utilisateur '{DEFAULT_DB_USER}'...")
            cursor.execute(f"CREATE USER IF NOT EXISTS '{DEFAULT_DB_USER}'@'localhost' IDENTIFIED BY '{DEFAULT_DB_PASSWORD}'")
            
            # Accorder les privilèges
            print("Attribution des privilèges...")
            cursor.execute(f"GRANT ALL PRIVILEGES ON {DEFAULT_DB_NAME}.* TO '{DEFAULT_DB_USER}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            
            print("✅ Base de données et utilisateur créés avec succès!")
            
            # Tester la connexion avec le nouvel utilisateur
            test_connection()
            
    except Error as e:
        print(f"❌ Erreur lors de la création de la base de données: {e}")
        sys.exit(1)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def test_connection():
    """Tester la connexion avec le nouvel utilisateur."""
    try:
        connection = mysql.connector.connect(
            host=DEFAULT_DB_HOST,
            port=DEFAULT_DB_PORT,
            user=DEFAULT_DB_USER,
            password=DEFAULT_DB_PASSWORD,
            database=DEFAULT_DB_NAME
        )
        
        if connection.is_connected():
            print("✅ Connexion testée avec succès!")
            connection.close()
        else:
            print("❌ Échec de la connexion de test")
            
    except Error as e:
        print(f"❌ Erreur lors du test de connexion: {e}")


def create_env_file():
    """Créer le fichier .env avec les variables d'environnement."""
    env_content = f"""# Configuration de la base de données MySQL
DATABASE_URL=mysql+pymysql://{DEFAULT_DB_USER}:{DEFAULT_DB_PASSWORD}@{DEFAULT_DB_HOST}:{DEFAULT_DB_PORT}/{DEFAULT_DB_NAME}
DATABASE_URL_ASYNC=mysql+aiomysql://{DEFAULT_DB_USER}:{DEFAULT_DB_PASSWORD}@{DEFAULT_DB_HOST}:{DEFAULT_DB_PORT}/{DEFAULT_DB_NAME}

# JWT et sécurité
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Chiffrement biométrique
BIOMETRIC_ENCRYPTION_KEY=your-biometric-encryption-key-change-this

# Redis (optionnel pour le développement local)
REDIS_URL=redis://localhost:6379/0

# Socket.IO
SOCKETIO_SECRET_KEY=your-socketio-secret-key

# Notifications push (optionnel)
FCM_SERVER_KEY=your-fcm-server-key
FCM_SENDER_ID=your-fcm-sender-id

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# Celery (optionnel pour le développement local)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Configuration de l'application
DEBUG=true
LOG_LEVEL=INFO
"""
    
    env_file = Path(__file__).parent / ".env"
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"✅ Fichier .env créé: {env_file}")


def main():
    """Fonction principale."""
    print("🚀 Configuration de la base de données MySQL pour Waste Management")
    print("=" * 60)
    
    # Vérifier si MySQL est installé
    try:
        import mysql.connector
        print("✅ Module mysql-connector-python disponible")
    except ImportError:
        print("❌ Module mysql-connector-python non trouvé")
        print("Installez-le avec: pip install mysql-connector-python")
        sys.exit(1)
    
    # Créer la base de données et l'utilisateur
    create_database_and_user()
    
    # Créer le fichier .env
    create_env_file()
    
    print("\n" + "=" * 60)
    print("✅ Configuration terminée!")
    print(f"📊 Base de données: {DEFAULT_DB_NAME}")
    print(f"👤 Utilisateur: {DEFAULT_DB_USER}")
    print(f"🔑 Mot de passe: {DEFAULT_DB_PASSWORD}")
    print(f"🌐 Hôte: {DEFAULT_DB_HOST}:{DEFAULT_DB_PORT}")
    print("\n📝 Prochaines étapes:")
    print("1. Installez les dépendances: pip install -r requirements.txt")
    print("2. Lancez l'application: python -m uvicorn app.main:app --reload")
    print("3. Accédez à l'API: http://localhost:8000")


if __name__ == "__main__":
    main()