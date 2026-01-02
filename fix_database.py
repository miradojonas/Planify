#!/usr/bin/env python3
"""
Script de migration SQLite pour ajouter la colonne channel_type à la table existante
"""
import sqlite3
import os
import sys

def migrate_database():
    """Effectue la migration de la base de données SQLite"""
    db_path = 'agenda_scolaire.db'
    
    try:
        print("🔄 Début de la migration SQLite...")
        
        # Vérifier si la base existe
        if not os.path.exists(db_path):
            print("❌ Base de données introuvable. Création d'une nouvelle base...")
            create_fresh_database()
            return
        
        # Connexion à la base
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne channel_type existe déjà
        cursor.execute("PRAGMA table_info(chat_rooms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'channel_type' not in columns:
            print("➕ Ajout de la colonne channel_type...")
            cursor.execute("ALTER TABLE chat_rooms ADD COLUMN channel_type VARCHAR(20) DEFAULT 'direct'")
            conn.commit()
            print("✅ Colonne channel_type ajoutée avec succès")
        else:
            print("ℹ️ La colonne channel_type existe déjà")
        
        # Vérifier la structure finale
        cursor.execute("PRAGMA table_info(chat_rooms)")
        columns = cursor.fetchall()
        print("\n📋 Structure de la table chat_rooms:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n🎉 Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration SQLite: {e}")
        print("🔄 Tentative de création d'une nouvelle base...")
        create_fresh_database()

def create_fresh_database():
    """Crée une nouvelle base de données complète"""
    try:
        # Supprimer l'ancienne base si elle existe
        if os.path.exists('agenda_scolaire.db'):
            os.remove('agenda_scolaire.db')
            print("✅ Ancienne base supprimée")
        
        # Créer avec Flask-SQLAlchemy
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import app, db
        from models.user import User
        
        with app.app_context():
            db.create_all()
            print("✅ Nouvelle base créée avec SQLAlchemy")
            
            # Créer des utilisateurs de test
            if not User.query.filter_by(role='admin').first():
                admin = User(nom='Admin', prenom='PLANIFY', email='admin@planify.fr', role='admin')
                admin.set_password('admin123')
                
                prof = User(nom='Dupont', prenom='Jean', email='prof@planify.fr', role='professeur')
                prof.set_password('prof123')
                
                eleve = User(nom='Martin', prenom='Pierre', email='eleve@planify.fr', role='eleve')
                eleve.set_password('eleve123')
                
                db.session.add_all([admin, prof, eleve])
                db.session.commit()
                print("✅ Utilisateurs de test créés")
                
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")

if __name__ == '__main__':
    migrate_database()