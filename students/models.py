"""
This module defines the User class which handles user authentication and session management.
"""

from html import escape
import tempfile
import uuid
from flask import jsonify, send_file, session
import pandas as pd
from core import email_handler, handlers
from opportunities.models import Opportunity


class Student:
    """Student class."""

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
            return jsonify({"message": "Student added"}), 200

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

        student = DATABASE_MANAGER.get_one_by_id("students", _id)

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

        return jsonify({"error": "Student not found"}), 404

    def update_student_by_uuid(self, uuid, student_data):
        """Update student in the database by student_id."""
        # Attempt to update the student directly with the provided data
        from app import DATABASE_MANAGER

        result = DATABASE_MANAGER.update_one_by_id("students", uuid, student_data)

        # Return True if the update was successful (i.e., a document was matched and modified)
        if result.matched_count > 0:
            return jsonify({"message": "Student updated"}), 200
        return jsonify({"error": "Student not found"}), 404

    def delete_student_by_id(self, student_id):
        """Deleting student."""
        from app import DATABASE_MANAGER

        student = DATABASE_MANAGER.get_one_by_field(
            "students", "student_id", str(student_id)
        )

        if not student:
            return jsonify({"error": "Student not found"}), 404

        DATABASE_MANAGER.delete_by_id("students", student["_id"])

        opportunities = Opportunity().get_opportunities()

        for opportunity in opportunities:
            if (
                "preferences" in opportunity
                and student["_id"] in opportunity["preferences"]
            ):
                opportunity["preferences"].remove(student["_id"])
                DATABASE_MANAGER.update_one_by_id(
                    "opportunities", opportunity["_id"], opportunity
                )

        return jsonify({"message": "Student deleted"}), 200

    def delete_students(self):
        """Deleting all students."""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("students")
        return jsonify({"message": "All students deleted"}), 200

    def get_student_by_email(self, email):
        """Getting student."""
        from app import DATABASE_MANAGER

        student = DATABASE_MANAGER.get_one_by_field("students", "email", email)

        if student:
            return jsonify(student), 200

        return jsonify({"error": "Student not found"}), 404

    def import_from_xlsx(self, base_email, file):
        """Importing students from Excel file."""
        from app import DATABASE_MANAGER

        try:
            df = handlers.excel_verifier_and_reader(
                file, {"First Name", "Last Name", "Email (Uni)", "Student Number"}
            )
            students = df.to_dict(orient="records")
            data = []
            for student in students:
                temp_student = {}
                temp_student["_id"] = uuid.uuid4().hex
                temp_student["first_name"] = student["First Name"]
                temp_student["last_name"] = student["Last Name"]
                temp_student["email"] = student["Email (Uni)"]
                if temp_student["email"].split("@")[1] != base_email:
                    error_msg = {
                        "error": (
                            f"Invalid student {temp_student['first_name']}, "
                            f"{temp_student['last_name']}"
                        )
                    }
                    return jsonify(error_msg), 400

                temp_student["student_id"] = str(student["Student Number"])
                if len(str(temp_student["student_id"])) != 8:
                    error_msg = {
                        "error": (
                            f"Invalid student {temp_student['first_name']}, "
                            f"{temp_student['last_name']}"
                        )
                    }
                    return jsonify(error_msg), 400

                DATABASE_MANAGER.delete_all_by_field(
                    "students", "student_id", temp_student["student_id"]
                )

                temp_student["first_name"] = escape(temp_student["first_name"])
                temp_student["last_name"] = escape(temp_student["last_name"])
                temp_student["email"] = escape(temp_student["email"])
                temp_student["student_id"] = escape(temp_student["student_id"])

                data.append(temp_student)
            for temp_student in data:
                DATABASE_MANAGER.insert("students", temp_student)

            return jsonify({"message": f"{len(students)} students imported"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 400

    def student_login(self, student_id):
        """Handle student login."""
        from app import DATABASE_MANAGER

        # Find the student by id which is their password
        student = DATABASE_MANAGER.get_one_by_field(
            "students", "student_id", student_id
        )

        if student:
            email_handler.send_otp(student["email"])
            session["student"] = student
            return jsonify({"message": "OTP sent"}), 200

        return jsonify({"error": "Student not found"}), 404

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
            if opportunity["modules_required"] == [""]:
                opportunity["modules_required"] = []
            if opportunity["courses_required"] == [""]:
                opportunity["courses_required"] = []
            modules_required = set(opportunity["modules_required"])

            if modules_required.issubset(student["modules"]):
                if (
                    student["course"] in opportunity.get("courses_required", "")
                    or opportunity.get("courses_required") == []
                ):
                    if opportunity["duration"] in student["placement_duration"]:
                        valid_opportunities.append(opportunity)

        return valid_opportunities

    def download_students(self):
        """Download all students as a XLSX file."""
        from app import DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all("students")

        clean_data = []

        skills_map = {
            skill["_id"]: skill["skill_name"]
            for skill in DATABASE_MANAGER.get_all("skills")
        }

        for student in students:
            student_data = {
                "First Name": student["first_name"],
                "Last Name": student["last_name"],
                "Email (Uni)": student["email"],
                "Student Number": student["student_id"],
            }
            if "course" in student:
                student_data["Course"] = student["course"]
            else:
                student_data["Course"] = ""

            if "modules" in student:
                student_data["Modules"] = ",".join(student["modules"])
            else:
                student_data["Modules"] = ""

            if "skills" in student:
                student_data["Skills"] = ",".join(
                    [skills_map[skill] for skill in student["skills"]]
                )
            else:
                student_data["Skills"] = ""

            if "comments" in student:
                student_data["Comments"] = student["comments"]
            else:
                student_data["Comments"] = ""

            if "placement_duration" in student:
                student_data["Placement Duration"] = ",".join(
                    student["placement_duration"]
                )
            else:
                student_data["Placement Duration"] = ""

            clean_data.append(student_data)

        df = pd.DataFrame(clean_data)

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            tmp_file_path = tmp_file.name

            return send_file(
                tmp_file_path, as_attachment=True, download_name="students.xlsx"
            )

    def delete_all_students(self):
        """Delete all students."""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("students")

        opportunities = DATABASE_MANAGER.get_all("opportunities")

        for opportunity in opportunities:
            if "preferences" in opportunity:
                del opportunity["preferences"]
                DATABASE_MANAGER.update_one_by_id(
                    "opportunities", opportunity["_id"], opportunity
                )

        return jsonify({"message": "All students deleted"}), 200
