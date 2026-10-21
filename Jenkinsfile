pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\Duraimurugan T\\AppData\\Local\\Programs\\Python\\Python314\\python.exe'
        DOCKER = 'C:\\Users\\Duraimurugan T\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'

        IMAGE_NAME = 'student-management-finalyear'
        CONTAINER_NAME = 'student-management-finalyear'
        APP_PORT = '5001'

        DATABASE_CONTAINER = 'studentmanagement-devops-finalyear-db-1'
        DOCKER_NETWORK = 'studentmanagement-devops-finalyear_default'
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

$docker = $env:DOCKER
$image = "$($env:IMAGE_NAME):$($env:BUILD_NUMBER)"

Write-Host "Starting Docker deployment..."
Write-Host "Image: $image"

# Check Docker network
& $docker network inspect $env:DOCKER_NETWORK *> $null

if ($LASTEXITCODE -ne 0) {
    throw "Docker network not found."
}

# Check database container
& $docker inspect $env:DATABASE_CONTAINER *> $null

if ($LASTEXITCODE -ne 0) {
    throw "Database container not found."
}

# Check database is running
$dbRunning = & $docker inspect `
    --format '{{.State.Running}}' `
    $env:DATABASE_CONTAINER

if ($dbRunning -ne "true") {
    throw "Database container is not running."
}

# Check existing application container safely
$existingContainer = & $docker ps -a `
    --filter "name=^/$($env:CONTAINER_NAME)$" `
    --format "{{.Names}}"

if ($LASTEXITCODE -ne 0) {
    throw "Unable to check Docker containers."
}

if ($existingContainer -eq $env:CONTAINER_NAME) {

    Write-Host "Removing old application container..."

    & $docker rm -f $env:CONTAINER_NAME

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to remove old container."
    }

} else {
    Write-Host "No existing container found. Creating new container..."
}

# Deploy application
Write-Host "Creating new application container..."

& $docker run -d `
    --name $env:CONTAINER_NAME `
    --restart unless-stopped `
    --network $env:DOCKER_NETWORK `
    -p "$($env:APP_PORT):5000" `
    -e "SECRET_KEY=$env:APP_SECRET_KEY" `
    -e "POSTGRES_USER=postgres" `
    -e "POSTGRES_PASSWORD=$env:DB_PASSWORD" `
    -e "POSTGRES_DB=student_management" `
    -e "POSTGRES_HOST=$env:DATABASE_CONTAINER" `
    -e "POSTGRES_PORT=5432" `
    $image

if ($LASTEXITCODE -ne 0) {
    throw "Docker container deployment failed."
}

Write-Host "Docker container created successfully."
'''
                }
            }
        }

        stage('Deployment Health Check') {
            steps {
                powershell '''
$ErrorActionPreference = "Stop"

$docker = $env:DOCKER
$healthy = $false

Write-Host "Checking application health..."

for ($i = 1; $i -le 12; $i++) {

    try {

        $response = Invoke-RestMethod `
            -Uri "http://localhost:$($env:APP_PORT)/health" `
            -TimeoutSec 5

        if (
            $response.status -eq "healthy" -and
            $response.database -eq "connected"
        ) {
            $healthy = $true
            break
        }

    }
    catch {
        Write-Host "Application not ready. Attempt $i of 12."
    }

    Start-Sleep -Seconds 5
}

if (-not $healthy) {

    Write-Host "Application health check failed."

    & $docker logs $env:CONTAINER_NAME

    throw "Deployment health check failed."
}

Write-Host "Application health check passed."
'''
            }
        }
    }

    post {

        success {
            echo 'SUCCESS: All tests passed.'
            echo 'SUCCESS: Docker image built.'
            echo 'SUCCESS: Application deployed.'
            echo 'SUCCESS: Health check passed.'
        }

        failure {
            echo 'FAILED: Check Jenkins Console Output.'
        }

        always {
            echo 'Jenkins pipeline completed.'
        }
    }
}