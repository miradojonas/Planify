"""
Script pour créer des notifications de rappel automatiques
À exécuter périodiquement (par exemple avec un cron job)
"""

from datetime import datetime, timedelta
from app import app, db
from models.user import User
from models.homework import Homework, HomeworkSubmission
from models.notification import Notification

def create_reminder_notifications():
    """Créer des notifications de rappel pour les devoirs dont l'échéance approche"""
    
    with app.app_context():
        # Trouver les devoirs qui expirent dans les prochaines 24 heures
        now = datetime.utcnow()
        tomorrow = now + timedelta(hours=24)
        
        upcoming_homework = Homework.query.filter(
            Homework.is_published == True,
            Homework.due_date > now,
            Homework.due_date <= tomorrow
        ).all()
        
        print(f"Trouvé {len(upcoming_homework)} devoirs avec échéance dans les 24h")
        
        for homework in upcoming_homework:
            # Trouver tous les élèves qui n'ont pas encore rendu ce devoir
            students_without_submission = db.session.query(User).filter(
                User.role == 'eleve',
                ~User.id.in_(
                    db.session.query(HomeworkSubmission.student_id)
                    .filter(HomeworkSubmission.homework_id == homework.id)
                )
            ).all()
            
            print(f"Devoir '{homework.title}': {len(students_without_submission)} élèves n'ont pas rendu")
            
            for student in students_without_submission:
                # Vérifier qu'une notification de rappel n'a pas déjà été envoyée
                existing_reminder = Notification.query.filter_by(
                    user_id=student.id,
                    related_homework_id=homework.id,
                    type='reminder'
                ).first()
                
                if not existing_reminder:
                    # Créer la notification de rappel
                    Notification.create_reminder_notification(student.id, homework)
                    print(f"Notification de rappel créée pour {student.prenom} {student.nom}")
        
        db.session.commit()
        print("Notifications de rappel créées avec succès")

if __name__ == '__main__':
    create_reminder_notifications()