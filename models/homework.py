from .user import db
from datetime import datetime

class Homework(db.Model):
    __tablename__ = 'homework'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    subject = db.Column(db.String(64))  # Matière
    points = db.Column(db.Integer, default=20)  # Points sur lesquels le devoir est noté
    attachment_url = db.Column(db.String(256))  # Fichier joint
    is_published = db.Column(db.Boolean, default=True)  # Visible par les élèves
    
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Professeur qui a créé
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    submissions = db.relationship('HomeworkSubmission', backref='homework', lazy='dynamic', cascade='all, delete-orphan')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='created_homework')
    
    def get_submission_for_student(self, student_id):
        """Récupère la soumission d'un élève pour ce devoir"""
        return HomeworkSubmission.query.filter_by(
            homework_id=self.id,
            student_id=student_id
        ).first()
    
    def is_overdue(self):
        """Vérifie si le devoir est en retard"""
        return datetime.utcnow() > self.due_date
    
    def get_submission_count(self):
        """Nombre de soumissions reçues"""
        return self.submissions.count()
    
    def get_status_for_student(self, student_id):
        """Statut du devoir pour un élève spécifique"""
        submission = self.get_submission_for_student(student_id)
        if submission:
            return submission.status
        elif self.is_overdue():
            return 'overdue'
        else:
            return 'pending'
    
    def to_dict(self, student_id=None):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat(),
            'subject': self.subject,
            'points': self.points,
            'is_published': self.is_published,
            'submission_count': self.get_submission_count(),
            'is_overdue': self.is_overdue(),
            'teacher_name': f"{self.teacher.prenom} {self.teacher.nom}"
        }
        
        if student_id:
            submission = self.get_submission_for_student(student_id)
            data['student_submission'] = submission.to_dict() if submission else None
            data['status'] = self.get_status_for_student(student_id)
        
        return data

class HomeworkSubmission(db.Model):
    __tablename__ = 'homework_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text)  # Réponse textuelle
    attachment_url = db.Column(db.String(256))  # Fichier joint par l'élève
    grade = db.Column(db.Float)  # Note attribuée
    feedback = db.Column(db.Text)  # Commentaires du professeur
    status = db.Column(db.String(20), default='submitted')  # submitted, graded, late
    
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime)
    
    # Relations
    student = db.relationship('User', foreign_keys=[student_id], backref='homework_submissions')
    
    def is_late(self):
        """Vérifie si la soumission est en retard"""
        return self.submitted_at > self.homework.due_date
    
    def to_dict(self):
        return {
            'id': self.id,
            'homework_id': self.homework_id,
            'student_name': f"{self.student.prenom} {self.student.nom}",
            'content': self.content,
            'grade': self.grade,
            'feedback': self.feedback,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat(),
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'is_late': self.is_late()
        }