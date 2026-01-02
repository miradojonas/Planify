#!/usr/bin/env python3
"""
Script de lancement pour tester le calendrier PLANIFY avec horloge temps réel
"""

import webbrowser
import time
from threading import Timer

def open_browser():
    """Ouvrir le navigateur après le démarrage du serveur"""
    time.sleep(2)  # Attendre que le serveur soit prêt
    webbrowser.open('http://127.0.0.1:5000/calendar')

if __name__ == '__main__':
    print("🚀 LANCEMENT DU CALENDRIER PLANIFY AVEC HORLOGE TEMPS RÉEL")
    print("=" * 60)
    print("📅 Fonctionnalités du calendrier programmé:")
    print("   ⏰ Horloge temps réel avec affichage de l'heure et date")
    print("   🎯 Animation des événements en cours")
    print("   ⏱️  Gestion des heures de début et fin")
    print("   📊 Tri automatique par horaire")
    print("   📱 Interface responsive")
    print("   ✅ Validation des créneaux horaires")
    print("\n🌐 Le navigateur va s'ouvrir automatiquement sur /calendar")
    print("📍 URL: http://127.0.0.1:5000/calendar")
    print("\n" + "=" * 60)
    
    # Programmer l'ouverture du navigateur
    timer = Timer(2.0, open_browser)
    timer.start()
    
    # Lancer l'application Flask
    from app import app
    app.run(debug=True, host='127.0.0.1', port=5000)