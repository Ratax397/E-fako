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
pip3 install -r requirements.txt
print_success "Dépendances installées"

# Étape 4: Configuration de la base de données
print_status "Configuration de la base de données MySQL..."
python3 setup_mysql.py
print_success "Base de données configurée"

# Étape 5: Création des migrations
print_status "Création des migrations de base de données..."
python3 create_initial_migration.py
print_success "Migrations créées"

# Étape 6: Application des migrations
print_status "Application des migrations..."
alembic upgrade head
print_success "Migrations appliquées"

# Étape 7: Test de la connexion
print_status "Test de la connexion à la base de données..."
python3 -c "
from app.core.database import test_db_connection
import asyncio
result = asyncio.run(test_db_connection())
if result:
    print('✅ Connexion réussie!')
else:
    print('❌ Échec de connexion')
    exit(1)
"

# Étape 8: Vérification finale
print_status "Vérification finale..."
if [ -f ".env" ]; then
    print_success "Fichier .env créé"
else
    print_warning "Fichier .env non trouvé"
fi

# Résumé final
echo ""
echo "🎉 Migration MySQL terminée avec succès!"
echo "========================================"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Démarrer l'API: python3 -m uvicorn app.main:app --reload"
echo "2. Accéder à l'API: http://localhost:8000"
echo "3. Documentation: http://localhost:8000/api/v1/docs"
echo ""
echo "📊 Informations de connexion:"
echo "   Base de données: waste_management"
echo "   Utilisateur: waste_user"
echo "   Hôte: localhost:3306"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Vérifier le statut: alembic current"
echo "   - Voir l'historique: alembic history"
echo "   - Tester la connexion: mysql -u waste_user -p waste_management"
echo ""

print_success "Migration terminée! Vous pouvez maintenant démarrer votre application."