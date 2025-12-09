from flask import Flask, jsonify, request, render_template
import json
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# DATA_FILE = "data.json"

# def load_data():
#     if os.path.exists(DATA_FILE):
#         try:
#             with open(DATA_FILE, "r") as f:
#                 content = f.read().strip()
#                 if not content:
#                     return {} 
#                 return json.loads(content)
#         except json.JSONDecodeError:
#             return {}
#     return {}

# def save_data(data):
#     with open(DATA_FILE, "w") as f:
#         json.dump(data, f, indent=2)

# students = load_data()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'students.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    grade = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {"name": self.name, "grade": self.grade}
    
with app.app_context(): db.create_all()

@app.route("/")
def index():
    return render_template("grades.html")

@app.route("/grades", methods=["GET"])
def get_all_grades():
    students = Student.query.all()
    return jsonify({s.name: s.grade for s in students})

@app.route("/grades/<name>", methods=["GET"])
def get_grade(name):
    student = Student.query.filter_by(name = name).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student.to_dict())

@app.route("/grades", methods=["POST"])
def add_student():
    data = request.get_json()
    name = data.get("name")
    grade = data.get("grade")
    if not name or grade is None:
        return jsonify({"error": "Missing name or grade"}), 400
    
    if Student.query.filter_by(name = name).first():
        return jsonify({"error": "Student already exists"}), 400

    new_student = Student(name = name, grade = float(grade))
    db.session.add(new_student)
    db.session.commit()

    return jsonify({"message": f"Added {name}"}), 201

@app.route("/grades/<name>", methods=["PUT"])
def update_grade(name):
    student = Student.query.filter_by(name = name).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()
    grade = data.get("grade")
    if grade is None:
        return jsonify({"error": "Missing grade"}), 400

    student.grade = float(grade)
    db.session.commit()
    return jsonify({"message": f"Updated {name}"}), 200

@app.route("/grades/<name>", methods=["DELETE"])
def delete_student(name):
    student = Student.query.filter_by(name = name).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": f"Deleted {name}"}), 200

if __name__ == "__main__":
    app.run(debug=True)