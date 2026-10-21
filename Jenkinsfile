
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'student-management-finalyear'
        CONTAINER_NAME = 'student-management-finalyear'
        APP_PORT = '5001'
        DATABASE_CONTAINER = 'studentmanagement-devops-finalyear-db-1'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
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
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .'
            }
        }

        stage('Deploy Container') {
            steps {
                script {
                    bat '''
                    docker rm -f %CONTAINER_NAME% 2>NUL
                    if errorlevel 1 exit /b 0
                    '''

                    bat '''
                    docker run -d ^
                      --name %CONTAINER_NAME% ^
                      --restart unless-stopped ^
                      --network studentmanagement-devops-finalyear_default ^
                      -p %APP_PORT%:5000 ^
                      -e SECRET_KEY=jenkins-demo-change-this-secret ^
                      -e POSTGRES_USER=postgres ^
                      -e POSTGRES_PASSWORD="%POSTGRES_PASSWORD%" ^
                      -e POSTGRES_DB=student_management ^
                      -e POSTGRES_HOST=%DATABASE_CONTAINER% ^
                      -e POSTGRES_PORT=5432 ^
                      %IMAGE_NAME%:%BUILD_NUMBER%
                    '''
                }
            }
        }

        stage('Deployment Health Check') {
            steps {
                bat '''
                powershell -NoProfile -Command "$ok = $false; for ($i = 0; $i -lt 12; $i++) { try { $r = Invoke-RestMethod -Uri 'http://localhost:5001/health' -TimeoutSec 3; if ($r.status -eq 'healthy') { $ok = $true; break } } catch { Start-Sleep -Seconds 5 } }; if (-not $ok) { docker logs %CONTAINER_NAME%; exit 1 }"
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed, Docker image built, and deployment health check passed.'
        }

        failure {
            echo 'FAILED: Check Console Output and Docker logs.'
        }

        always {
            echo 'Jenkins pipeline completed.'
        }
    }
}
