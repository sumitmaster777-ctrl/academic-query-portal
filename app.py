
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///academic_queries.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Database model
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


# Student portal
@app.route("/")
def home():
    return render_template("index.html")


# Teacher dashboard
@app.route("/teacher")
def teacher():
    return render_template("teacher.html")


# API: Submit a query
@app.route("/api/queries", methods=["POST"])
def submit_query():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    required_fields = [
        "studentName",
        "email",
        "course",
        "category",
        "description"
    ]

    for field in required_fields:
        if not data.get(field) or not str(data[field]).strip():
            return jsonify({"error": f"{field} is required"}), 400

    query = Query(
        query_id="Q" + str(int(datetime.now().timestamp() * 1000)),
        student_name=data["studentName"].strip(),
        email=data["email"].strip(),
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


# API: Retrieve all queries
@app.route("/api/queries", methods=["GET"])
def get_queries():
    queries = Query.query.order_by(
        Query.submitted_at.desc()
    ).all()

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
# API: Update query status
@app.route("/api/queries/<string:query_id>", methods=["PUT"])
def update_query_status(query_id):
    data = request.get_json()

    if not data or data.get("status") not in [
        "Pending",
        "In Progress",
        "Resolved"
    ]:
        return jsonify({"error": "Invalid status"}), 400

    query = Query.query.filter_by(query_id=query_id).first()

    if query is None:
        return jsonify({"error": "Query not found"}), 404

    query.status = data["status"]
    db.session.commit()

    return jsonify({"message": "Query status updated successfully"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
