import os
from functools import wraps
from datetime import datetime
from urllib.parse import quote_plus

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    flash,
    render_template_string,
    jsonify,
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from werkzeug.security import generate_password_hash, check_password_hash


# --------------------------------------------------
# Extensions
# --------------------------------------------------

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


# --------------------------------------------------
# Database Models
# --------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student", nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    register_number = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


# --------------------------------------------------
# Base HTML Template
# --------------------------------------------------

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>{{ title }} - Student Management System</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f6fb;
            color: #253047;
        }

        nav {
            background: #182848;
            color: white;
            padding: 16px 6%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }

        nav a {
            color: white;
            text-decoration: none;
            margin-left: 14px;
        }

        nav a:hover {
            color: #87b5ff;
        }

        .container {
            max-width: 1050px;
            margin: 32px auto;
            padding: 24px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 18px #0000000d;
        }

        h1, h2 {
            color: #182848;
        }

        input, select {
            width: 100%;
            padding: 11px;
            margin: 6px 0 14px;
            border: 1px solid #ccd3df;
            border-radius: 6px;
        }

        input:focus {
            outline: none;
            border-color: #2457c5;
        }

        button, .btn {
            display: inline-block;
            background: #2457c5;
            color: white;
            padding: 10px 15px;
            border: 0;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            margin: 3px;
        }

        button:hover, .btn:hover {
            opacity: 0.9;
        }

        .danger {
            background: #c0392b;
        }

        .secondary {
            background: #566477;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 18px;
        }

        th, td {
            border-bottom: 1px solid #e4e8ef;
            padding: 11px;
            text-align: left;
        }

        th {
            background: #edf2fb;
        }

        .message {
            padding: 12px;
            background: #fff1c9;
            border-radius: 6px;
            margin: 10px 0;
        }

        .success {
            background: #dff6e7;
        }

        .cards {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .card {
            background: #edf2fb;
            padding: 18px;
            border-radius: 8px;
            flex: 1;
            min-width: 180px;
        }

        .table-container {
            overflow-x: auto;
        }

        footer {
            text-align: center;
            color: #667085;
            padding: 20px;
        }

        @media (max-width: 650px) {
            .container {
                margin: 12px;
                padding: 16px;
            }

            nav {
                padding: 14px;
            }

            nav a {
                margin-left: 6px;
            }
        }
    </style>
</head>

<body>

<nav>
    <strong>Student Management System</strong>

    <div>
        <a href="{{ url_for('home') }}">Home</a>

        {% if current_user.is_authenticated %}
            <a href="{{ url_for('dashboard') }}">Dashboard</a>

            {% if current_user.role == 'admin' %}
                <a href="{{ url_for('students') }}">Students</a>
            {% endif %}

            <a href="{{ url_for('logout') }}">Logout</a>

        {% else %}
            <a href="{{ url_for('login') }}">Login</a>
            <a href="{{ url_for('register') }}">Register</a>
        {% endif %}
    </div>
</nav>

<main class="container">

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% for category, message in messages %}
            <div class="message {{ 'success' if category == 'success' else '' }}">
                {{ message }}
            </div>
        {% endfor %}
    {% endwith %}

    {{ content|safe }}

</main>

<footer>
    Student Management System | Flask + SQLAlchemy + Docker + Jenkins
</footer>

</body>
</html>
"""


# --------------------------------------------------
# Render Page Function
# --------------------------------------------------

def render_page(page_title, content, **context):
    page_content = render_template_string(
        content,
        **context
    )

    return render_template_string(
        BASE_TEMPLATE,
        title=page_title,
        content=page_content
    )


# --------------------------------------------------
# Application Factory
# --------------------------------------------------

def create_app(test_config=None):

    app = Flask(__name__)

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        db_user = os.environ.get("POSTGRES_USER", "postgres")
        db_password = os.environ.get("POSTGRES_PASSWORD", "")
        db_host = os.environ.get("POSTGRES_HOST", "db")
        db_port = os.environ.get("POSTGRES_PORT", "5432")
        db_name = os.environ.get("POSTGRES_DB", "student_management")

        if db_password:
            database_url = (
                f"postgresql+psycopg2://{quote_plus(db_user)}:"
                f"{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}"
            )
        else:
            database_url = "sqlite:///student_management.db"

    app.config.update(
        SECRET_KEY=os.environ.get(
            "SECRET_KEY",
            "development-only-change-me"
        ),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    app.User = User
    app.Student = Student

    # --------------------------------------------------
    # Admin Access Control
    # --------------------------------------------------

    def admin_required(view_function):
        @wraps(view_function)
        @login_required
        def wrapped_view(*args, **kwargs):
            if current_user.role != "admin":
                return "Forbidden: administrator access required", 403

            return view_function(*args, **kwargs)

        return wrapped_view

    # --------------------------------------------------
    # Home Page
    # --------------------------------------------------

    @app.route("/")
    def home():
        content = """
        <h1>Student Management System</h1>

        <p>
    <a class="btn" href="{{ url_for('students') }}">
        Manage Students
    </a>

    <a class="btn" href="{{ url_for('users') }}">
        Registered Users
    </a>
</p>
        <div class="cards">
            <div class="card">
                <h3>Student Records</h3>
                <p>Add, view and update student information.</p>
            </div>

            <div class="card">
                <h3>Secure Login</h3>
                <p>Access features based on your user role.</p>
            </div>

            <div class="card">
                <h3>DevOps Ready</h3>
                <p>Designed for testing, Docker and Jenkins CI.</p>
            </div>
        </div>

        <p>
            <a class="btn" href="{{ url_for('login') }}">Login</a>
            <a class="btn secondary" href="{{ url_for('register') }}">
                Create Account
            </a>
        </p>
        """

        return render_page("Home", content)

    # --------------------------------------------------
    # Health Check
    # --------------------------------------------------

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify(
                status="healthy",
                database="connected"
            ), 200

        except Exception:
            db.session.rollback()
            return jsonify(
                status="unhealthy",
                database="disconnected"
            ), 503

    # --------------------------------------------------
    # Register
    # --------------------------------------------------

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            if not username or not password:
                flash("Username and password are required.", "warning")

            elif len(password) < 8:
                flash("Password must contain at least 8 characters.", "warning")

            elif User.query.filter_by(username=username).first():
                flash("That username is already registered.", "warning")

            else:
                user = User(username=username, role="student")
                user.set_password(password)

                db.session.add(user)
                db.session.commit()

                flash(
                    "Account created successfully. Please log in.",
                    "success"
                )
                return redirect(url_for("login"))

        content = """
        <h1>Register</h1>

        <form method="post">
            <label>Username</label>
            <input name="username" required maxlength="80">

            <label>Password (minimum 8 characters)</label>
            <input type="password" name="password" required minlength="8">

            <button type="submit">Register</button>
        </form>

        <p>
            Already have an account?
            <a href="{{ url_for('login') }}">Login</a>
        </p>
        """

        return render_page("Register", content)

    # --------------------------------------------------
    # Login
    # --------------------------------------------------

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                flash("Login successful.", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid username or password.", "warning")

        content = """
        <h1>Login</h1>

        <form method="post">
            <label>Username</label>
            <input name="username" required>

            <label>Password</label>
            <input type="password" name="password" required>

            <button type="submit">Login</button>
        </form>

        <p>
            New user?
            <a href="{{ url_for('register') }}">Register here</a>
        </p>
        """

        return render_page("Login", content)

    # --------------------------------------------------
    # Logout
    # --------------------------------------------------

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have logged out.", "success")
        return redirect(url_for("home"))

    # --------------------------------------------------
    # Dashboard
    # --------------------------------------------------

    @app.route("/dashboard")
    @login_required
    def dashboard():
        student_count = Student.query.count()

        content = """
        <h1>Dashboard</h1>

        <p>Welcome, <strong>{{ current_user.username }}</strong>!</p>
        <p>Role: {{ current_user.role|title }}</p>

        {% if current_user.role == 'admin' %}
            <div class="cards">
                <div class="card">
                    <h2>{{ student_count }}</h2>
                    <p>Total student records</p>
                </div>
            </div>

            <p>
                <a class="btn" href="{{ url_for('students') }}">
                    Manage Students
                </a>
            </p>
        {% else %}
            <p>
                You are logged in as a student.
                Contact an administrator if you need record-management access.
            </p>
        {% endif %}
        """

        return render_page(
            "Dashboard",
            content,
            student_count=student_count
        )

    # --------------------------------------------------
    # View Students
    # --------------------------------------------------

    @app.route("/students")
    @admin_required
    def students():
        records = Student.query.order_by(Student.id.desc()).all()

        content = """
        <h1>Student Records</h1>

        <p>
            <a class="btn" href="{{ url_for('add_student') }}">
                Add Student
            </a>
        </p>

        {% if records %}
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Register No.</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Department</th>
                        <th>Year</th>
                        <th>Phone</th>
                        <th>Actions</th>
                    </tr>
                </thead>

                <tbody>
                    {% for student in records %}
                    <tr>
                        <td>{{ student.register_number }}</td>
                        <td>{{ student.full_name }}</td>
                        <td>{{ student.email }}</td>
                        <td>{{ student.department }}</td>
                        <td>{{ student.year }}</td>
                        <td>{{ student.phone }}</td>

                        <td>
                            <a
                                class="btn"
                                href="{{ url_for('edit_student', student_id=student.id) }}"
                            >
                                Edit
                            </a>

                            <form
                                method="post"
                                action="{{ url_for('delete_student', student_id=student.id) }}"
                                style="display:inline"
                            >
                                <button
                                    class="danger"
                                    type="submit"
                                    onclick="return confirm('Delete this student?')"
                                >
                                    Delete
                                </button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
            <p>No student records found.</p>
        {% endif %}
        """

        return render_page("Students", content, records=records)

    # --------------------------------------------------
    # Add Student
    # --------------------------------------------------

    @app.route("/students/add", methods=["GET", "POST"])
    @admin_required
    def add_student():
        if request.method == "POST":
            register_number = request.form.get("register_number", "").strip()
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            department = request.form.get("department", "").strip()
            year = request.form.get("year", "").strip()
            phone = request.form.get("phone", "").strip()

            if not all([
                register_number,
                full_name,
                email,
                department,
                year,
                phone
            ]):
                flash("Please fill in all fields.", "warning")

            elif Student.query.filter_by(
                register_number=register_number
            ).first():
                flash("That register number already exists.", "warning")

            else:
                student = Student(
                    register_number=register_number,
                    full_name=full_name,
                    email=email,
                    department=department,
                    year=year,
                    phone=phone,
                )

                db.session.add(student)
                db.session.commit()

                flash("Student added successfully.", "success")
                return redirect(url_for("students"))

        return render_student_form("Add Student")

    # --------------------------------------------------
    # Edit Student
    # --------------------------------------------------

    @app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
    @admin_required
    def edit_student(student_id):
        student = db.get_or_404(Student, student_id)

        if request.method == "POST":
            fields = [
                "register_number",
                "full_name",
                "email",
                "department",
                "year",
                "phone",
            ]

            values = {
                field: request.form.get(field, "").strip()
                for field in fields
            }

            duplicate = Student.query.filter(
                Student.register_number == values["register_number"],
                Student.id != student.id,
            ).first()

            if not all(values.values()):
                flash("Please fill in all fields.", "warning")

            elif duplicate:
                flash("That register number is already in use.", "warning")

            else:
                for field, value in values.items():
                    setattr(student, field, value)

                db.session.commit()

                flash("Student updated successfully.", "success")
                return redirect(url_for("students"))

        return render_student_form("Edit Student", student)

    # --------------------------------------------------
    # Delete Student
    # --------------------------------------------------

    @app.route("/students/<int:student_id>/delete", methods=["POST"])
    @admin_required
    def delete_student(student_id):
        student = db.get_or_404(Student, student_id)

        db.session.delete(student)
        db.session.commit()

        flash("Student deleted successfully.", "success")
        return redirect(url_for("students"))

    # --------------------------------------------------
    # Add / Edit Student Form
    # --------------------------------------------------

    def render_student_form(title, student=None):
        if student is None:
            student = Student(
                register_number="",
                full_name="",
                email="",
                department="",
                year="",
                phone="",
            )

        content = """
        <h1>{{ title }}</h1>

        <form method="post">
            <label>Register Number</label>
            <input
                name="register_number"
                value="{{ student.register_number }}"
                required
            >

            <label>Full Name</label>
            <input
                name="full_name"
                value="{{ student.full_name }}"
                required
            >

            <label>Email</label>
            <input
                type="email"
                name="email"
                value="{{ student.email }}"
                required
            >

            <label>Department</label>
            <input
                name="department"
                value="{{ student.department }}"
                required
            >

            <label>Year</label>
            <input
                name="year"
                value="{{ student.year }}"
                required
            >

            <label>Phone</label>
            <input
                name="phone"
                value="{{ student.phone }}"
                required
            >

            <button type="submit">Save</button>

            <a
                class="btn secondary"
                href="{{ url_for('students') }}"
            >
                Cancel
            </a>
        </form>
        """

        # FIX: This return is INSIDE render_student_form()
        return render_page(
            title,
            content,
            title=title,
            student=student
        )
    # --------------------------------------------------
    # Registered Users - Admin Only
    # --------------------------------------------------

    @app.route("/users")
    @admin_required
    def users():
        registered_users = User.query.order_by(User.id).all()

        content = """
        <h1>Registered Users</h1>

        <table>
            <thead>
                <tr>
                    <th>User ID</th>
                    <th>Username</th>
                    <th>Role</th>
                </tr>
            </thead>

            <tbody>
                {% for user in registered_users %}
                <tr>
                    <td>{{ user.id }}</td>
                    <td>{{ user.username }}</td>
                    <td>{{ user.role }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <br>
        <a class="btn" href="{{ url_for('dashboard') }}">
            Back to Dashboard
        </a>
        """

        return render_page(
            "Registered Users",
            content,
            registered_users=registered_users
        )
    # --------------------------------------------------
    # Create Database Tables
    # --------------------------------------------------

    if not app.config.get("TESTING"):
        with app.app_context():
            db.create_all()

    return app


# --------------------------------------------------
# Run Locally
# --------------------------------------------------

app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )