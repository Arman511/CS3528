"""
This module defines the User class which handles user authentication and session management.
"""

import uuid
from flask import jsonify, request, session
from pymongo import TEXT
import pandas as pd
from core import handlers
from opportunities.models import Opportunity


class Student:
    """Student class."""

    def search_students(self, query):
        """Searching students."""
        from app import DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all_by_list_query("students", query)

        if students:
            return jsonify(students), 200

        return jsonify({"error": "No students found"}), 404

    def add_student(self, student, overwrite=False):
        """Adding new student."""
        # student = {
        #     "_id": uuid.uuid1().hex,
        #     "first_name": request.form.get("first_name"),
        #     "last_name": request.form.get("last_name"),
        #     "email": request.form.get("email"),
        #     "student_id": request.form.get("student_id"),
        # }
        # overwrite = bool(request.form.get("overwrite"))
        from app import DATABASE_MANAGER

        if not overwrite and DATABASE_MANAGER.get_one_by_field(
            "students", "student_id", student["student_id"]
        ):
            return jsonify({"error": "Student already in database"}), 400

        if overwrite:
            DATABASE_MANAGER.delete_one_by_field(
                "students", "student_id", student["student_id"]
            )

        DATABASE_MANAGER.insert("students", student)

        if student:
            return jsonify(student), 200

        return jsonify({"error": "Student not added"}), 400

    def get_student_by_id(self, student_id):
        """Getting student."""
        from app import DATABASE_MANAGER

        student = DATABASE_MANAGER.get_one_by_field(
            "students", "student_id", str(student_id)
        )

        if student:
            return student

        return None

    def get_student_by_uuid(self, _id: str):
        """Getting student."""
        from app import DATABASE_MANAGER

        student = DATABASE_MANAGER.get_by_id("students", _id)

        if student:
            return student

        return None

    def get_students(self):
        """Getting all students."""
        from app import DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all("students")

        if students:
            return students

        return []

    def get_students_map(self):
        """Getting all students."""
        from app import DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all("students")

        if students:
            return {student["_id"]: student for student in students}

        return {}

    def update_student_by_id(self, student_id, student_data):
        """Update student in the database by student_id."""
        # Attempt to update the student directly with the provided data
        from app import DATABASE_MANAGER

        result = DATABASE_MANAGER.update_by_field(
            "students", "student_id", str(student_id), student_data
        )

        # Return True if the update was successful (i.e., a document was matched and modified)
        if result.matched_count > 0:
            return jsonify({"message": "Student updated"}), 200
        else:
            return jsonify({"error": "Student not found"}), 404

    def update_student_by_uuid(self, uuid, student_data):
        """Update student in the database by student_id."""
        # Attempt to update the student directly with the provided data
        from app import DATABASE_MANAGER

        result = DATABASE_MANAGER.update_one_by_id("students", uuid, student_data)

        # Return True if the update was successful (i.e., a document was matched and modified)
        if result.matched_count > 0:
            return jsonify({"message": "Student updated"}), 200
        else:
            return jsonify({"error": "Student not found"}), 404

    def delete_student_by_id(self, student_id):
        """Deleting student."""
        from app import DATABASE_MANAGER

        student = DATABASE_MANAGER.get_one_by_field(
            "students", "student_id", str(student_id)
        )

        if student:
            DATABASE_MANAGER.delete_by_id("students", student["_id"])
            return jsonify({"message": "Student deleted"}), 200

        return jsonify({"error": "Student not found"}), 404

    def delete_students(self):
        """Deleting all students."""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("students")
        return jsonify({"message": "All students deleted"}), 200

    def get_student_by_email(self, email):
        """Getting student."""
        from app import DATABASE_MANAGER

        student = DATABASE_MANAGER.get_one_by_field(
            "students",
            "email",
        )

        if student:
            return jsonify(student), 200

        return jsonify({"error": "Student not found"}), 404

    def get_students_by_course(self, course):
        """Getting students."""
        from app import DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all_by_field(
            "students", "course", request.form.get("course")
        )

        if students:
            return jsonify(students), 200

        return jsonify({"error": "No students found"}), 404

    def get_students_by_skills(self, skills):
        """Getting students."""
        from app import DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all_by_field(
            "students", "skills", request.form.get("skills")
        )

        if students:
            return jsonify(students), 200

        return jsonify({"error": "No students found"}), 404

    def get_students_by_course_and_skills(self, course, skills):
        """Getting students."""
        from app import DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all_by_two_fields(
            "students", "course", course, "skills", skills
        )

        if students:
            return jsonify(students), 200

        return jsonify({"error": "No students found"}), 404

    def get_students_by_name(self, first_name, last_name):
        """Getting students by name."""
        from app import DATABASE_MANAGER

        # Ensure text index is created on the collection
        DATABASE_MANAGER.create_index(
            "students", [("first_name", TEXT), ("last_name", TEXT)]
        )

        students = DATABASE_MANAGER.get_all_by_text_search(
            "students", (f"{first_name} {last_name}")
        )

        if students:
            return jsonify(students), 200

        return jsonify({"error": "No students found"}), 404

    def import_from_xlsx(self, base_email, file):
        """Importing students from Excel file."""
        from app import DATABASE_MANAGER

        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        if not handlers.allowed_file(request.files["file"].filename, ["xlsx", "xls"]):
            return jsonify({"error": "Invalid file type"}), 400
        try:
            df = pd.read_excel(file)

            students = df.to_dict(orient="records")
            data = []
            for student in students:
                temp_student = {}
                temp_student["_id"] = uuid.uuid4().hex
                temp_student["first_name"] = student["First Name"]
                temp_student["last_name"] = student["Last Name"]
                temp_student["email"] = student["Email (Uni)"]
                if temp_student["email"].split("@")[1] != base_email:
                    return (
                        jsonify(
                            {
                                "message": (
                                    f"Incorrect student {temp_student['first_name']} "
                                    f"{temp_student['last_name']}"
                                )
                            }
                        ),
                        400,
                    )
                temp_student["student_id"] = str(student["Student Number"])
                if len(str(temp_student["student_id"])) != 8:
                    return (
                        jsonify(
                            {
                                "error": (
                                    f"Invalid student {temp_student['first_name']}, "
                                    f"{temp_student['last_name']}"
                                )
                            }
                        ),
                        400,
                    )
                DATABASE_MANAGER.delete_all_by_field(
                    "students", "student_id", temp_student["student_id"]
                )
                data.append(temp_student)
            for temp_student in data:
                DATABASE_MANAGER.insert("students", temp_student)

            return jsonify({"message": f"{len(students)} students imported"}), 200
        except (
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            FileNotFoundError,
        ) as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 400

    def student_login(self, student_id, password):
        """Handle student login."""
        from app import DATABASE_MANAGER

        # Find the student by id which is their password
        student = DATABASE_MANAGER.get_one_by_id("students", password)

        if student and str(student.get("student_id")) == student_id:
            del student["_id"]
            session["student"] = student
            session["student_logged_in"] = True
            return jsonify({"message": "Login successful"}), 200

        return jsonify({"error": "Invalid id or password"}), 401

    def rank_preferences(self, student_id, preferences):
        """Sets a students preferences."""
        from app import DATABASE_MANAGER

        student = DATABASE_MANAGER.get_one_by_field(
            "students", "student_id", str(student_id)
        )

        if not student:
            return jsonify({"error": "Student not found"}), 404

        DATABASE_MANAGER.update_one_by_field(
            "students", "student_id", str(student_id), {"preferences": preferences}
        )

        return jsonify({"message": "Preferences updated"}), 200

    def get_opportunities_by_student(self, student_id):
        """Get opportunities that a student could do"""
        find_student = self.get_student_by_id(student_id)

        if not find_student:
            return jsonify({"error": "Student not found"}), 404

        opportunities = Opportunity().get_opportunities()

        student = find_student
        student["modules"] = set(student["modules"])

        valid_opportunities = []
        for opportunity in opportunities:
            modules_required = set(
                module
                for module in opportunity["modules_required"]
                if module.strip().replace('"', "") != ""
            )

            if modules_required.issubset(student["modules"]):
                if (
                    student["course"] in opportunity["courses_required"]
                    or opportunity["courses_required"] == ""
                ):
                    if opportunity["duration"] in student["placement_duration"]:
                        valid_opportunities.append(opportunity)

        return valid_opportunities
