pipeline {
    agent any

environment {
    PYTHON = 'C:\\Users\\Duraimurugan T\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
    DOCKER = 'C:\\Users\\Duraimurugan T\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
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

        stage('Check Python and Docker') {
    steps {
        bat '"%PYTHON%" --version'
        bat '"%DOCKER%" version'
    }
}

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install --upgrade pip'
                bat '"%PYTHON%" -m pip install -r requirements.txt'
                bat '"%PYTHON%" -m pip install -r requirements-dev.txt'
            }
        }

        stage('Automated Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                
bat '"%DOCKER%" build -t %IMAGE_NAME%:%BUILD_NUMBER% .'

            }
        }

        stage('Deploy Container') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'POSTGRES_PASSWORD',
                        variable: 'DB_PASSWORD'
                    ),
                    string(
                        credentialsId: 'APP_SECRET_KEY',
                        variable: 'APP_SECRET_KEY'
                    )
                ]) {
                    powershell '''
                    $ErrorActionPreference = "Stop"

                    docker rm -f $env:CONTAINER_NAME 2>$null
                    $LASTEXITCODE = 0

                    docker run -d `
                      --name $env:CONTAINER_NAME `
                      --restart unless-stopped `
                      --network studentmanagement-devops-finalyear_default `
                      -p "$($env:APP_PORT):5000" `
                      -e "SECRET_KEY=$env:APP_SECRET_KEY" `
                      -e "POSTGRES_USER=postgres" `
                      -e "POSTGRES_PASSWORD=$env:DB_PASSWORD" `
                      -e "POSTGRES_DB=student_management" `
                      -e "POSTGRES_HOST=$env:DATABASE_CONTAINER" `
                      -e "POSTGRES_PORT=5432" `
                      "$($env:IMAGE_NAME):$($env:BUILD_NUMBER)"

                    if ($LASTEXITCODE -ne 0) {
                        throw "Docker deployment failed."
                    }

                    Write-Host "Deployment container started."
                    '''
                }
            }
        }

        stage('Deployment Health Check') {
            steps {
                powershell '''
                $healthy = $false

                for ($i = 0; $i -lt 12; $i++) {
                    try {
                        $response = Invoke-RestMethod `
                            -Uri "http://localhost:$env:APP_PORT/health" `
                            -TimeoutSec 5

                        if ($response.status -eq "healthy") {
                            $healthy = $true
                            break
                        }
                    }
                    catch {
                        Write-Host "Waiting for application health check..."
                        Start-Sleep -Seconds 5
                    }
                }

                if (-not $healthy) {
                    docker logs $env:CONTAINER_NAME
                    throw "Deployment health check failed."
                }

                Write-Host "Application health check passed."
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Tests passed, Docker image built, and deployment health check passed.'
        }

        failure {
            echo 'FAILED: Check Console Output for the exact error.'
        }

        always {
            echo 'Jenkins pipeline completed.'
        }
    }
}