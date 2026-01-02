from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nom = db.Column(db.String(64), nullable=False)
    prenom = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, professeur, eleve
    photo = db.Column(db.String(256), default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Nouveaux champs de profil
    profile_photo = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    
    # Préférences
    email_notifications = db.Column(db.Boolean, default=True)
    homework_reminders = db.Column(db.Boolean, default=True)
    theme = db.Column(db.String(10), default='light')  # light, dark, auto
    language = db.Column(db.String(5), default='fr')
    
    # Champ updated_at retiré temporairement à cause de contraintes SQLite
    
    # Relations
    events = db.relationship('Event', backref='author', lazy='dynamic')
    courses_teaching = db.relationship('Course', backref='teacher', lazy='dynamic')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    chats_started = db.relationship('ChatRoom', foreign_keys='ChatRoom.user1_id', backref='user1', lazy='dynamic')
    chats_received = db.relationship('ChatRoom', foreign_keys='ChatRoom.user2_id', backref='user2', lazy='dynamic')
    ai_chats = db.relationship('AIChat', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.prenom} {self.nom}"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_teacher(self):
        return self.role == 'professeur'
    
    def is_student(self):
        return self.role == 'eleve'
    
    def get_initials(self):
        return f"{self.prenom[0]}{self.nom[0]}".upper()
    
    def get_profile_photo_url(self):
        """Retourne l'URL de la photo de profil ou None"""
        if self.profile_photo:
            return f"/static/uploads/profiles/{self.profile_photo}"
        return None
    
    def delete_profile_photo(self):
        """Supprime la photo de profil du système de fichiers"""
        if self.profile_photo:
            photo_path = os.path.join('static', 'uploads', 'profiles', self.profile_photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)
            self.profile_photo = None
    
    def __repr__(self):
        return f'<User {self.email}>'