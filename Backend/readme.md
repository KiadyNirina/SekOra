# SekOra Backend

Backend de **SekOra**, une application de gestion scolaire développée avec Django et Django REST Framework.

Il fournit les API nécessaires au fonctionnement de la plateforme et communique avec le frontend développé avec Svelte.

## 🚀 Stack technique

- Python 3.10
- Django & Django REST Framework
- JWT Authentication
- Django Channels & Redis
- MySQL 8.0
- phpMyAdmin
- Docker & Docker Compose

## 📁 Structure du projet

```text
Backend/
├── backend/
│   ├── backend/
│   ├── base/
│   ├── manage.py
│   └── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
└── README.md
```

## ⚙️ Installation

### Prérequis

- Git
- Docker
- Docker Compose

Vérifier leur installation :

```bash
docker --version
docker compose version
```

### Cloner le projet

```bash
git clone https://github.com/KiadyNirina/SekOra.git
cd SekOra/Backend
```

### Configurer les variables d'environnement

Créer un fichier `.env` à la racine du backend , voici un exemple:

```env
DB_NAME=eboss_nez
DB_USER=root
DB_PASSWORD=root
DB_HOST=db
DB_PORT=3306
REDIS_HOST=redis
REDIS_PORT=6379
```

### Démarrer les services

Construire l'image Docker :

```bash
docker compose build
```

Démarrer les conteneurs :

```bash
docker compose up -d
```

Vérifier leur état :

```bash
docker compose ps
```

## 🗄️ Base de données

La base de données utilisée est MySQL. Elle fonctionne dans un conteneur Docker et est accessible depuis Django via le service `db`.

Pour appliquer les migrations :

```bash
docker compose exec backend python manage.py migrate
```

Créer un superutilisateur :

```bash
docker compose exec backend python manage.py createsuperuser
```

## 🌐 Accès aux services

| Service | Adresse locale |
|---|---|
| Backend Django | http://localhost:8000 |
| phpMyAdmin | http://localhost:8080 |

## 📌 Architecture

```text
SekOra
├── Frontend : Svelte
└── Backend
    ├── Django REST Framework
    ├── JWT Authentication
    ├── Django Channels
    ├── MySQL
    └── Redis
```

## 📄 Licence

Projet SekOra — tous droits réservés.