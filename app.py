
import json
import os
import webbrowser
from threading import Timer

from flask import Flask, jsonify, render_template, request
from ai_helper import analyze_performance, generate_study_tips, AIConfigurationError, AIServiceError

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), "students.json")


def load_students():
    """Load saved records. If the file is missing or invalid, start with an empty list."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError):
        app.logger.exception("Could not read students.json")
        return []


def save_students(students):
    """Write records safely using UTF-8 and readable JSON indentation."""
    temp_file = DATA_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(students, file, indent=2, ensure_ascii=False)
    os.replace(temp_file, DATA_FILE)


students = load_students()


def calculate_result(marks):
    total = sum(marks.values())
    average = round(total / len(marks), 2) if marks else 0
    if average >= 85:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 50:
        grade = "D"
    else:
        grade = "F"
    return total, average, grade


def validate_payload(data, existing_id=None):
    if not isinstance(data, dict):
        raise ValueError("Please submit valid student information.")

    student_id = str(data.get("id", "")).strip()
    name = str(data.get("name", "")).strip()
    student_class = str(data.get("class", "")).strip()
    subjects = data.get("subjects", [])
    marks_list = data.get("marks", [])

    if not student_id or not name or not student_class:
        raise ValueError("Student ID, name, and class/semester are required.")
    if not isinstance(subjects, list) or not isinstance(marks_list, list):
        raise ValueError("Subjects and marks must be provided as lists.")
    if not subjects or len(subjects) != len(marks_list):
        raise ValueError("Enter the same number of subject names and marks.")
    clean_subjects = [str(subject).strip() for subject in subjects]
    if any(not subject for subject in clean_subjects):
        raise ValueError("Subject names cannot be empty.")
    if len({subject.casefold() for subject in clean_subjects}) != len(clean_subjects):
        raise ValueError("Subject names must not be duplicated.")

    marks = {}
    for subject, raw_mark in zip(clean_subjects, marks_list):
        try:
            mark = float(raw_mark)
        except (TypeError, ValueError):
            raise ValueError(f"Marks for {subject} must be numeric.")
        if not 0 <= mark <= 100:
            raise ValueError(f"Marks for {subject} must be between 0 and 100.")
        marks[subject] = mark

    for student in students:
        if student["id"].casefold() == student_id.casefold() and student["id"] != existing_id:
            raise ValueError("This Student ID already exists.")

    total, average, grade = calculate_result(marks)
    return {
        "id": student_id,
        "name": name,
        "class": student_class,
        "marks": marks,
        "total": total,
        "average": average,
        "grade": grade,
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/students", methods=["GET"])
def get_students():
    return jsonify(students)


@app.route("/api/students", methods=["POST"])
def add_student():
    try:
        student = validate_payload(request.get_json(silent=True))
        students.append(student)
        save_students(students)
        return jsonify({"message": "Student added successfully.", "student": student}), 201
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except OSError:
        app.logger.exception("Could not save student record")
        return jsonify({"error": "Could not save records. Check folder permissions."}), 500


@app.route("/api/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    existing = next((item for item in students if item["id"] == student_id), None)
    if existing is None:
        return jsonify({"error": "Student not found."}), 404
    try:
        data = request.get_json(silent=True) or {}
        data["id"] = student_id  # Student ID is fixed during updates.
        updated = validate_payload(data, existing_id=student_id)
        existing.update(updated)
        save_students(students)
        return jsonify({"message": "Student updated successfully.", "student": existing})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except OSError:
        app.logger.exception("Could not save updated record")
        return jsonify({"error": "Could not save the updated record."}), 500


@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    existing = next((item for item in students if item["id"] == student_id), None)
    if existing is None:
        return jsonify({"error": "Student not found."}), 404
    students.remove(existing)
    try:
        save_students(students)
    except OSError:
        students.append(existing)
        app.logger.exception("Could not save after deletion")
        return jsonify({"error": "Could not save the deletion."}), 500
    return jsonify({"message": "Student deleted successfully."})


@app.route("/api/ai/<kind>/<student_id>", methods=["POST"])
def student_ai(kind, student_id):
    student = next((item for item in students if item["id"] == student_id), None)
    if student is None:
        return jsonify({"error": "Student not found."}), 404
    if kind not in ("analyze", "tips"):
        return jsonify({"error": "Unsupported AI request. Use analyze or tips."}), 400
    try:
        result = analyze_performance(student) if kind == "analyze" else generate_study_tips(student)
        return jsonify({"result": result})
    except AIConfigurationError as error:
        return jsonify({"error": str(error)}), 503
    except AIServiceError as error:
        return jsonify({"error": str(error)}), 502
    except Exception:
        app.logger.exception("Unexpected AI error")
        return jsonify({"error": "An unexpected AI error occurred. Please try again."}), 500


if __name__ == "__main__":
    # Open Chrome shortly after Flask starts. If Chrome is unavailable, open the default browser.
    def open_browser():
        try:
            webbrowser.get("google-chrome").open("http://127.0.0.1:5000")
        except webbrowser.Error:
            webbrowser.open("http://127.0.0.1:5000")

    Timer(1.2, open_browser).start()
    app.run(debug=True)
