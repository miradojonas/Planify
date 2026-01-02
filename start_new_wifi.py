#!/usr/bin/env python3
"""
Détection automatique de l'IP pour PLANIFY Mobile après changement de WiFi
"""

import socket
import subprocess

def get_current_ip():
    """Obtenir l'adresse IP actuelle"""
    try:
        # Méthode 1: Connexion test vers Google DNS
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            # Méthode 2: Via hostname
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "127.0.0.1"

def get_wifi_info():
    """Obtenir les informations WiFi Windows"""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'profile'], 
                              capture_output=True, text=True, encoding='cp1252')
        if result.returncode == 0:
            # Extraire le nom du réseau connecté
            for line in result.stdout.split('\n'):
                if 'Profil Tous les utilisateurs' in line or 'All User Profile' in line:
                    wifi_name = line.split(':')[-1].strip()
                    return wifi_name
    except:
        pass
    return "WiFi détecté"

if __name__ == '__main__':
    current_ip = get_current_ip()
    wifi_name = get_wifi_info()
    
    print("📶 NOUVEAU WIFI DÉTECTÉ - MISE À JOUR PLANIFY")
    print("=" * 55)
    print(f"🌐 Nouvelle adresse IP : {current_ip}")
    print(f"📶 Réseau WiFi : {wifi_name}")
    print(f"🔌 Port : 8080")
    print()
    print("📱 NOUVELLE URL POUR VOTRE TÉLÉPHONE :")
    print(f"   http://{current_ip}:8080")
    print()
    print("📋 INSTRUCTIONS MISES À JOUR :")
    print("   1. Connectez votre téléphone à ce nouveau WiFi")
    print("   2. Ouvrez votre navigateur mobile")
    print(f"   3. Tapez : http://{current_ip}:8080")
    print("   4. Connectez-vous avec vos identifiants PLANIFY")
    print()
    print("🔑 COMPTES DISPONIBLES :")
    print("   - Admin : admin@planify.fr / admin123")
    print("   - Prof : prof@planify.fr / prof123")
    print("   - Élève : eleve@planify.fr / eleve123")
    print()
    print("=" * 55)
    print("🚀 Démarrage de PLANIFY avec la nouvelle IP...")
    
    # Démarrer l'application
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        input("Appuyez sur Entrée pour fermer...")