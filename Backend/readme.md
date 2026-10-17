# SekOra Backend

Backend de la plateforme **SekOra**, une application de gestion scolaire développée avec **Django** et **Django REST Framework**.

Le backend fournit les API nécessaires à la gestion des établissements, utilisateurs, élèves, professeurs, parents, cours, évaluations et autres fonctionnalités de la plateforme.

L'environnement de développement est entièrement conteneurisé avec **Docker**, afin d'éviter de modifier l'environnement Python ou MySQL de la machine hôte.

---

## 🚀 Stack technique

* **Python 3.10**
* **Django**
* **Django REST Framework**
* **JWT Authentication**
* **Django Channels**
* **Redis**
* **MySQL 8.0**
* **phpMyAdmin**
* **Docker & Docker Compose**

### Principales dépendances

* `djangorestframework`
* `djangorestframework-simplejwt`
* `django-cors-headers`
* `channels`
* `channels-redis`
* `mysqlclient`
* `reportlab`
* `PyJWT`

---

## 📁 Structure du projet

```text
Backend/
│
├── backend/
│   ├── manage.py
│   │
│   ├── backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── ...
│   │
│   ├── base/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   └── requirements.txt
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
└── README.md
```

---

## 🐳 Environnement Docker

Le projet utilise plusieurs conteneurs :

```text
                 ┌─────────────────────┐
                 │    Frontend Svelte  │
                 │    localhost:5173   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Django Backend    │
                 │    localhost:8000   │
                 └─────────┬───────────┘
                           │
                 ┌─────────┴───────────┐
                 │                     │
                 ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │    MySQL     │      │    Redis     │
          │    8.0       │      │      7       │
          └──────────────┘      └──────────────┘
                 ▲
                 │
          ┌──────────────┐
          │ phpMyAdmin   │
          │ localhost:8080
          └──────────────┘
```

### Services

| Service    |   Port | Description                    |
| ---------- | -----: | ------------------------------ |
| Django     | `8000` | API Backend                    |
| MySQL      | `3306` | Base de données interne Docker |
| Redis      | `6379` | Cache / Channels               |
| phpMyAdmin | `8080` | Administration MySQL           |

MySQL et Redis ne sont volontairement **pas exposés directement sur les ports de la machine hôte**.

---

# ⚙️ Installation

## Prérequis

Installer :

* Git
* Docker
* Docker Compose

Vérifier l'installation :

```bash
docker --version
docker compose version
```

---

## 📥 Cloner le projet

```bash
git clone https://github.com/KiadyNirina/SekOra.git
cd SekOra/Backend
```

---

## 🔐 Configuration des variables d'environnement

Créer un fichier `.env` à la racine du backend :

```env
DB_NAME=eboss_nez
DB_USER=root
DB_PASSWORD=root
DB_HOST=db
DB_PORT=3306

REDIS_HOST=redis
REDIS_PORT=6379
```

> ⚠️ Ne jamais commit le fichier `.env` contenant des informations sensibles.

Il est recommandé de fournir un `.env.example` dans le repository.

---

# 🐳 Lancer le projet

Construire l'image Docker :

```bash
docker compose build
```

Démarrer les services :

```bash
docker compose up -d
```

Vérifier leur état :

```bash
docker compose ps
```

Les services doivent être `Up` :

```text
eboss_backend
eboss_mysql
eboss_redis
eboss_phpmyadmin
```

---

# 🗄️ Base de données

La base utilisée par Django est :

```text
eboss_nez
```

MySQL fonctionne dans son propre conteneur Docker.

Django y accède via :

```text
db:3306
```

et non via `localhost`.

---

## 🔄 Effectuer les migrations

Après le démarrage :

```bash
docker compose exec backend python manage.py migrate
```

Créer un superutilisateur :

```bash
docker compose exec backend python manage.py createsuperuser
```

---

# 🖥️ phpMyAdmin

phpMyAdmin est disponible à :

```text
http://localhost:8080
```

Informations de connexion :

```text
Serveur : db
Utilisateur : root
Mot de passe : root
```

La base de données principale est :

```text
eboss_nez
```

---

# 🌐 Backend API

Une fois les conteneurs démarrés, le backend est accessible à :

```text
http://localhost:8000
```

Le serveur Django est lancé avec :

```bash
python manage.py runserver 0.0.0.0:8000
```

---

# 🔑 Authentification

L'API utilise **JWT (JSON Web Token)** via `djangorestframework-simplejwt`.

Le backend gère notamment :

* authentification utilisateur ;
* access tokens ;
* refresh tokens ;
* gestion des utilisateurs ;
* permissions et rôles.

Les tokens sont utilisés par le frontend pour authentifier les requêtes API.

---

# 👥 Rôles

L'application prend en charge différents profils utilisateurs, notamment :

* Établissement
* Professeur
* Élève
* Parent

Les permissions sont gérées côté backend afin de contrôler l'accès aux différentes ressources de l'application.

---

# ⚡ Redis & WebSocket

Redis est utilisé notamment pour Django Channels.

Configuration Docker :

```text
redis:6379
```

Le backend utilise :

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        ...
    }
}
```

Cela permet notamment de gérer les fonctionnalités temps réel basées sur WebSocket.

---

# 🛠️ Commandes utiles

### Voir les conteneurs

```bash
docker compose ps
```

### Voir les logs du backend

```bash
docker compose logs backend
```

En temps réel :

```bash
docker compose logs -f backend
```

### Voir les logs MySQL

```bash
docker compose logs db
```

### Voir les logs Redis

```bash
docker compose logs redis
```

### Entrer dans le conteneur Django

```bash
docker compose exec backend bash
```

### Ouvrir un shell Django

```bash
docker compose exec backend python manage.py shell
```

### Vérifier les migrations

```bash
docker compose exec backend python manage.py showmigrations
```

### Créer de nouvelles migrations

```bash
docker compose exec backend python manage.py makemigrations
```

### Appliquer les migrations

```bash
docker compose exec backend python manage.py migrate
```

---

# 🛑 Arrêter le projet

Arrêter les conteneurs :

```bash
docker compose down
```

Cette commande conserve le volume MySQL.

Pour arrêter **et supprimer les données MySQL** :

```bash
docker compose down -v
```

> ⚠️ `-v` supprime le volume `eboss_mysql_data` et donc les données de la base Docker.

---

# 🔄 Développement

Le code local :

```text
./backend
```

est monté dans le conteneur :

```text
/app
```

Ainsi, les modifications du code Django sont directement disponibles dans le conteneur.

Après une modification nécessitant une nouvelle dépendance Python, reconstruire l'image :

```bash
docker compose build backend
docker compose up -d
```

---

# 🔒 Sécurité

Les identifiants présents dans le fichier `.env` sont destinés à l'environnement de développement local.

Pour un environnement de production, il est recommandé de :

* utiliser des mots de passe forts ;
* utiliser des variables d'environnement sécurisées ;
* désactiver `DEBUG` ;
* configurer correctement `ALLOWED_HOSTS` ;
* restreindre les origines CORS ;
* utiliser HTTPS ;
* ne pas utiliser le compte MySQL `root` pour l'application ;
* protéger les clés secrètes Django ;
* ne jamais committer `.env`.

---

# 📌 Architecture

```text
SekOra
│
├── Frontend
│   └── Svelte
│
└── Backend
    │
    ├── Django
    │   ├── REST API
    │   ├── JWT
    │   └── Channels
    │
    ├── MySQL
    │   └── eboss_nez
    │
    └── Redis
        └── Channels / WebSocket
```

---

# 👨‍💻 Développement

Le backend est développé avec Django et Django REST Framework.

L'utilisation de Docker permet de conserver un environnement de développement indépendant de l'installation Python locale de la machine.

Pour démarrer rapidement :

```bash
docker compose up -d
docker compose exec backend python manage.py migrate
```

Puis accéder au backend :

```text
http://localhost:8000
```

et à phpMyAdmin :

```text
http://localhost:8080
```

---

## 📄 Licence

Projet SekOra — tous droits réservés.
