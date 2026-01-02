from .user import db
from datetime import datetime

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    channel_type = db.Column(db.String(20), default='direct')  # direct, prof_student, prof_admin, admin_student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('Message', backref='chat', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_other_user(self, current_user_id):
        return self.user2 if self.user1_id == current_user_id else self.user1
    
    def get_unread_count(self, current_user_id):
        return Message.query.filter_by(
            chat_id=self.id, 
            read=False
        ).filter(Message.sender_id != current_user_id).count()
    
    def get_last_message(self):
        return Message.query.filter_by(chat_id=self.id).order_by(Message.created_at.desc()).first()
    
    def can_user_access(self, user_id, user_role):
        """Vérifie si un utilisateur peut accéder à ce canal"""
        # L'utilisateur peut toujours accéder à ses propres conversations
        if user_id in [self.user1_id, self.user2_id]:
            return True
        return False
    
    def is_message_visible_to_user(self, message, user_id, user_role):
        """Vérifie si un message est visible pour un utilisateur selon les règles de canal"""
        # Messages directs : visibles pour les participants
        if self.channel_type == 'direct':
            return user_id in [self.user1_id, self.user2_id]
        
        # Canal prof-étudiant : prof ne voit pas les messages admin
        elif self.channel_type == 'prof_student':
            if user_role == 'professeur' and message.sender.role == 'admin':
                return False
            return user_id in [self.user1_id, self.user2_id]
        
        # Autres canaux : accès normal
        return user_id in [self.user1_id, self.user2_id]
    
    @staticmethod
    def get_channel_type(user1_role, user2_role):
        """Détermine le type de canal selon les rôles des utilisateurs"""
        roles = sorted([user1_role, user2_role])
        
        if roles == ['admin', 'eleve']:
            return 'admin_student'
        elif roles == ['admin', 'professeur']:
            return 'prof_admin'
        elif roles == ['eleve', 'professeur']:
            return 'prof_student'
        else:
            return 'direct'

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'sender_id': self.sender_id,
            'read': self.read,
            'created_at': self.created_at.isoformat()
        }