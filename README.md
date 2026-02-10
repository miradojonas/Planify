# Planify

Démo Flask (portfolio) : agenda scolaire + EDT + devoirs + chat.

## Stack

- Backend: Flask + Flask-Login + SQLAlchemy
- DB: PostgreSQL (Render) en prod, SQLite en local (fallback)
- Déploiement: Render

## Lancer en local

### 1) Installer

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configurer les variables

- Copie `.env.example` vers `.env` et remplis au minimum `SECRET_KEY`.
- Pour utiliser PostgreSQL en local, renseigne aussi `DATABASE_URL` (URI).

### 3) Initialiser la base

```bash
python scripts/init_db.py
```

Optionnel (seed users de démo) :

```bash
SEED_DEFAULT_USERS=true python scripts/init_db.py
```

### 4) Démarrer

```bash
python app.py
```

Puis ouvre http://localhost:5000

## Déployer sur Render

### 1) Créer une base de données PostgreSQL

1. Sur [Render](https://render.com), crée un nouveau **PostgreSQL** service.
2. Copie l'**Internal Database URL** (elle sera injectée automatiquement si tu lies les services).

### 2) Créer un Web Service

1. Importe ton repo GitHub dans Render.
2. Configure :
   - **Runtime** : Python
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`
3. Dans **Environment Variables**, ajouter :
   - `DATABASE_URL` → l'URL PostgreSQL de Render
   - `SECRET_KEY` → une clé secrète aléatoire
   - `SEED_DEFAULT_USERS=true` (optionnel, pour créer les comptes de démo)
4. Déployer.

## Dépannage

- Si l'app utilise SQLite en prod : vérifie que `DATABASE_URL` est bien défini sur Render.
- Pour voir les logs : Dashboard Render → ton service → Logs.
