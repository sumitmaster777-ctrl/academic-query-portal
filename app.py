from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///academic_queries.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.String(50), unique=True, nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="Pending")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/teacher")
def teacher():
    return render_template("teacher.html")


if __name__ == "__main__":
    app.run(debug=True)