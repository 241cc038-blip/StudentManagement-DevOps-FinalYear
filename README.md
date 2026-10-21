# StudentOps — Student Management with Automated CI/CD

Final-year BSc IT portfolio project demonstrating a Flask web application, PostgreSQL persistence, role-based access, automated tests, Docker packaging and a Jenkins pipeline.

## Features
- User registration and login; passwords are stored as hashes.
- Administrator-only student create, edit and delete operations.
- Student search by name, register number, email or department.
- PostgreSQL database with Docker Compose.
- Health endpoint at `/health`.
- Pytest suite and Jenkins pipeline.
- Docker image build and local container deployment.

## Prerequisites
- Python 3.12+
- Docker Desktop with Linux containers / Docker Compose
- Git
- Jenkins (optional for local run; needed for CI/CD demo)

## Run with Docker Compose (recommended)
1. Open PowerShell in the project folder.
2. Copy `.env.example` to `.env` and replace the sample secrets with strong values.
3. Start the application and PostgreSQL:

   ```powershell
   docker compose up --build -d
   docker compose ps
   ```

4. Open `http://localhost:5000`.
5. Create a user through Register. The configured admin account is created from `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables on first startup. For the compose defaults, change these values in `.env` before running.

Health check: `http://localhost:5000/health`.

## Run tests locally
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

Tests use an isolated in-memory SQLite database. The application uses PostgreSQL when started with Docker Compose.

## Jenkins setup
Create a Pipeline job configured as **Pipeline script from SCM**, choose Git, enter the repository URL, set branch `*/main`, and script path `Jenkinsfile`. The Jenkins Windows agent needs Python, Git, Docker CLI and permission to access the Docker engine. This example pipeline deploys a standalone container for CI/CD demonstration; for a persistent PostgreSQL deployment, use Docker Compose as a separately configured deployment stage.

## Security notes
- Change all example secrets before running beyond a local demo.
- This is an academic portfolio starter, not a production-hardened system. Add CSRF protection, rate limiting, secure cookie settings, database migrations, audit logging, backups and HTTPS before production use.
- The initial administrator account is provisioned only when both admin environment variables are set and no admin account exists.

## Suggested resume entry
**StudentOps — Student Management System with CI/CD**  
Built a Flask-based student records platform with PostgreSQL persistence, hashed-password authentication, role-based authorization, search and CRUD workflows. Containerized the app with Docker and configured Jenkins to run automated Pytest checks, build an image and deploy a local container.

Only list tools and features you personally run, verify and understand during your project demonstration.
