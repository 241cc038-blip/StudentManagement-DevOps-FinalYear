import pytest
from app import create_app, db

@pytest.fixture()
def app():
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test-only-secret",
    })
    with test_app.app_context():
        db.drop_all()
        db.create_all()
        admin = test_app.User(username="admin", role="admin")
        admin.set_password("TestPassword123")
        db.session.add(admin)
        db.session.commit()
    yield test_app
    with test_app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()

def login_admin(client):
    return client.post("/login", data={
        "username": "admin", "password": "TestPassword123"
    }, follow_redirects=True)

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Management" in response.data

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"

def test_register_and_login(client):
    response = client.post("/register", data={
        "username": "student01", "password": "StrongPass123"
    }, follow_redirects=True)
    assert response.status_code == 200
    response = client.post("/login", data={
        "username": "student01", "password": "StrongPass123"
    }, follow_redirects=True)
    assert b"Dashboard" in response.data

def test_admin_can_add_student(client, app):
    login_admin(client)
    response = client.post("/students/add", data={
        "register_number": "IT001",
        "full_name": "Abirami",
        "email": "abirami@example.com",
        "department": "BSc IT",
        "year": "III Year",
        "phone": "9000000000"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Abirami" in response.data

def test_student_cannot_open_admin_add_form(client):
    client.post("/register", data={
        "username": "student01", "password": "StrongPass123"
    })
    client.post("/login", data={
        "username": "student01", "password": "StrongPass123"
    })
    response = client.get("/students/add")
    assert response.status_code == 403
