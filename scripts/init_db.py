"""
Planify — Initialisation de la base de données
================================================
Ce script crée toutes les tables et peut optionnellement
insérer les utilisateurs par défaut (seed).

Usage local (SQLite) :
  python scripts/init_db.py

Usage PostgreSQL (Render) :
  DATABASE_URL="postgresql://..." python scripts/init_db.py

Avec seed des utilisateurs :
  SEED_DEFAULT_USERS=true python scripts/init_db.py
"""

import os
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Force DB init when running this script explicitly.
os.environ.setdefault("AUTO_INIT_DB", "true")

from app import app, db, _init_db_if_needed  # noqa: E402


if __name__ == "__main__":
    with app.app_context():
        _init_db_if_needed()

        # Vérification
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n✅ Base de données initialisée avec succès !")
        print(f"📊 {len(tables)} table(s) créée(s) :")
        for t in sorted(tables):
            print(f"   • {t}")

        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if 'postgresql' in db_uri:
            print(f"\n🐘 Mode PostgreSQL (Render)")
        else:
            print(f"\n🗄️  Mode SQLite (local)")
        print(f"📡 URI: {db_uri[:60]}...")
