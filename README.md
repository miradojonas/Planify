# Planify

Démo Flask (portfolio) : agenda scolaire + EDT + devoirs + chat.

## Stack

- Backend: Flask + Flask-Login + SQLAlchemy
- DB: Postgres (Supabase) en prod, SQLite en local (fallback)
- Déploiement: Vercel (fonction Python `api/index.py`) + Supabase

## Lancer en local

### 1) Installer

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configurer les variables

- Copie [.env.example](.env.example) vers `.env` et remplis au minimum `SECRET_KEY`.
- Pour utiliser Supabase en local, renseigne aussi `DATABASE_URL` (URI).

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

## Déployer sur Vercel + Supabase

### 1) Supabase

1. Crée un projet Supabase.
2. Récupère la connection string (URI) :
	Supabase → Project Settings → Database → Connection string (URI).
3. Utilise une URI de la forme :

```
postgresql://USER:PASSWORD@db.<PROJECT_REF>.supabase.co:5432/postgres
```

### 2) Vercel

1. Importer le repo dans Vercel.
2. Dans **Project Settings → Environment Variables**, ajouter :

- `SECRET_KEY` (obligatoire)
- `DATABASE_URL` (obligatoire en prod)
- `DB_SSLMODE=require` (recommandé)
- `AUTO_INIT_DB=false` (recommandé en serverless)

Optionnels :

- `DB_FORCE_IPV4=true` (utile si tu vois des erreurs IPv6 type “Network is unreachable”)
- `SEED_DEFAULT_USERS=true` (uniquement si tu veux injecter des comptes de démo sur une DB vide)

3. Déployer.

Vercel route tout vers la fonction Python via [vercel.json](vercel.json) et [api/index.py](api/index.py).

## Passer de la DB locale (SQLite) à Supabase (Postgres)

Dans ce projet, la DB locale est le fichier `agenda_scolaire.db` (SQLite).
En prod (Vercel), l’app doit utiliser Supabase via `DATABASE_URL`.

### Option 1 — Le plus simple (sans récupérer les données)

1. Mets `DATABASE_URL` (Supabase) dans `.env` en local et dans Vercel.
2. Crée les tables sur Supabase :

```bash
DATABASE_URL="..." python3 scripts/init_db.py
```

Ensuite, l’app n’utilise plus SQLite et tout est stocké sur Supabase.

### Option 2 — Migrer les données existantes de SQLite vers Supabase

1. Renseigne `DATABASE_URL` vers Supabase.
2. Lance la migration :

```bash
DATABASE_URL="..." python3 scripts/migrate_sqlite_to_postgres.py --sqlite-path agenda_scolaire.db
```

Si tu as déjà des données sur Supabase et que tu veux écraser (attention: destructif) :

```bash
DATABASE_URL="..." python3 scripts/migrate_sqlite_to_postgres.py --sqlite-path agenda_scolaire.db --truncate-destination
```

## Dépannage

- Si l’app utilise SQLite en prod: vérifie que `DATABASE_URL` est bien défini sur Vercel.
- Si erreur SSL Postgres: garde `DB_SSLMODE=require`.
- Si erreur réseau IPv6: essaye `DB_FORCE_IPV4=true`.
