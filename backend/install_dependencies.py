#!/usr/bin/env python3
"""
Script d'installation intelligent des dépendances pour éviter les conflits.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description, ignore_errors=False):
    """Exécuter une commande avec gestion d'erreurs."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            print(f"⚠️ {description} - Ignoré: {e}")
            return False, e.stderr
        else:
            print(f"❌ {description} - Erreur: {e}")
            print(f"Sortie d'erreur: {e.stderr}")
            return False, e.stderr

def install_package(package, description="", alternative=None):
    """Installer un package avec gestion d'alternative."""
    success, output = run_command(f"pip install {package}", f"Installation de {package}")
    
    if not success and alternative:
        print(f"⚠️ Tentative avec l'alternative: {alternative}")
        success, output = run_command(f"pip install {alternative}", f"Installation alternative de {alternative}")
    
    return success

def main():
    """Installation intelligente des dépendances."""
    print("🚀 Installation intelligente des dépendances MySQL")
    print("=" * 55)
    
    # Mise à jour de pip
    run_command("python -m pip install --upgrade pip", "Mise à jour de pip")
    
    # Dépendances essentielles en premier
    essential_packages = [
        ("python-dotenv==1.0.0", "Variables d'environnement"),
        ("fastapi==0.104.1", "Framework FastAPI"),
        ("uvicorn[standard]==0.24.0", "Serveur ASGI"),
        ("pydantic==2.5.0", "Validation des données"),
        ("pydantic-settings==2.1.0", "Configuration Pydantic"),
        ("sqlalchemy==2.0.23", "ORM SQLAlchemy"),
        ("alembic==1.13.1", "Migrations de base de données"),
    ]
    
    print("\n📦 Installation des dépendances essentielles...")
    for package, desc in essential_packages:
        install_package(package, desc)
    
    # Dépendances MySQL avec alternatives
    print("\n🗄️ Installation des connecteurs MySQL...")
    mysql_packages = [
        ("pymysql==1.1.0", "Connecteur MySQL Python pur"),
        ("aiomysql==0.2.0", "Connecteur MySQL asynchrone"),
    ]
    
    for package, desc in mysql_packages:
        install_package(package, desc)
    
    # mysqlclient avec alternative
    print("\n🔧 Installation de mysqlclient (avec alternative)...")
    mysqlclient_success = install_package(
        "mysqlclient==2.2.0", 
        "Connecteur MySQL C", 
        "mysql-connector-python==8.2.0"
    )
    
    if not mysqlclient_success:
        print("⚠️ mysqlclient échoué, utilisation de mysql-connector-python")
    
    # Sécurité et authentification
    print("\n🔐 Installation des dépendances de sécurité...")
    security_packages = [
        ("cryptography==41.0.8", "Cryptographie"),
        ("python-jose[cryptography]==3.3.0", "JWT avec cryptographie"),
        ("passlib[bcrypt]==1.7.4", "Hachage de mots de passe"),
        ("python-multipart==0.0.6", "Support multipart"),
    ]
    
    for package, desc in security_packages:
        install_package(package, desc)
    
    # Reconnaissance faciale (optionnel)
    print("\n👁️ Installation des dépendances de reconnaissance faciale...")
    face_packages = [
        ("numpy==1.24.3", "Calculs numériques"),
        ("Pillow==10.1.0", "Traitement d'images"),
        ("opencv-python==4.8.1.78", "Vision par ordinateur"),
    ]
    
    for package, desc in face_packages:
        success = install_package(package, desc)
        if not success and "opencv" in package:
            print("⚠️ OpenCV peut nécessiter des dépendances système supplémentaires")
    
    # Face recognition (peut échouer sur certains systèmes)
    print("\n🔍 Installation de face-recognition (optionnel)...")
    face_recognition_success = install_package(
        "face-recognition==1.3.0", 
        "Reconnaissance faciale (optionnel)"
    )
    
    if not face_recognition_success:
        print("⚠️ face-recognition échoué - vous pouvez continuer sans cette fonctionnalité")
    
    # Socket.IO et temps réel
    print("\n⚡ Installation des dépendances temps réel...")
    realtime_packages = [
        ("python-socketio==5.11.0", "Socket.IO serveur"),
        ("python-engineio==4.7.1", "Engine.IO"),
    ]
    
    for package, desc in realtime_packages:
        install_package(package, desc)
    
    # Autres dépendances
    print("\n📚 Installation des autres dépendances...")
    other_packages = [
        ("requests==2.31.0", "Requêtes HTTP"),
        ("email-validator==2.1.0", "Validation email"),
        ("python-dateutil==2.8.2", "Utilitaires de date"),
        ("structlog==23.2.0", "Logging structuré"),
    ]
    
    for package, desc in other_packages:
        install_package(package, desc)
    
    # Dépendances optionnelles
    print("\n🔧 Installation des dépendances optionnelles...")
    optional_packages = [
        ("pytest==7.4.3", "Tests (optionnel)"),
        ("httpx==0.25.2", "Client HTTP async (optionnel)"),
        ("pyfcm==1.5.4", "Notifications push (optionnel)"),
        ("redis==5.0.1", "Cache Redis (optionnel)"),
        ("celery==5.3.4", "Tâches asynchrones (optionnel)"),
    ]
    
    for package, desc in optional_packages:
        install_package(package, desc)
    
    # Vérification finale
    print("\n🧪 Vérification des installations critiques...")
    critical_imports = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pymysql", "PyMySQL"),
        ("cryptography", "Cryptographie"),
        ("dotenv", "Python-dotenv"),
    ]
    
    failed_imports = []
    for module, name in critical_imports:
        try:
            __import__(module)
            print(f"✅ {name} importé avec succès")
        except ImportError:
            print(f"❌ {name} non disponible")
            failed_imports.append(name)
    
    # Résumé final
    print("\n" + "=" * 55)
    if not failed_imports:
        print("🎉 Installation terminée avec succès!")
        print("✅ Toutes les dépendances critiques sont installées")
        print("\n📋 Prochaines étapes:")
        print("1. Configurer MySQL: python setup_mysql.py")
        print("2. Créer les migrations: python create_initial_migration.py")
        print("3. Appliquer les migrations: alembic upgrade head")
        print("4. Démarrer l'API: python -m uvicorn app.main:app --reload")
    else:
        print("⚠️ Installation terminée avec des avertissements")
        print(f"❌ Dépendances manquantes: {', '.join(failed_imports)}")
        print("\n🔧 Solutions possibles:")
        print("- Réexécuter le script")
        print("- Installer manuellement les dépendances manquantes")
        print("- Vérifier la compatibilité Python 3.10")
    
    print("\n💡 En cas de problème:")
    print("- Vérifiez que Python 3.10 est installé")
    print("- Mettez à jour pip: python -m pip install --upgrade pip")
    print("- Utilisez un environnement virtuel")

if __name__ == "__main__":
    main()