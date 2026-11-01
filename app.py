
import os
import re
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Application configuration
database_url = os.environ.get("DATABASE_URL")

if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )

app.config["SQLALCHEMY_DATABASE_URI"] = (
    database_url or "sqlite:///academic_queries.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Initialize CSRF protection and database
csrf = CSRFProtect(app)
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Query model
class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.String(50), unique=True, nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="Pending")
    submitted_at = db.Column(db.DateTime, default=db.func.now())


# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Load logged-in user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Student registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please complete all fields.")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("register"))

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email,
            role="student"
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("home"))

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.role == "teacher":
            return redirect(url_for("teacher"))

        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)

            if user.role == "teacher":
                return redirect(url_for("teacher"))

            return redirect(url_for("home"))

        flash("Invalid email or password.")

    return render_template("login.html")


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Student portal
@app.route("/")
@login_required
def home():
    if current_user.role != "student":
        return redirect(url_for("teacher"))

    return render_template("index.html")


# Teacher dashboard
@app.route("/teacher")
@login_required
def teacher():
    if current_user.role != "teacher":
        return redirect(url_for("home"))

    return render_template("teacher.html")


# Submit query
@app.route("/api/queries", methods=["POST"])
@login_required
def submit_query():
    if current_user.role != "student":
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    required_fields = [
        "studentName", "email", "course",
        "category", "description"
    ]

    for field in required_fields:
        if not data.get(field) or not str(data[field]).strip():
            return jsonify({"error": f"{field} is required"}), 400

    query = Query(
        query_id="Q" + str(int(datetime.now().timestamp() * 1000)),
        student_name=current_user.name,
        email=current_user.email,
        course=data["course"].strip(),
        category=data["category"].strip(),
        description=data["description"].strip()
    )

    db.session.add(query)
    db.session.commit()

    return jsonify({
        "message": "Query submitted successfully",
        "query_id": query.query_id
    }), 201


# Retrieve queries
@app.route("/api/queries", methods=["GET"])
@login_required
def get_queries():
    if current_user.role == "teacher":
        queries = Query.query.order_by(
            Query.submitted_at.desc()
        ).all()
    else:
        queries = Query.query.filter_by(
            email=current_user.email
        ).order_by(Query.submitted_at.desc()).all()

    result = []

    for query in queries:
        result.append({
            "id": query.query_id,
            "studentName": query.student_name,
            "email": query.email,
            "course": query.course,
            "category": query.category,
            "description": query.description,
            "status": query.status,
            "submittedAt": query.submitted_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

    return jsonify(result)


# Update query status
@app.route("/api/queries/<string:query_id>", methods=["PUT"])
@login_required
def update_query_status(query_id):
    if current_user.role != "teacher":
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    allowed_statuses = ["Pending", "In Progress", "Resolved"]

    if not data or data.get("status") not in allowed_statuses:
        return jsonify({"error": "Invalid status"}), 400

    query = Query.query.filter_by(query_id=query_id).first()

    if query is None:
        return jsonify({"error": "Query not found"}), 404

    query.status = data["status"]
    db.session.commit()

    return jsonify({
        "message": "Query status updated successfully"
    })


# Run application
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
