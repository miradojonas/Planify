from flask_sqlalchemy import SQLAlchemy
from models.user import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'homework', 'grade', 'reminder', 'system'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'), nullable=True)
    
    # Relations
    user = db.relationship('User', backref='notifications')
    homework = db.relationship('Homework', backref='notifications')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'homework_id': self.related_homework_id,
            'time_ago': self.get_time_ago()
        }
    
    def get_time_ago(self):
        if not self.created_at:
            return "Maintenant"
        
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"Il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"Il y a {hours} heure{'s' if hours > 1 else ''}"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"Il y a {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "À l'instant"
    
    @staticmethod
    def create_homework_notification(user_id, homework):
        """Créer une notification pour un nouveau devoir"""
        notification = Notification(
            user_id=user_id,
            title="Nouveau devoir assigné",
            message=f"Un nouveau devoir '{homework.title}' a été assigné. Échéance: {homework.due_date.strftime('%d/%m/%Y à %H:%M')}",
            type="homework",
            related_homework_id=homework.id
        )
        db.session.add(notification)
        return notification
    
    @staticmethod
    def create_grade_notification(user_id, homework, grade):
        """Créer une notification pour une note reçue"""
        notification = Notification(
            user_id=user_id,
            title="Note reçue",
            message=f"Votre devoir '{homework.title}' a été corrigé. Note: {grade}/{homework.points}",
            type="grade",
            related_homework_id=homework.id
        )
        db.session.add(notification)
        return notification
    
    @staticmethod
    def create_reminder_notification(user_id, homework):
        """Créer une notification de rappel d'échéance"""
        notification = Notification(
            user_id=user_id,
            title="Échéance approchante",
            message=f"Le devoir '{homework.title}' doit être rendu dans moins de 24h!",
            type="reminder",
            related_homework_id=homework.id
        )
        db.session.add(notification)
        return notification
    
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        self.is_read = True
        db.session.commit()