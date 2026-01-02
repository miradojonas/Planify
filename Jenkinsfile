pipeline {
    agent any
    
    environment {
        APP_NAME = 'planify-app'
        IMAGE_NAME = 'planify-flask'
        CONTAINER_NAME = 'planify-container'
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
    }
    
    stages {
        stage('🧹 Nettoyage') {
            steps {
                echo 'Nettoyage de l\'environnement...'
                sh '''
                    docker-compose down || true
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                '''
            }
        }
        
        stage('📦 Installation des dépendances') {
            steps {
                echo 'Vérification des dépendances Python...'
                sh '''
                    if [ -f requirements.txt ]; then
                        echo "✅ requirements.txt trouvé"
                        cat requirements.txt
                    else
                        echo "❌ requirements.txt introuvable !"
                        exit 1
                    fi
                '''
            }
        }
        
        stage('🧪 Tests unitaires') {
            steps {
                echo 'Exécution des tests...'
                sh '''
                    # Tests basiques
                    echo "Tests ignorés pour le moment"
                    # Ajoutez vos tests ici
                    # python -m pytest tests/ || true
                '''
            }
        }
        
        stage('🐳 Build Docker Image') {
            steps {
                echo 'Construction de l\'image Docker avec Docker Compose...'
                sh '''
                    docker-compose build
                    docker images | grep planify || true
                '''
            }
        }
        
        stage('🚀 Déploiement avec Docker Compose') {
            steps {
                echo 'Démarrage des services avec Docker Compose...'
                sh '''
                    docker-compose up -d
                    sleep 10
                    docker-compose ps
                '''
            }
        }
        
        stage('✅ Health Check') {
            steps {
                echo 'Vérification que l\'application répond...'
                retry(3) {
                    sh '''
                        sleep 3
                        curl -f http://localhost:5001 || exit 1
                    '''
                }
            }
        }
        
        stage('📊 Logs et Status') {
            steps {
                echo 'Affichage des logs et statuts...'
                sh '''
                    echo "=== Conteneurs actifs ==="
                    docker ps
                    echo ""
                    echo "=== Logs récents ==="
                    docker-compose logs --tail=20
                '''
            }
        }
    }
    
    post {
        success {
            echo '''
            ✅ ========================================
            ✅ DÉPLOIEMENT RÉUSSI !
            ✅ ========================================
            ✅ Planify est déployé avec succès
            ✅ Accédez à : http://localhost:5001
            ✅ ========================================
            '''
        }
        failure {
            echo '''
            ❌ ========================================
            ❌ DÉPLOIEMENT ÉCHOUÉ !
            ❌ ========================================
            '''
            sh '''
                echo "Logs d'erreur :"
                docker-compose logs --tail=50
            '''
        }
        always {
            echo 'Statut final des conteneurs :'
            sh 'docker ps -a | grep planify || true'
        }
    }
}