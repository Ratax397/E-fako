#!/usr/bin/env python3
"""
Script pour créer automatiquement la base de données MySQL avec toutes les tables.
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path Python
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

def create_database():
    """Créer la base de données MySQL."""
    print("🚀 Création de la base de données MySQL")
    print("=" * 40)
    
    # Configuration par défaut
    DB_NAME = "waste_management"
    DB_USER = "waste_user"
    DB_PASSWORD = "waste_password_2024"
    DB_HOST = "localhost"
    DB_PORT = 3306
    
    try:
        # Connexion root pour créer la base
        print("🔐 Connexion à MySQL en tant que root...")
        root_password = input("Entrez le mot de passe root MySQL (ou appuyez sur Entrée si aucun): ").strip()
        
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user="root",
            password=root_password if root_password else None
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Créer la base de données
            print(f"📊 Création de la base de données '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # Créer l'utilisateur
            print(f"👤 Création de l'utilisateur '{DB_USER}'...")
            cursor.execute(f"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASSWORD}'")
            
            # Accorder les privilèges
            print("🔑 Attribution des privilèges...")
            cursor.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            
            print("✅ Base de données et utilisateur créés avec succès!")
            
            # Fermer la connexion root
            cursor.close()
            connection.close()
            
            return True
            
    except Error as e:
        print(f"❌ Erreur lors de la création de la base de données: {e}")
        return False

def create_tables():
    """Créer toutes les tables avec SQLAlchemy."""
    print("\n🏗️ Création des tables...")
    
    try:
        # Importer les modèles et la base
        from app.core.database import Base, engine
        from app.models import user, waste, notification
        
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        print("✅ Toutes les tables créées avec succès!")
        
        # Lister les tables créées
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Tables créées ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return False

def test_connection():
    """Tester la connexion à la base de données."""
    print("\n🧪 Test de connexion...")
    
    try:
        from app.core.database import test_db_connection
        import asyncio
        
        result = asyncio.run(test_db_connection())
        
        if result:
            print("✅ Connexion à la base de données réussie!")
            return True
        else:
            print("❌ Échec de la connexion à la base de données")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de connexion: {e}")
        return False

def create_env_file():
    """Créer le fichier .env s'il n'existe pas."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ Fichier .env existant trouvé")
        return True
    
    print("📝 Création du fichier .env...")
    
    env_content = """# Configuration de la base de données MySQL
DATABASE_URL=mysql+pymysql://waste_user:waste_password_2024@localhost:3306/waste_management
DATABASE_URL_ASYNC=mysql+aiomysql://waste_user:waste_password_2024@localhost:3306/waste_management

# JWT et sécurité
JWT_SECRET_KEY=WasteManagement2024_JWT_LocalKey_SecureToken_32Chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Chiffrement biométrique
BIOMETRIC_ENCRYPTION_KEY=BiometricAuth_LocalEncryption_WasteApp_2024_Key

# Redis (optionnel pour le développement local)
REDIS_URL=redis://localhost:6379/0

# Socket.IO
SOCKETIO_SECRET_KEY=WasteApp_SocketIO_LocalSecret_2024_SecureKey_Here

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
    
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ Fichier .env créé avec succès!")
    return True

def main():
    """Fonction principale."""
    print("🚀 Configuration complète de la base de données MySQL")
    print("=" * 55)
    
    # Vérifier si MySQL est installé
    try:
        import mysql.connector
        print("✅ MySQL connector disponible")
    except ImportError:
        print("❌ MySQL connector non trouvé")
        print("Installez-le avec: pip install mysql-connector-python")
        sys.exit(1)
    
    # Créer le fichier .env
    if not create_env_file():
        print("❌ Échec de la création du fichier .env")
        sys.exit(1)
    
    # Recharger les variables d'environnement
    load_dotenv()
    
    # Créer la base de données
    if not create_database():
        print("❌ Échec de la création de la base de données")
        sys.exit(1)
    
    # Créer les tables
    if not create_tables():
        print("❌ Échec de la création des tables")
        sys.exit(1)
    
    # Tester la connexion
    if not test_connection():
        print("❌ Échec du test de connexion")
        sys.exit(1)
    
    # Résumé final
    print("\n" + "=" * 55)
    print("🎉 Configuration terminée avec succès!")
    print("=" * 55)
    print(f"📊 Base de données: waste_management")
    print(f"👤 Utilisateur: waste_user")
    print(f"🔑 Mot de passe: waste_password_2024")
    print(f"🌐 Hôte: localhost:3306")
    print(f"📝 Fichier .env: Créé et configuré")
    print(f"🏗️ Tables: Créées et prêtes")
    
    print("\n📋 Prochaines étapes:")
    print("1. Démarrer l'API: python -m uvicorn app.main:app --reload")
    print("2. Accéder à l'API: http://localhost:8000")
    print("3. Documentation: http://localhost:8000/api/v1/docs")
    print("4. Tester le frontend: cd .. && npm run dev")
    
    print("\n🔧 Commandes utiles:")
    print("- Connexion MySQL: mysql -u waste_user -p waste_management")
    print("- Lister les tables: SHOW TABLES;")
    print("- Voir la structure: DESCRIBE users;")
    
    print("\n✅ Votre backend MySQL est prêt à fonctionner!")

if __name__ == "__main__":
    main()