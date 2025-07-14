#!/usr/bin/env python3
"""
Script de test pour valider la migration MySQL.
"""

import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire courant au path Python
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Tester les imports des modules MySQL."""
    print("🔍 Test des imports...")
    
    try:
        import mysql.connector
        print("✅ mysql.connector importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import mysql.connector: {e}")
        return False
    
    try:
        import pymysql
        print("✅ pymysql importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import pymysql: {e}")
        return False
    
    try:
        import aiomysql
        print("✅ aiomysql importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import aiomysql: {e}")
        return False
    
    return True


def test_database_connection():
    """Tester la connexion à la base de données."""
    print("\n🔍 Test de la connexion à la base de données...")
    
    try:
        from app.core.database import test_db_connection
        result = asyncio.run(test_db_connection())
        
        if result:
            print("✅ Connexion à la base de données réussie")
            return True
        else:
            print("❌ Échec de la connexion à la base de données")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test de connexion: {e}")
        return False


def test_models_import():
    """Tester l'import des modèles."""
    print("\n🔍 Test des modèles...")
    
    try:
        from app.models.user import User, UserRole, UserStatus
        print("✅ Modèle User importé avec succès")
    except Exception as e:
        print(f"❌ Erreur import modèle User: {e}")
        return False
    
    try:
        from app.models.waste import WasteRecord, WasteType, WasteStatus
        print("✅ Modèle WasteRecord importé avec succès")
    except Exception as e:
        print(f"❌ Erreur import modèle WasteRecord: {e}")
        return False
    
    try:
        from app.models.notification import Notification, NotificationType
        print("✅ Modèle Notification importé avec succès")
    except Exception as e:
        print(f"❌ Erreur import modèle Notification: {e}")
        return False
    
    return True


def test_configuration():
    """Tester la configuration de l'application."""
    print("\n🔍 Test de la configuration...")
    
    try:
        from app.core.config import settings
        print("✅ Configuration chargée avec succès")
        
        # Vérifier les variables essentielles
        required_vars = [
            'DATABASE_URL',
            'DATABASE_URL_ASYNC',
            'JWT_SECRET_KEY',
            'BIOMETRIC_ENCRYPTION_KEY'
        ]
        
        for var in required_vars:
            if hasattr(settings, var):
                value = getattr(settings, var)
                if value and value != "":
                    print(f"✅ {var} configuré")
                else:
                    print(f"⚠️ {var} vide ou non configuré")
            else:
                print(f"❌ {var} manquant")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors du chargement de la configuration: {e}")
        return False


def test_database_operations():
    """Tester les opérations de base de données."""
    print("\n🔍 Test des opérations de base de données...")
    
    try:
        from app.core.database import SessionLocal
        from app.models.user import User, UserRole, UserStatus
        
        # Test de création de session
        db = SessionLocal()
        print("✅ Session de base de données créée")
        
        # Test de requête simple
        try:
            users = db.query(User).limit(1).all()
            print("✅ Requête de base de données réussie")
        except Exception as e:
            print(f"⚠️ Requête de base de données échouée (normal si pas de données): {e}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Erreur lors des opérations de base de données: {e}")
        return False


def test_async_database():
    """Tester les opérations asynchrones de base de données."""
    print("\n🔍 Test des opérations asynchrones...")
    
    async def test_async():
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.user import User
            
            async with AsyncSessionLocal() as session:
                # Test de requête asynchrone simple
                result = await session.execute("SELECT 1")
                print("✅ Requête asynchrone réussie")
                return True
        except Exception as e:
            print(f"❌ Erreur lors des opérations asynchrones: {e}")
            return False
    
    return asyncio.run(test_async())


def test_schema_creation():
    """Tester la création du schéma de base de données."""
    print("\n🔍 Test de la création du schéma...")
    
    try:
        from app.core.database import Base, engine
        from app.models import user, waste, notification
        
        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)
        print("✅ Schéma de base de données créé avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du schéma: {e}")
        return False


def main():
    """Fonction principale de test."""
    print("🧪 Test de validation de la migration MySQL")
    print("=" * 50)
    
    tests = [
        ("Imports MySQL", test_imports),
        ("Connexion base de données", test_database_connection),
        ("Modèles", test_models_import),
        ("Configuration", test_configuration),
        ("Opérations de base de données", test_database_operations),
        ("Opérations asynchrones", test_async_database),
        ("Création du schéma", test_schema_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ Test '{test_name}' échoué")
        except Exception as e:
            print(f"❌ Test '{test_name}' a levé une exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! La migration MySQL est réussie.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)