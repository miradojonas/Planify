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

if __name__ == '__main__':
    print("CALENDRIER PLANIFY - Nettoyage des evenements de demonstration")
    print("=" * 70)
    clean_demo_events()
    print("\nPROPRE: Le calendrier est maintenant vide et pret a l'utilisation!")
    print("CONSEIL: Visitez /calendar pour creer vos propres evenements")