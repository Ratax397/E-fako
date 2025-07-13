#!/bin/bash

# Script de démarrage rapide pour la migration MySQL
# Usage: ./quick_start_mysql.sh

set -e  # Arrêter en cas d'erreur

echo "🚀 Démarrage rapide de la migration MySQL"
echo "=========================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "requirements.txt" ]; then
    print_error "Ce script doit être exécuté depuis le répertoire backend/"
    exit 1
fi

# Étape 1: Vérifier MySQL
print_status "Vérification de MySQL..."
if ! command -v mysql &> /dev/null; then
    print_error "MySQL n'est pas installé. Veuillez l'installer d'abord."
    echo "Instructions d'installation:"
    echo "  Ubuntu/Debian: sudo apt install mysql-server"
    echo "  CentOS/RHEL: sudo yum install mysql-server"
    echo "  macOS: brew install mysql"
    exit 1
fi

print_success "MySQL est installé"

# Étape 2: Vérifier Python et pip
print_status "Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 n'est pas installé"
    exit 1
fi

print_success "Python 3 est installé"

# Étape 3: Installer les dépendances
print_status "Installation des dépendances Python..."
if [ -f "fix_dependencies.py" ]; then
    print_status "Utilisation du script de dépannage des dépendances..."
    python3 fix_dependencies.py
else
    print_status "Installation standard des dépendances..."
    python3 -m pip install --upgrade pip
    pip3 install -r requirements.txt
fi
print_success "Dépendances installées"

# Étape 4: Configuration complète de la base de données
print_status "Configuration complète de la base de données MySQL..."
python3 create_database.py
print_success "Base de données configurée et tables créées"

# Étape 5: Test de la connexion
print_status "Test de la connexion à la base de données..."
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from app.core.database import test_db_connection
import asyncio
result = asyncio.run(test_db_connection())
if result:
    print('✅ Connexion réussie!')
else:
    print('❌ Échec de connexion')
    exit(1)
"

# Étape 6: Vérification finale
print_status "Vérification finale..."
if [ -f ".env" ]; then
    print_success "Fichier .env créé"
else
    print_warning "Fichier .env non trouvé"
fi

# Test des imports critiques
print_status "Test des imports critiques..."
python3 -c "
try:
    import fastapi, sqlalchemy, pymysql, cryptography, dotenv
    from app.core.database import Base, engine
    from app.models import user, waste, notification
    print('✅ Tous les imports critiques fonctionnent')
except Exception as e:
    print(f'❌ Erreur d\'import: {e}')
    exit(1)
"

# Résumé final
echo ""
echo "🎉 Migration MySQL terminée avec succès!"
echo "========================================"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Démarrer l'API: python3 -m uvicorn app.main:app --reload"
echo "2. Accéder à l'API: http://localhost:8000"
echo "3. Documentation: http://localhost:8000/api/v1/docs"
echo "4. Tester le frontend: cd .. && npm run dev"
echo ""
echo "📊 Informations de connexion:"
echo "   Base de données: waste_management"
echo "   Utilisateur: waste_user"
echo "   Mot de passe: waste_password_2024"
echo "   Hôte: localhost:3306"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Connexion MySQL: mysql -u waste_user -p waste_management"
echo "   - Lister les tables: SHOW TABLES;"
echo "   - Voir la structure: DESCRIBE users;"
echo "   - Test de connexion: python3 -c \"from app.core.database import test_db_connection; import asyncio; print(asyncio.run(test_db_connection()))\""
echo ""

print_success "Migration terminée! Vous pouvez maintenant démarrer votre application."