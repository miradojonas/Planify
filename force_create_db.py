#!/usr/bin/env python3
"""
Script pour forcer la création complète de la base de données
"""
import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def force_create_database():
    """Force la création complète de la base de données"""
    try:
        print("🔄 Création forcée de la base de données...")
        
        # Importer après avoir ajouté le path
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        # Configuration Flask temporaire
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda_scolaire.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'temp-key'
        
        db = SQLAlchemy(app)
        
        # Définir les modèles directement ici pour éviter les imports
        class User(db.Model):
            __tablename__ = 'users'
            id = db.Column(db.Integer, primary_key=True)
            email = db.Column(db.String(120), unique=True, nullable=False)
            password_hash = db.Column(db.String(256), nullable=False)
            nom = db.Column(db.String(64), nullable=False)
            prenom = db.Column(db.String(64), nullable=False)
            role = db.Column(db.String(20), nullable=False)
            photo = db.Column(db.String(256), default='default.jpg')
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            is_active = db.Column(db.Boolean, default=True)
        
        class ChatRoom(db.Model):
            __tablename__ = 'chat_rooms'
            id = db.Column(db.Integer, primary_key=True)
            user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
            user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
            channel_type = db.Column(db.String(20), nullable=False, default='direct')
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        class Message(db.Model):
            __tablename__ = 'messages'
            id = db.Column(db.Integer, primary_key=True)
            chat_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
            sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
            content = db.Column(db.Text, nullable=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            read = db.Column(db.Boolean, default=False)
        
        class Event(db.Model):
            __tablename__ = 'events'
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String(100), nullable=False)
            description = db.Column(db.Text)
            start_date = db.Column(db.DateTime, nullable=False)
            end_date = db.Column(db.DateTime, nullable=False)
            author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        class Course(db.Model):
            __tablename__ = 'courses'
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(100), nullable=False)
            teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
            classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        class Classroom(db.Model):
            __tablename__ = 'classrooms'
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String(50), nullable=False)
            capacity = db.Column(db.Integer, default=30)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        class TimeSlot(db.Model):
            __tablename__ = 'time_slots'
            id = db.Column(db.Integer, primary_key=True)
            course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
            day_of_week = db.Column(db.Integer, nullable=False)
            start_time = db.Column(db.Time, nullable=False)
            end_time = db.Column(db.Time, nullable=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        class AIChat(db.Model):
            __tablename__ = 'ai_chats'
            id = db.Column(db.Integer, primary_key=True)
            user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
            message = db.Column(db.Text, nullable=False)
            response = db.Column(db.Text, nullable=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        class Assignment(db.Model):
            __tablename__ = 'assignments'
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String(100), nullable=False)
            description = db.Column(db.Text)
            due_date = db.Column(db.DateTime, nullable=False)
            author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        with app.app_context():
            # Supprimer l'ancienne base
            if os.path.exists('agenda_scolaire.db'):
                os.remove('agenda_scolaire.db')
                print("✅ Ancienne base supprimée")
            
            # Créer toutes les tables
            db.create_all()
            print("✅ Toutes les tables créées")
            
            # Créer les utilisateurs de test
            admin = User(
                nom='Administrateur',
                prenom='PLANIFY',
                email='admin@planify.fr',
                role='admin',
                password_hash=generate_password_hash('admin123')
            )
            
            prof = User(
                nom='Dupont',
                prenom='Jean',
                email='prof@planify.fr',
                role='professeur',
                password_hash=generate_password_hash('prof123')
            )
            
            eleve = User(
                nom='Martin',
                prenom='Pierre',
                email='eleve@planify.fr',
                role='eleve',
                password_hash=generate_password_hash('eleve123')
            )
            
            db.session.add_all([admin, prof, eleve])
            db.session.commit()
            print("✅ Utilisateurs de test créés")
            
            # Vérifier la structure de chat_rooms
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('chat_rooms')
            print("\n📋 Structure de chat_rooms:")
            for col in columns:
                print(f"   - {col['name']} ({col['type']})")
        
        print("\n🎉 Base de données créée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    force_create_database()