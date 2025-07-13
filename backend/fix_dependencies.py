#!/usr/bin/env python3
"""
Script de dépannage pour résoudre les problèmes de dépendances.
"""

import subprocess
import sys
import platform

def run_command(command, description):
    """Exécuter une commande avec gestion d'erreurs."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur: {e}")
        return False, e.stderr

def fix_cryptography():
    """Résoudre les problèmes de cryptography."""
    print("\n🔧 Résolution des problèmes de cryptography...")
    
    # Désinstaller et réinstaller cryptography
    run_command("pip uninstall cryptography -y", "Désinstallation de cryptography")
    
    # Installer les dépendances système selon l'OS
    system = platform.system().lower()
    
    if system == "linux":
        print("📦 Installation des dépendances système Linux...")
        run_command("sudo apt-get update", "Mise à jour des paquets")
        run_command("sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev", "Installation des dépendances de compilation")
    elif system == "darwin":  # macOS
        print("📦 Installation des dépendances système macOS...")
        run_command("brew install openssl libffi", "Installation via Homebrew")
    elif system == "windows":
        print("📦 Windows détecté - utilisation de la version précompilée...")
    
    # Réinstaller cryptography
    success, _ = run_command("pip install cryptography==41.0.8", "Réinstallation de cryptography")
    
    if not success:
        print("⚠️ Tentative avec une version plus récente...")
        run_command("pip install cryptography", "Installation de la dernière version de cryptography")

def fix_mysqlclient():
    """Résoudre les problèmes de mysqlclient."""
    print("\n🔧 Résolution des problèmes de mysqlclient...")
    
    system = platform.system().lower()
    
    if system == "linux":
        print("📦 Installation des dépendances MySQL Linux...")
        run_command("sudo apt-get install -y default-libmysqlclient-dev build-essential", "Dépendances MySQL Linux")
    elif system == "darwin":  # macOS
        print("📦 Installation des dépendances MySQL macOS...")
        run_command("brew install mysql-client", "Installation MySQL client via Homebrew")
    elif system == "windows":
        print("📦 Windows détecté - utilisation de l'alternative...")
        run_command("pip install mysql-connector-python==8.2.0", "Installation de mysql-connector-python")
        return
    
    # Tentative d'installation de mysqlclient
    success, _ = run_command("pip install mysqlclient==2.2.0", "Installation de mysqlclient")
    
    if not success:
        print("⚠️ mysqlclient échoué, utilisation de l'alternative...")
        run_command("pip install mysql-connector-python==8.2.0", "Installation de mysql-connector-python")

def fix_face_recognition():
    """Résoudre les problèmes de face-recognition."""
    print("\n🔧 Résolution des problèmes de face-recognition...")
    
    system = platform.system().lower()
    
    if system == "linux":
        print("📦 Installation des dépendances face-recognition Linux...")
        run_command("sudo apt-get install -y cmake", "Installation de cmake")
        run_command("sudo apt-get install -y libopenblas-dev liblapack-dev", "Dépendances BLAS/LAPACK")
    elif system == "darwin":  # macOS
        print("📦 Installation des dépendances face-recognition macOS...")
        run_command("brew install cmake", "Installation de cmake via Homebrew")
    elif system == "windows":
        print("📦 Windows détecté - installation des dépendances...")
        run_command("pip install cmake", "Installation de cmake via pip")
    
    # Installation de dlib d'abord
    print("🔧 Installation de dlib...")
    success, _ = run_command("pip install dlib==19.24.2", "Installation de dlib")
    
    if success:
        run_command("pip install face-recognition==1.3.0", "Installation de face-recognition")
    else:
        print("⚠️ dlib échoué - face-recognition sera ignoré")

def fix_opencv():
    """Résoudre les problèmes d'OpenCV."""
    print("\n🔧 Résolution des problèmes d'OpenCV...")
    
    # Désinstaller les versions conflictuelles
    run_command("pip uninstall opencv-python opencv-contrib-python -y", "Nettoyage des versions OpenCV")
    
    # Réinstaller la version stable
    run_command("pip install opencv-python==4.8.1.78", "Installation d'OpenCV")

def remove_python_cors():
    """Supprimer python-cors qui n'existe pas."""
    print("\n🔧 Suppression de python-cors (package inexistant)...")
    run_command("pip uninstall python-cors -y", "Suppression de python-cors")

def main():
    """Fonction principale de dépannage."""
    print("🛠️ Script de dépannage des dépendances")
    print("=" * 45)
    
    print(f"🖥️ Système détecté: {platform.system()} {platform.release()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Mise à jour de pip
    run_command("python -m pip install --upgrade pip", "Mise à jour de pip")
    
    # Résolution des problèmes courants
    remove_python_cors()
    fix_cryptography()
    fix_mysqlclient()
    fix_opencv()
    fix_face_recognition()
    
    # Installation des dépendances essentielles
    print("\n📦 Installation des dépendances essentielles...")
    essential_packages = [
        "python-dotenv==1.0.0",
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "sqlalchemy==2.0.23",
        "pymysql==1.1.0",
        "aiomysql==0.2.0",
        "alembic==1.13.1",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "python-multipart==0.0.6",
        "python-socketio==5.11.0",
        "python-engineio==4.7.1",
        "requests==2.31.0",
        "email-validator==2.1.0",
        "python-dateutil==2.8.2",
        "structlog==23.2.0",
        "numpy==1.24.3",
        "Pillow==10.1.0",
    ]
    
    for package in essential_packages:
        run_command(f"pip install {package}", f"Installation de {package}")
    
    # Vérification finale
    print("\n🧪 Vérification des installations...")
    test_imports = [
        "fastapi",
        "sqlalchemy",
        "pymysql",
        "cryptography",
        "dotenv",
        "pydantic",
        "uvicorn",
        "alembic",
        "numpy",
        "PIL",
    ]
    
    failed = []
    for module in test_imports:
        try:
            __import__(module)
            print(f"✅ {module} OK")
        except ImportError:
            print(f"❌ {module} manquant")
            failed.append(module)
    
    # Résumé
    print("\n" + "=" * 45)
    if not failed:
        print("🎉 Toutes les dépendances essentielles sont installées!")
        print("\n📋 Prochaines étapes:")
        print("1. Configurer MySQL: python setup_mysql.py")
        print("2. Créer les migrations: python create_initial_migration.py")
        print("3. Démarrer l'API: python -m uvicorn app.main:app --reload")
    else:
        print(f"⚠️ Dépendances manquantes: {', '.join(failed)}")
        print("\n🔧 Solutions possibles:")
        print("- Réexécuter ce script")
        print("- Installer manuellement les dépendances manquantes")
        print("- Utiliser un environnement virtuel")
        print("- Vérifier la compatibilité de votre système")

if __name__ == "__main__":
    main()