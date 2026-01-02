from .user import db
from datetime import datetime

class Classroom(db.Model):
    __tablename__ = 'classrooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)
    equipment = db.Column(db.Text)
    location = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    courses = db.relationship('Course', backref='classroom', lazy='dynamic')
    
    def __repr__(self):
        return f'<Classroom {self.name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#10b981')
    
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    time_slots = db.relationship('TimeSlot', backref='course', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic')
    
    def __repr__(self):
        return f'<Course {self.name}>'

class TimeSlot(db.Model):
    __tablename__ = 'time_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=lundi, 1=mardi, etc.
    time_range = db.Column(db.String(32), nullable=False)  # "08:00-09:30"
    
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    def get_day_name(self):
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        return days[self.day_of_week] if self.day_of_week < len(days) else 'Inconnu'
    
    def __repr__(self):
        return f'<TimeSlot {self.get_day_name()} {self.time_range}>'