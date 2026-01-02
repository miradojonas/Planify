#!/bin/bash

# Script pour configurer Jenkins avec Docker pour Planify

echo "🚀 Configuration de Jenkins pour Planify"

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    echo "Installez Docker avec: sudo apt install docker.io"
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    echo "Installez Docker Compose avec: sudo apt install docker-compose"
    exit 1
fi

echo -e "${BLUE}📦 Création du réseau Docker pour Jenkins...${NC}"
docker network create jenkins || true

echo -e "${BLUE}🐳 Lancement de Jenkins dans Docker...${NC}"
docker run -d \
  --name jenkins \
  --restart unless-stopped \
  --network jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

echo -e "${GREEN}✅ Jenkins est en cours de démarrage...${NC}"
echo ""
echo "📋 Instructions:"
echo "1. Attendez 30 secondes que Jenkins démarre"
echo "2. Accédez à http://localhost:8080"
echo "3. Récupérez le mot de passe initial avec:"
echo "   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword"
echo ""
echo "4. Installez les plugins recommandés, plus:"
echo "   - Docker Pipeline"
echo "   - Docker plugin"
echo ""
echo "5. Configurez les permissions Docker dans Jenkins:"
echo "   docker exec -u root jenkins chmod 666 /var/run/docker.sock"
echo ""
echo "📊 Pour voir les logs de Jenkins:"
echo "   docker logs -f jenkins"
echo ""
echo "🛑 Pour arrêter Jenkins:"
echo "   docker stop jenkins"
echo ""
echo "🔄 Pour redémarrer Jenkins:"
echo "   docker start jenkins"

# Attendre que Jenkins démarre
echo -e "${BLUE}⏳ Attente du démarrage de Jenkins (30s)...${NC}"
sleep 30

# Afficher le mot de passe initial
echo -e "${GREEN}🔑 Mot de passe initial de Jenkins:${NC}"
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "Jenkins démarre encore, réessayez dans quelques secondes"

# Configurer les permissions Docker
echo -e "${BLUE}🔧 Configuration des permissions Docker...${NC}"
docker exec -u root jenkins chmod 666 /var/run/docker.sock 2>/dev/null || true

echo -e "${GREEN}✨ Configuration terminée!${NC}"
