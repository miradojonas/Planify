#!/usr/bin/env python3
"""
Script pour démarrer PLANIFY et l'afficher sur téléphone mobile
"""

import socket
import webbrowser
import time
from threading import Timer

def get_local_ip():
    """Obtenir l'adresse IP locale de l'ordinateur"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return "127.0.0.1"

def open_browser():
    """Ouvrir le navigateur après le démarrage du serveur"""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    local_ip = get_local_ip()
    
    print("📱 DÉMARRAGE DE PLANIFY POUR TÉLÉPHONE MOBILE")
    print("=" * 60)
    print(f"🌐 Serveur en cours de démarrage...")
    print(f"📍 Adresse IP locale : {local_ip}")
    print(f"🔌 Port : 8080")
    print()
    print("📲 CONNEXION DEPUIS VOTRE TÉLÉPHONE :")
    print(f"   URL : http://{local_ip}:8080")
    print()
    print("📋 ÉTAPES POUR VOTRE TÉLÉPHONE :")
    print("   1. Assurez-vous que votre téléphone est sur le même WiFi")
    print(f"   2. Ouvrez votre navigateur mobile")
    print(f"   3. Tapez : http://{local_ip}:8080")
    print("   4. Connectez-vous avec :")
    print("      - Admin : admin@planify.fr / admin123")
    print("      - Prof : prof@planify.fr / prof123") 
    print("      - Élève : eleve@planify.fr / eleve123")
    print()
    print("🔥 FONCTIONNALITÉS DISPONIBLES SUR MOBILE :")
    print("   📅 Calendrier avec horloge temps réel")
    print("   📊 EDT (Emploi du Temps)")
    print("   💬 Chat et messagerie")
    print("   🤖 Assistant IA")
    print("   📝 Devoirs et notes")
    print("   👤 Profil utilisateur")
    print("   🔔 Notifications")
    print()
    print("=" * 60)
    print("🚀 Démarrage du serveur...")
    
    # Programmer l'ouverture du navigateur sur PC
    timer = Timer(2.0, open_browser)
    timer.start()
    
    # Lancer l'application Flask
    from app import app
    app.run(debug=True, host='0.0.0.0', port=8080)