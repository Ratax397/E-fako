#!/bin/bash

# Script de démarrage complet pour le projet Waste Management
# Démarre automatiquement le backend MySQL et le frontend Electron

set -e

echo "🚀 Démarrage du projet Waste Management (Backend MySQL + Frontend Electron)"
echo "=" * 80

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Fonction pour vérifier si un port est occupé
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Fonction pour démarrer le backend
start_backend() {
    print_status "Démarrage du backend MySQL..."
    
    cd backend
    
    # Vérifier que le fichier .env existe
    if [ ! -f ".env" ]; then
        print_warning "Fichier .env non trouvé. Configuration automatique..."
        python create_database.py
    fi
    
    # Vérifier la connexion MySQL
    print_status "Test de la connexion MySQL..."
    if ! python -c "from app.core.database import test_db_connection; import asyncio; exit(0 if asyncio.run(test_db_connection()) else 1)" 2>/dev/null; then
        print_error "Connexion MySQL échouée. Lancement de la configuration..."
        python create_database.py
    fi
    
    # Démarrer l'API FastAPI
    print_status "Lancement de l'API FastAPI sur http://localhost:8000..."
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Attendre que l'API soit prête
    print_status "Attente du démarrage de l'API..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "API démarrée avec succès!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Timeout: L'API n'a pas pu démarrer"
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
    done
    
    cd ..
}

# Fonction pour démarrer le frontend
start_frontend() {
    print_status "Démarrage du frontend Electron..."
    
    # Vérifier que les dépendances sont installées
    if [ ! -d "node_modules" ]; then
        print_status "Installation des dépendances Node.js..."
        npm install
    fi
    
    # Démarrer l'application Electron
    print_status "Lancement de l'application Electron..."
    npm run dev &
    FRONTEND_PID=$!
    
    print_success "Application Electron démarrée!"
}

# Fonction de nettoyage
cleanup() {
    print_status "Arrêt des processus..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend arrêté"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend arrêté"
    fi
    exit 0
}

# Gérer l'arrêt propre
trap cleanup SIGINT SIGTERM

# Vérifications préliminaires
print_status "Vérifications préliminaires..."

# Vérifier Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js n'est pas installé"
    exit 1
fi

# Vérifier MySQL
if ! command -v mysql &> /dev/null; then
    print_error "MySQL n'est pas installé"
    exit 1
fi

print_success "Toutes les dépendances sont installées"

# Vérifier si les ports sont libres
if check_port 8000; then
    print_warning "Le port 8000 est déjà occupé. Arrêt du processus existant..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Démarrer les services
start_backend
start_frontend

# Afficher les informations
echo ""
echo "🎉 Projet démarré avec succès!"
echo "=" * 50
echo ""
echo "📊 Services disponibles:"
echo "  🔗 API Backend:          http://localhost:8000"
echo "  📚 Documentation API:    http://localhost:8000/api/v1/docs"
echo "  💻 Application Electron: Fenêtre ouverte automatiquement"
echo ""
echo "🔧 Test rapide:"
echo "  curl http://localhost:8000/health"
echo ""
echo "⚠️  Pour arrêter le projet: Ctrl+C"
echo ""

# Attendre indéfiniment
print_status "Projet en cours d'exécution. Appuyez sur Ctrl+C pour arrêter."
wait