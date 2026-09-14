pipeline {
    agent any

    environment {
        IMAGE_NAME     = 'todo-api'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = 'todo-app-container'
        HOST_PORT      = '3000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    # Purana container (agar chal raha hai) rok kar hata dein
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true

                    # Naye image se naya container start karein
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${HOST_PORT}:3000 \
                        --restart unless-stopped \
                        ${IMAGE_NAME}:latest
                '''
            }
        }
    }

    post {
        success {
            echo "Deployed ${IMAGE_NAME}:${IMAGE_TAG} as ${CONTAINER_NAME} on port ${HOST_PORT}."
        }
        failure {
            echo "Build or deploy failed."
        }
        always {
            // Purani, ab-unused (dangling) images clean karein taake disk na bhare
            sh 'docker image prune -f || true'
        }
    }
}
