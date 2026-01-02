from .user import db
from datetime import datetime
import json

class AIChat(db.Model):
    __tablename__ = 'ai_chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(32), default='text')
    context = db.Column(db.Text)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'type': self.message_type,
            'timestamp': self.created_at.isoformat()
        }

class Summary(db.Model):
    __tablename__ = 'summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text)
    summary = db.Column(db.Text, nullable=False)
    summary_type = db.Column(db.String(32), default='general')
    meta_data = db.Column(db.Text)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_metadata(self):
        return json.loads(self.meta_data) if self.meta_data else {}

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(128), nullable=False)
    questions = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(32), default='medium')
    score = db.Column(db.Float)
    max_score = db.Column(db.Integer, default=10)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_questions(self):
        return json.loads(self.questions) if self.questions else []
    
    def set_questions(self, questions_list):
        self.questions = json.dumps(questions_list)