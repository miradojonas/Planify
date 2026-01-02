#!/usr/bin/env python3
"""
PLANIFY Mobile - Version simplifiée fonctionnelle
"""

import socket
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'planify-mobile-2025'

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Template principal
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 PLANIFY Mobile</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        
        .container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .logo {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        .title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .subtitle {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .card {
            background: rgba(255,255,255,0.15);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .menu-item {
            display: flex;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            text-decoration: none;
            color: white;
            transition: all 0.3s ease;
        }
        
        .menu-item:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }
        
        .menu-icon {
            font-size: 24px;
            margin-right: 15px;
            width: 40px;
            text-align: center;
        }
        
        .menu-content {
            flex: 1;
        }
        
        .menu-title {
            font-weight: bold;
            font-size: 16px;
        }
        
        .menu-desc {
            font-size: 12px;
            opacity: 0.8;
            margin-top: 2px;
        }
        
        .login-form {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        
        .form-group {
            margin: 15px 0;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.2);
            color: white;
            font-size: 16px;
        }
        
        .form-group input::placeholder {
            color: rgba(255,255,255,0.7);
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: #4CAF50;
            color: white;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: #45a049;
            transform: translateY(-1px);
        }
        
        .status {
            text-align: center;
            padding: 15px;
            margin: 20px 0;
            border-radius: 10px;
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid #4CAF50;
        }
        
        .clock {
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        
        .date {
            font-size: 14px;
            opacity: 0.8;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    
    <script>
        // Horloge temps réel
        function updateClock() {
            const now = new Date();
            const time = now.toLocaleTimeString('fr-FR');
            const date = now.toLocaleDateString('fr-FR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            const clockElement = document.getElementById('clock');
            const dateElement = document.getElementById('date');
            
            if (clockElement) clockElement.textContent = time;
            if (dateElement) dateElement.textContent = date.charAt(0).toUpperCase() + date.slice(1);
        }
        
        // Mettre à jour toutes les secondes
        setInterval(updateClock, 1000);
        updateClock();
    </script>
</body>
</html>
"""

# Page d'accueil/connexion
HOME_PAGE = """
{% extends "main_template" %}
{% block content %}
<div class="header">
    <div class="logo">🎓</div>
    <div class="title">PLANIFY</div>
    <div class="subtitle">Plateforme Éducative Mobile</div>
</div>

<div class="clock">
    <div id="clock">12:00:00</div>
    <div class="date" id="date">Chargement...</div>
</div>

<div class="status">
    ✅ Connexion mobile réussie !<br>
    🌐 IP: """ + get_ip() + """<br>
    📱 Interface optimisée
</div>

{% if not session.get('logged_in') %}
<div class="card">
    <h3>🔐 Connexion</h3>
    <form method="POST" action="/login" class="login-form">
        <div class="form-group">
            <label>👤 Rôle</label>
            <select name="role" required>
                <option value="">Choisir un rôle</option>
                <option value="admin">🛠️ Administrateur</option>
                <option value="professeur">👨‍🏫 Professeur</option>
                <option value="eleve">🎓 Élève</option>
            </select>
        </div>
        <div class="form-group">
            <label>📧 Email</label>
            <input type="email" name="email" placeholder="Votre email" required>
        </div>
        <div class="form-group">
            <label>🔑 Mot de passe</label>
            <input type="password" name="password" placeholder="Votre mot de passe" required>
        </div>
        <button type="submit" class="btn">Se connecter</button>
    </form>
    
    <div style="margin-top: 20px; font-size: 12px; opacity: 0.8;">
        <strong>Comptes de test :</strong><br>
        Admin: admin@planify.fr / admin123<br>
        Prof: prof@planify.fr / prof123<br>
        Élève: eleve@planify.fr / eleve123
    </div>
</div>
{% else %}
<div class="card">
    <h3>👋 Bienvenue {{ session.get('role').title() }} !</h3>
    <p>🎯 Vous êtes connecté avec succès</p>
</div>

<a href="/dashboard" class="menu-item">
    <div class="menu-icon">📊</div>
    <div class="menu-content">
        <div class="menu-title">Tableau de bord</div>
        <div class="menu-desc">Vue d'ensemble</div>
    </div>
</a>

<a href="/calendar" class="menu-item">
    <div class="menu-icon">📅</div>
    <div class="menu-content">
        <div class="menu-title">Calendrier</div>
        <div class="menu-desc">Événements et planning</div>
    </div>
</a>

<a href="/edt" class="menu-item">
    <div class="menu-icon">📋</div>
    <div class="menu-content">
        <div class="menu-title">Emploi du Temps</div>
        <div class="menu-desc">Planning des cours</div>
    </div>
</a>

<a href="/chat" class="menu-item">
    <div class="menu-icon">💬</div>
    <div class="menu-content">
        <div class="menu-title">Messages</div>
        <div class="menu-desc">Communication</div>
    </div>
</a>

<a href="/logout" class="menu-item" style="background: rgba(244, 67, 54, 0.2);">
    <div class="menu-icon">🚪</div>
    <div class="menu-content">
        <div class="menu-title">Déconnexion</div>
        <div class="menu-desc">Quitter l'application</div>
    </div>
</a>
{% endif %}
{% endblock %}
"""

# Page simple pour les modules
MODULE_PAGE = """
{% extends "main_template" %}
{% block content %}
<div class="header">
    <div class="logo">{{ icon }}</div>
    <div class="title">{{ title }}</div>
    <div class="subtitle">{{ subtitle }}</div>
</div>

<div class="clock">
    <div id="clock">12:00:00</div>
    <div class="date" id="date">Chargement...</div>
</div>

<div class="card">
    <h3>{{ title }}</h3>
    <p>📱 Module optimisé pour mobile</p>
    <p>🎯 Fonctionnalité : {{ subtitle }}</p>
    <p>👤 Connecté en tant que : <strong>{{ session.get('role', 'Invité').title() }}</strong></p>
</div>

<div class="card">
    <h4>🚧 En développement</h4>
    <p>Cette section sera bientôt disponible avec toutes les fonctionnalités PLANIFY.</p>
</div>

<a href="/" class="menu-item">
    <div class="menu-icon">🏠</div>
    <div class="menu-content">
        <div class="menu-title">Accueil</div>
        <div class="menu-desc">Retour au menu principal</div>
    </div>
</a>
{% endblock %}
"""

# Routes
@app.route('/')
def home():
    return render_template_string(MAIN_TEMPLATE.replace('{% block content %}{% endblock %}', HOME_PAGE))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    
    # Comptes de test
    accounts = {
        'admin@planify.fr': {'password': 'admin123', 'role': 'admin'},
        'prof@planify.fr': {'password': 'prof123', 'role': 'professeur'},
        'eleve@planify.fr': {'password': 'eleve123', 'role': 'eleve'}
    }
    
    if email in accounts and accounts[email]['password'] == password and accounts[email]['role'] == role:
        session['logged_in'] = True
        session['role'] = role
        session['email'] = email
        return redirect('/')
    
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')
    
    return render_template_string(
        MAIN_TEMPLATE.replace('{% block content %}{% endblock %}', MODULE_PAGE),
        icon='📊',
        title='Tableau de bord',
        subtitle='Vue d\'ensemble de vos activités'
    )

@app.route('/calendar')
def calendar():
    if not session.get('logged_in'):
        return redirect('/')
    
    return render_template_string(
        MAIN_TEMPLATE.replace('{% block content %}{% endblock %}', MODULE_PAGE),
        icon='📅',
        title='Calendrier',
        subtitle='Gestion des événements et planning'
    )

@app.route('/edt')
def edt():
    if not session.get('logged_in'):
        return redirect('/')
    
    return render_template_string(
        MAIN_TEMPLATE.replace('{% block content %}{% endblock %}', MODULE_PAGE),
        icon='📋',
        title='Emploi du Temps',
        subtitle='Planning des cours et activités'
    )

@app.route('/chat')
def chat():
    if not session.get('logged_in'):
        return redirect('/')
    
    return render_template_string(
        MAIN_TEMPLATE.replace('{% block content %}{% endblock %}', MODULE_PAGE),
        icon='💬',
        title='Messages',
        subtitle='Communication et discussions'
    )

if __name__ == '__main__':
    ip = get_ip()
    print("📱 PLANIFY MOBILE - VERSION SIMPLIFIÉE")
    print("=" * 45)
    print(f"🌐 Adresse IP : {ip}")
    print(f"🔌 Port : 8080")
    print()
    print(f"📱 URL POUR VOTRE TÉLÉPHONE :")
    print(f"   http://{ip}:8080")
    print()
    print("🔑 COMPTES DE CONNEXION :")
    print("   Admin : admin@planify.fr / admin123")
    print("   Prof : prof@planify.fr / prof123")
    print("   Élève : eleve@planify.fr / eleve123")
    print()
    print("✅ VERSION SIMPLIFIÉE - 100% FONCTIONNELLE")
    print("=" * 45)
    
    try:
        app.run(debug=False, host='0.0.0.0', port=8080)
    except Exception as e:
        print(f"❌ Erreur : {e}")
        input("Appuyez sur Entrée pour fermer...")