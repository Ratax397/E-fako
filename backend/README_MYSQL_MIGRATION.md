# Migration MySQL - Guide d'Installation et Configuration

## Vue d'ensemble

Ce guide vous accompagne dans la migration complète de votre backend PostgreSQL vers MySQL pour l'application de gestion des déchets.

## Prérequis

### 1. Installation de MySQL

#### Sur Ubuntu/Debian:
```bash
sudo apt update
sudo apt install mysql-server mysql-client
sudo mysql_secure_installation
```

#### Sur CentOS/RHEL:
```bash
sudo yum install mysql-server mysql-client
sudo systemctl start mysqld
sudo mysql_secure_installation
```

#### Sur macOS (avec Homebrew):
```bash
brew install mysql
brew services start mysql
```

#### Sur Windows:
- Téléchargez MySQL Installer depuis [mysql.com](https://dev.mysql.com/downloads/installer/)
- Suivez l'assistant d'installation

### 2. Vérification de l'installation
```bash
mysql --version
```

## Installation et Configuration

### Étape 1: Configuration de la base de données

1. **Lancez le script de configuration MySQL:**
```bash
cd backend
python setup_mysql.py
```

Ce script va:
- Créer la base de données `waste_management`
- Créer l'utilisateur `waste_user`
- Configurer les permissions
- Créer le fichier `.env` avec les variables d'environnement

### Étape 2: Installation des dépendances

```bash
# Installer les nouvelles dépendances MySQL
pip install -r requirements.txt

# Vérifier l'installation
python -c "import mysql.connector; print('MySQL connecteur installé avec succès')"
```

### Étape 3: Création des migrations

```bash
# Créer la migration initiale
python create_initial_migration.py

# Appliquer les migrations
alembic upgrade head
```

### Étape 4: Test de la connexion

```bash
# Tester la connexion à la base de données
python -c "
from app.core.database import test_db_connection
import asyncio
result = asyncio.run(test_db_connection())
print('Connexion réussie!' if result else 'Échec de connexion')
"
```

## Configuration de l'Environnement

### Variables d'Environnement (.env)

Le fichier `.env` généré contient:

```env
# Configuration de la base de données MySQL
DATABASE_URL=mysql+pymysql://waste_user:waste_password_2024@localhost:3306/waste_management
DATABASE_URL_ASYNC=mysql+aiomysql://waste_user:waste_password_2024@localhost:3306/waste_management

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
```

## Lancement de l'Application

### 1. Démarrage du backend

```bash
# Démarrer l'API FastAPI
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Vérification de l'API

- **Documentation API:** http://localhost:8000/api/v1/docs
- **Health Check:** http://localhost:8000/health
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

### 3. Test des endpoints

```bash
# Test de santé
curl http://localhost:8000/health

# Test de l'API
curl http://localhost:8000/
```

## Gestion des Migrations

### Commandes Alembic utiles

```bash
# Voir l'historique des migrations
alembic history

# Voir la migration actuelle
alembic current

# Créer une nouvelle migration
alembic revision --autogenerate -m "Description de la migration"

# Appliquer toutes les migrations
alembic upgrade head

# Revenir à une migration spécifique
alembic downgrade <revision_id>

# Voir les migrations en attente
alembic show <revision_id>
```

## Intégration avec le Frontend Electron.js

### Configuration du Frontend

Le frontend Electron.js n'a pas besoin de modifications majeures car il communique avec l'API via HTTP. Assurez-vous que:

1. **L'API backend est accessible** depuis le frontend
2. **Les CORS sont configurés** correctement
3. **Les endpoints restent les mêmes** (pas de changement d'API)

### Test de l'Intégration

```bash
# Démarrer le frontend
cd ..  # Retour au répertoire racine
npm run dev
```

## Dépannage

### Problèmes Courants

#### 1. Erreur de connexion MySQL
```bash
# Vérifier que MySQL est démarré
sudo systemctl status mysql

# Vérifier les permissions utilisateur
mysql -u root -p
SHOW GRANTS FOR 'waste_user'@'localhost';
```

#### 2. Erreur de migration Alembic
```bash
# Réinitialiser Alembic
rm -rf alembic/versions/*
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

#### 3. Problème de dépendances Python
```bash
# Nettoyer et réinstaller
pip uninstall mysqlclient pymysql aiomysql
pip install -r requirements.txt
```

#### 4. Erreur de caractères UTF-8
```sql
-- Dans MySQL
ALTER DATABASE waste_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Sécurité

### Recommandations de Production

1. **Changer les mots de passe par défaut**
2. **Utiliser des clés JWT sécurisées**
3. **Configurer SSL/TLS pour MySQL**
4. **Restreindre l'accès réseau**
5. **Sauvegarder régulièrement la base de données**

### Exemple de configuration sécurisée

```env
# Production
DATABASE_URL=mysql+pymysql://waste_user:StrongPassword123!@localhost:3306/waste_management?ssl_ca=/path/to/ca.pem
JWT_SECRET_KEY=your-very-long-and-random-secret-key-here
DEBUG=false
```

## Performance

### Optimisations MySQL

```sql
-- Optimisations recommandées
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
SET GLOBAL innodb_log_file_size = 268435456; -- 256MB
SET GLOBAL max_connections = 200;
```

### Monitoring

```bash
# Vérifier les performances
mysql -u waste_user -p waste_management -e "SHOW STATUS LIKE 'Connections';"
mysql -u waste_user -p waste_management -e "SHOW STATUS LIKE 'Threads_connected';"
```

## Support

Pour toute question ou problème:

1. Vérifiez les logs de l'application
2. Consultez les logs MySQL: `sudo tail -f /var/log/mysql/error.log`
3. Testez la connexion: `mysql -u waste_user -p waste_management`

## Migration des Données (Optionnel)

Si vous avez des données existantes dans PostgreSQL, vous pouvez les migrer:

```bash
# Exporter depuis PostgreSQL
pg_dump -h localhost -U postgres -d waste_db > backup.sql

# Convertir et importer dans MySQL
# (Utilisez un outil comme pgloader ou un script personnalisé)
```

---

**Note:** Cette migration préserve toutes les fonctionnalités existantes tout en améliorant les performances avec MySQL.