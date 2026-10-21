pipeline {
    agent any
    environment {
        IMAGE_NAME = 'student-management-finalyear'
        CONTAINER_NAME = 'student-management-finalyear'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements-dev.txt'
            }
        }
        stage('Automated Tests') {
            steps {
                bat 'python -m pytest -v'
            }
        }
        stage('Build Docker Image') {
            steps {
                bat 'docker build -t student-management-finalyear:%BUILD_NUMBER% .'
            }
        }
        stage('Deploy Container') {
            steps {
                bat 'docker rm -f %CONTAINER_NAME% 2>NUL || exit /b 0'
                bat 'docker run -d --name %CONTAINER_NAME% -p 5000:5000 -e SECRET_KEY=replace_this_for_real_deployment -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD=ChangeMe123! student-management-finalyear:%BUILD_NUMBER%'
            }
        }
    }
    post {
        success { echo 'Tests passed and the application container was deployed.' }
        failure { echo 'Pipeline failed. Review the stage logs in Console Output.' }
    }
}
