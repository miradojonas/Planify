#!/usr/bin/env python3
"""
PLANIFY Mobile - Version simplifiée pour accès téléphone
"""

import socket
from flask import Flask

def get_local_ip():
    """Obtenir l'adresse IP locale"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "127.0.0.1"

# Créer l'application Flask
app = Flask(__name__)

@app.route('/')
def home():
    ip = get_local_ip()
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📱 PLANIFY Mobile Test</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 400px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
            }}
            .success {{
                font-size: 24px;
                margin-bottom: 20px;
            }}
            .info {{
                background: rgba(255,255,255,0.2);
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
            }}
            .btn {{
                background: #4CAF50;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                margin: 10px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }}
            .btn:hover {{
                background: #45a049;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">🎉 PLANIFY Mobile Connecté !</div>
            
            <div class="info">
                <strong>📱 Votre téléphone peut accéder à PLANIFY !</strong>
            </div>
            
            <div class="info">
                🌐 <strong>IP :</strong> {ip}<br>
                🔌 <strong>Port :</strong> 8080
            </div>
            
            <div class="info">
                📋 <strong>Prochaine étape :</strong><br>
                Démarrer la version complète de PLANIFY
            </div>
            
            <a href="/test" class="btn">🧪 Test Navigation</a>
            
            <div style="margin-top: 30px; font-size: 14px; opacity: 0.8;">
                ✅ Connexion mobile validée<br>
                🎯 Prêt pour PLANIFY complet
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/test')
def test():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📱 Test Navigation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                text-align: center;
                padding: 20px;
                margin: 0;
            }
            .container {
                max-width: 400px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                margin: 10px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Navigation Test Réussi !</h1>
            <p>🎯 Votre téléphone navigue parfaitement.</p>
            <p>📱 L'interface mobile fonctionne correctement.</p>
            <a href="/" class="btn">🏠 Retour Accueil</a>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    local_ip = get_local_ip()
    
    print("📱 TEST CONNEXION MOBILE PLANIFY")
    print("=" * 40)
    print(f"🌐 Adresse IP : {local_ip}")
    print(f"🔌 Port : 8080")
    print()
    print(f"📲 URL POUR VOTRE TÉLÉPHONE :")
    print(f"   http://{local_ip}:8080")
    print()
    print("📋 ÉTAPES :")
    print("   1. Connectez votre téléphone au même WiFi")
    print("   2. Ouvrez le navigateur mobile")
    print(f"   3. Tapez : http://{local_ip}:8080")
    print("   4. Testez la navigation")
    print()
    print("🔥 Si ce test fonctionne, PLANIFY fonctionnera aussi !")
    print("=" * 40)
    
    try:
        app.run(debug=False, host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("💡 Essayez un autre port ou redémarrez en tant qu'administrateur")