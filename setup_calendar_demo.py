#!/usr/bin/env python3
"""
Script pour nettoyer les événements de démonstration du calendrier
"""

from app import app, db
from models.calendar import Event

def clean_demo_events():
    """Supprimer tous les événements de démonstration"""
    with app.app_context():
        # Supprimer tous les événements existants
        existing_events = Event.query.count()
        if existing_events > 0:
            print(f"SUPPRESSION: {existing_events} evenements de demonstration supprimes...")
            Event.query.delete()
            db.session.commit()
            print("TERMINE: Tous les evenements de demonstration ont ete supprimes.")
        else:
            print("AUCUN: Aucun evenement a supprimer.")
            db.session.commit()
        
        # Récupérer un utilisateur admin ou professeur pour créer les événements
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            admin_user = User.query.filter_by(role='professeur').first()
        
        if not admin_user:
            print("ERREUR: Aucun utilisateur admin ou professeur trouve!")
            return
        
        # Date d'aujourd'hui et demain
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Événements de démonstration avec horaires précis
        demo_events = [
            # Événements d'aujourd'hui
            {
                'title': 'Cours de Mathématiques',
                'start_date': datetime.combine(today, datetime.min.time().replace(hour=8, minute=0)),
                'end_date': datetime.combine(today, datetime.min.time().replace(hour=9, minute=30)),
                'event_type': 'cours',
                'description': 'Algèbre linéaire - Salle A101',
                'color': '#3b82f6'
            },
            {
                'title': 'Cours de Physique',
                'start_date': datetime.combine(today, datetime.min.time().replace(hour=10, minute=0)),
                'end_date': datetime.combine(today, datetime.min.time().replace(hour=11, minute=30)),
                'event_type': 'cours',
                'description': 'Mécanique quantique - Labo B203',
                'color': '#3b82f6'
            },
            {
                'title': 'Réunion Pédagogique',
                'start_date': datetime.combine(today, datetime.min.time().replace(hour=14, minute=0)),
                'end_date': datetime.combine(today, datetime.min.time().replace(hour=15, minute=30)),
                'event_type': 'reunion',
                'description': 'Préparation des examens - Salle des professeurs',
                'color': '#8b5cf6'
            },
            {
                'title': 'Contrôle Continu',
                'start_date': datetime.combine(today, datetime.min.time().replace(hour=16, minute=0)),
                'end_date': datetime.combine(today, datetime.min.time().replace(hour=17, minute=0)),
                'event_type': 'examen',
                'description': 'Test de Chimie - Amphithéâtre C',
                'color': '#ef4444'
            },
            
            # Événements de demain
            {
                'title': 'Cours d\'Histoire',
                'start_date': datetime.combine(tomorrow, datetime.min.time().replace(hour=9, minute=0)),
                'end_date': datetime.combine(tomorrow, datetime.min.time().replace(hour=10, minute=30)),
                'event_type': 'cours',
                'description': 'Histoire contemporaine - Salle D205',
                'color': '#3b82f6'
            },
            {
                'title': 'TP Informatique',
                'start_date': datetime.combine(tomorrow, datetime.min.time().replace(hour=11, minute=0)),
                'end_date': datetime.combine(tomorrow, datetime.min.time().replace(hour=12, minute=30)),
                'event_type': 'cours',
                'description': 'Programmation Python - Salle info E101',
                'color': '#3b82f6'
            },
            {
                'title': 'Conseil de Classe',
                'start_date': datetime.combine(tomorrow, datetime.min.time().replace(hour=13, minute=30)),
                'end_date': datetime.combine(tomorrow, datetime.min.time().replace(hour=15, minute=0)),
                'event_type': 'reunion',
                'description': 'Bilan trimestriel - Salle de conférence',
                'color': '#8b5cf6'
            },
            {
                'title': 'Examen Final',
                'start_date': datetime.combine(tomorrow, datetime.min.time().replace(hour=15, minute=30)),
                'end_date': datetime.combine(tomorrow, datetime.min.time().replace(hour=17, minute=30)),
                'event_type': 'examen',
                'description': 'Examen de Philosophie - Amphithéâtre A',
                'color': '#ef4444'
            }
        ]
        
        # Créer les événements
        created_count = 0
        for event_data in demo_events:
            event = Event(
                title=event_data['title'],
                start_date=event_data['start_date'],
                end_date=event_data['end_date'],
                event_type=event_data['event_type'],
                description=event_data['description'],
                color=event_data['color'],
                user_id=admin_user.id
            )
            
            db.session.add(event)
            created_count += 1
        
        # Ajouter un evenement en cours pour tester l'animation
        now = datetime.now()
        current_time = now.replace(second=0, microsecond=0)
        
        # Evenement qui se deroule maintenant (30 minutes)
        current_event = Event(
            title='COURS EN COURS - Demo',
            start_date=current_time - timedelta(minutes=10),
            end_date=current_time + timedelta(minutes=20),
            event_type='cours',
            description='Cet evenement est en cours pour tester l\'animation temps reel',
            color='#ffd700',  # Couleur doree pour se demarquer
            user_id=admin_user.id
        )
        
        db.session.add(current_event)
        created_count += 1
        
        try:
            db.session.commit()
            print(f"SUCCES: {created_count} evenements de demonstration crees avec succes!")
            print(f"CALENDRIER: Evenements crees pour aujourd'hui ({today.strftime('%d/%m/%Y')}) et demain ({tomorrow.strftime('%d/%m/%Y')})")
            print("EN COURS: Un evenement est configure comme 'EN COURS' pour tester l'animation temps reel")
            print("\nFONCTIONNALITES ajoutees au calendrier:")
            print("   - Horloge temps reel avec date et heure actuelles")
            print("   - Animation des evenements en cours (bordure doree et pulsation)")
            print("   - Affichage des heures de debut et fin pour chaque evenement")
            print("   - Tri automatique des evenements par heure")
            print("   - Validation des horaires (fin apres debut)")
            print("   - Interface responsive pour mobile")
            
        except Exception as e:
            db.session.rollback()
            print(f"ERREUR lors de la creation des evenements: {e}")

if __name__ == '__main__':
    print("CALENDRIER PLANIFY - Nettoyage des evenements de demonstration")
    print("=" * 70)
    clean_demo_events()
    print("\nPROPRE: Le calendrier est maintenant vide et pret a l'utilisation!")
    print("CONSEIL: Visitez /calendar pour creer vos propres evenements")