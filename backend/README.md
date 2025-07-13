# Backend FastAPI - Gestion des Déchets

## Vue d'ensemble

Backend Python complet avec FastAPI pour une application de gestion de déchets avec interface Electron.js. Le système inclut une authentification par reconnaissance faciale, une base de données PostgreSQL temps réel, des APIs REST complètes, Socket.IO pour les mises à jour en temps réel, et un système de notifications push.

## Fonctionnalités

### 🔐 Authentification Avancée
- **Reconnaissance faciale** : Inscription et connexion par reconnaissance faciale
- **JWT sécurisé** : Tokens d'accès et de rafraîchissement
- **Chiffrement biométrique** : Données faciales chiffrées avec Fernet
- **Gestion des rôles** : User, Admin, Super Admin
- **Sécurité avancée** : Limitation des tentatives, blacklist des tokens

### 📊 Gestion des Déchets
- **CRUD complet** : Création, lecture, mise à jour, suppression
- **Types de déchets** : Organic, Plastic, Paper, Glass, Metal, Electronic, Hazardous, Textile
- **Traçabilité complète** : Statuts de PENDING à RECYCLED/DISPOSED
- **Géolocalisation** : Support des coordonnées GPS
- **Upload d'images** : Support des images Base64
- **Scoring environnemental** : Calcul automatique des scores et points
- **Validation admin** : Système de validation par les administrateurs

### 👥 Gestion des Utilisateurs
- **Profils complets** : Informations personnelles et préférences
- **Statistiques utilisateur** : Suivi des activités et contributions
- **Activation/Désactivation** : Contrôle admin des comptes
- **Préférences de notification** : Paramètres personnalisables

### 🔔 Système de Notifications
- **Notifications push** : FCM (Firebase Cloud Messaging)
- **Notifications en temps réel** : Socket.IO
- **Types de notifications** : System, Waste Update, Collection Reminder, Achievement, etc.
- **Priorités** : Low, Medium, High, Urgent
- **Templates** : Modèles de notifications réutilisables
- **Gestion des appareils** : Support multi-appareils
- **Retry automatique** : Système de tentatives en cas d'échec

### 📈 Statistiques et Dashboard
- **Dashboard admin** : Vue d'ensemble complète
- **Statistiques temps réel** : Utilisateurs connectés, activités
- **Tendances** : Analyses temporelles et graphiques
- **Métriques détaillées** : KPIs de performance
- **Exports de données** : Formats multiples

### 🌐 Socket.IO Temps Réel
- **Connexions authentifiées** : Sécurisation par JWT
- **Rooms par rôle** : Séparation admin/utilisateur
- **Mises à jour live** : Dashboard et notifications
- **Gestion des déconnexions** : Nettoyage automatique

## Architecture Technique

### Structure du Projet
```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dépendances FastAPI
│   │   └── v1/
│   │       ├── __init__.py      # Router principal
│   │       └── endpoints/
│   │           ├── auth.py      # Authentification
│   │           ├── users.py     # Gestion utilisateurs
│   │           ├── waste.py     # Gestion déchets
│   │           ├── statistics.py # Statistiques
│   │           └── notifications.py # Notifications
│   ├── core/
│   │   ├── config.py           # Configuration Pydantic
│   │   ├── database.py         # SQLAlchemy async
│   │   ├── exceptions.py       # Exceptions personnalisées
│   │   └── logging.py          # Logging structuré
│   ├── models/
│   │   ├── user.py             # Modèles utilisateur
│   │   ├── waste.py            # Modèles déchets
│   │   └── notification.py     # Modèles notifications
│   ├── schemas/
│   │   ├── user.py             # Schémas Pydantic utilisateur
│   │   ├── waste.py            # Schémas Pydantic déchets
│   │   └── notification.py     # Schémas Pydantic notifications
│   ├── services/
│   │   ├── auth_service.py     # Service authentification
│   │   ├── notification_service.py # Service notifications
│   │   └── socketio_service.py # Service Socket.IO
│   └── main.py                 # Application FastAPI
├── requirements.txt            # Dépendances Python
├── .env.example               # Variables d'environnement
└── README.md                  # Documentation
```

### Technologies Utilisées
- **FastAPI** : Framework web moderne et rapide
- **SQLAlchemy 2.0** : ORM avec support async
- **PostgreSQL** : Base de données principale
- **Redis** : Cache et sessions
- **Socket.IO** : Communication temps réel
- **Celery** : Tâches asynchrones
- **OpenCV & face-recognition** : Reconnaissance faciale
- **FCM** : Notifications push
- **Pydantic** : Validation des données
- **Structlog** : Logging structuré
- **Pytest** : Tests unitaires

## Installation et Configuration

### Prérequis
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- OpenCV dependencies

### Installation
```bash
cd backend
pip install -r requirements.txt
```

### Configuration
1. Copier `.env.example` vers `.env`
2. Configurer les variables d'environnement :
   - `DATABASE_URL` : Connexion PostgreSQL
   - `JWT_SECRET_KEY` : Clé JWT secrète
   - `BIOMETRIC_ENCRYPTION_KEY` : Clé de chiffrement biométrique
   - `FCM_SERVER_KEY` : Clé serveur Firebase
   - `REDIS_URL` : Connexion Redis

### Démarrage
```bash
# Développement
uvicorn app.main:socket_app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --workers 4
```

### Tâches Celery
```bash
# Worker Celery
celery -A app.services.notification_service.celery_app worker --loglevel=info

# Beat Celery (tâches périodiques)
celery -A app.services.notification_service.celery_app beat --loglevel=info
```

## API Documentation

### Endpoints Principaux

#### Authentification (`/api/v1/auth`)
- `POST /register` - Inscription utilisateur
- `POST /login` - Connexion par identifiants
- `POST /face-login` - Connexion par reconnaissance faciale
- `POST /face-register` - Enregistrement données faciales
- `POST /refresh` - Rafraîchissement token
- `GET /me` - Informations utilisateur actuel

#### Utilisateurs (`/api/v1/users`)
- `GET /` - Liste des utilisateurs (admin)
- `GET /me` - Profil utilisateur
- `PUT /me` - Mise à jour profil
- `POST /{user_id}/activate` - Activation compte (admin)
- `GET /statistics/overview` - Statistiques utilisateurs (admin)

#### Déchets (`/api/v1/waste`)
- `GET /` - Liste des enregistrements
- `POST /` - Créer un enregistrement
- `GET /{record_id}` - Détails d'un enregistrement
- `PUT /{record_id}` - Mise à jour
- `DELETE /{record_id}` - Suppression
- `POST /{record_id}/process` - Traitement (admin)
- `POST /{record_id}/validate` - Validation (admin)
- `POST /{record_id}/upload-image` - Upload image

#### Notifications (`/api/v1/notifications`)
- `GET /` - Notifications utilisateur
- `POST /` - Créer notification (admin)
- `POST /bulk` - Notifications en lot (admin)
- `POST /broadcast` - Diffusion (admin)
- `POST /mark-read` - Marquer comme lu
- `POST /devices` - Enregistrer appareil push

#### Statistiques (`/api/v1/statistics`)
- `GET /dashboard` - Dashboard complet (admin)
- `GET /users` - Statistiques utilisateurs (admin)
- `GET /waste` - Statistiques déchets (admin)
- `GET /realtime` - Données temps réel (admin)

### Socket.IO Events

#### Client vers Serveur
- `connect` - Connexion avec token JWT
- `ping` - Maintien de connexion
- `get_dashboard_data` - Données dashboard
- `join_room` - Rejoindre une room
- `leave_room` - Quitter une room

#### Serveur vers Client
- `welcome` - Message de bienvenue
- `user_connected` - Utilisateur connecté
- `user_disconnected` - Utilisateur déconnecté
- `waste_update` - Mise à jour déchets
- `notification` - Nouvelle notification
- `dashboard_update` - Mise à jour dashboard

## Sécurité

### Authentification
- JWT avec expiration configurable
- Refresh tokens sécurisés
- Reconnaissance faciale avec tolérance ajustable
- Chiffrement des données biométriques

### Autorisations
- Système de rôles granulaire
- Vérification des permissions sur chaque endpoint
- Isolation des données utilisateur
- Accès admin sécurisé

### Protection des Données
- Chiffrement des données sensibles
- Validation stricte des entrées
- Sanitisation des données
- Logging de sécurité

## Performance et Scalabilité

### Optimisations
- Requêtes SQL optimisées
- Pagination sur toutes les listes
- Cache Redis pour les sessions
- Connexions de base de données poolées

### Monitoring
- Logging structuré avec Structlog
- Métriques Prometheus
- Surveillance des performances
- Alertes automatiques

### Scalabilité
- Architecture asynchrone
- Support multi-workers
- Séparation des tâches lourdes (Celery)
- Cache distribué

## Tests

### Tests Unitaires
```bash
pytest tests/ -v --cov=app
```

### Tests d'Intégration
```bash
pytest tests/integration/ -v
```

### Tests de Performance
```bash
pytest tests/performance/ -v
```

## Déploiement

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/waste_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: waste_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
  
  redis:
    image: redis:6
```

## Maintenance

### Migrations de Base de Données
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Sauvegarde
```bash
pg_dump waste_management_db > backup.sql
```

### Monitoring
- Surveillance des logs avec ELK Stack
- Métriques avec Prometheus/Grafana
- Alertes Slack/Email automatiques

## Support et Contribution

### Développement
1. Fork le repository
2. Créer une branche feature
3. Développer avec tests
4. Créer une Pull Request

### Issues
- Reporter les bugs via GitHub Issues
- Proposer des améliorations
- Documenter les cas d'usage

---

**Développé avec ❤️ pour un futur plus vert** 🌱