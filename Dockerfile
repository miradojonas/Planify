# Dockerfile
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Variables d'environnement pour Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0

# Exposer le port interne du conteneur
EXPOSE 5000

# Commande pour démarrer Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]