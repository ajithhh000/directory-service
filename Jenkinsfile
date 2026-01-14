pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        APP_NAME = 'employee-directory'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out code from GitHub...'
                checkout scm
            }
        }
        
        stage('Environment Check') {
            steps {
                echo '🔍 Checking environment...'
                sh '''
                    echo "Docker version:"
                    docker --version
                    echo "Docker Compose version:"
                    docker compose version
                    echo "Current directory:"
                    pwd
                    echo "Files:"
                    ls -la
                '''
            }
        }
        
        stage('Stop Old Containers') {
            steps {
                echo '🛑 Stopping old containers...'
                sh '''
                    docker compose down || true
                '''
            }
        }
        
        stage('Clean Old Images') {
            steps {
                echo '🧹 Cleaning old Docker images...'
                sh '''
                    docker rmi employee-directory-app || true
                    docker system prune -f
                '''
            }
        }
        
        stage('Build Docker Images') {
            steps {
                echo '🔨 Building Docker images...'
                sh '''
                    docker compose build --no-cache
                '''
            }
        }
        
        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying application...'
                sh '''
                    docker compose up -d
                '''
            }
        }
        
        stage('Verify Deployment') {
            steps {
                echo '✅ Verifying deployment...'
                sh '''
                    echo "Waiting for containers to start..."
                    sleep 10
                    
                    echo "Container status:"
                    docker ps
                    
                    echo "Testing health endpoint:"
                    for i in {1..30}; do
                        if curl -f http://localhost:5000/health; then
                            echo "✅ Application is healthy!"
                            exit 0
                        fi
                        echo "Attempt $i/30 - waiting..."
                        sleep 2
                    done
                    
                    echo "❌ Health check failed"
                    docker compose logs app
                    exit 1
                '''
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo '🎉 Application deployed and running at http://localhost:5000'
        }
        failure {
            echo '❌ Pipeline failed!'
            sh 'docker compose logs'
        }
    }
}

