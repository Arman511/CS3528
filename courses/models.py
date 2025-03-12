"""
Courses model."""

from datetime import datetime, timedelta
import os
import tempfile
import uuid
from flask import jsonify, send_file
import pandas as pd


# Cache to store courses and the last update time
courses_cache = {"data": None, "last_updated": None}


class Course:
    """Course data model"""

    def reset_cache(self):
        """Resets the courses cache."""
        from app import DATABASE_MANAGER

        courses = DATABASE_MANAGER.get_all("courses")
        courses_cache["data"] = courses
        courses_cache["last_updated"] = datetime.now()
        return courses

    def add_course(self, course):
        """Adds a course to the database."""
        from app import DATABASE_MANAGER

        if DATABASE_MANAGER.get_one_by_field(
            "courses", "course_id", course["course_id"]
        ):
            return jsonify({"error": "Course already in database"}), 400

        DATABASE_MANAGER.insert("courses", course)

        if course:
            # Update cache
            self.reset_cache()
            return jsonify(course), 200

        return jsonify({"error": "Course not added"}), 400

    def delete_course_by_uuid(self, id_val):
        """Deletes a course from the database."""
        from app import DATABASE_MANAGER

        course = DATABASE_MANAGER.get_one_by_id("courses", id_val)

        if not course:
            return jsonify({"error": "Course not found"}), 404

        students = DATABASE_MANAGER.get_all_by_field(
            "students", "course", course["course_id"]
        )

        if students and len(students) > 0:
            return jsonify({"error": "Course has students enrolled"}), 400

        opportunities = DATABASE_MANAGER.get_all_by_in_list(
            "opportunities", "courses_required", [course["course_id"]]
        )

        for opportunity in opportunities:
            if (
                "courses_required" in opportunity
                and course["course_id"] in opportunity["courses_required"]
            ):
                opportunity["courses_required"].remove(course["course_id"])
                DATABASE_MANAGER.update_one_by_id(
                    "opportunities", opportunity["_id"], opportunity
                )

        DATABASE_MANAGER.delete_by_id("courses", course["_id"])
        # Update cache
        self.reset_cache()

        return jsonify(course), 200

    def get_course_by_id(self, course_id):
        """Retrieves a course by its ID."""
        from app import DATABASE_MANAGER

        course = DATABASE_MANAGER.get_one_by_field("courses", "course_id", course_id)

        if course:
            return course

        return None

    def get_course_by_uuid(self, uuid):
        """Get course by uuid"""
        from app import DATABASE_MANAGER

        course = DATABASE_MANAGER.get_one_by_id("courses", uuid)
        if course:
            return course

        return None

    def get_course_name_by_id(self, course_id):
        """Get course name by id"""
        course = self.get_course_by_id(course_id)
        if not course:
            return None
        return course["course_name"]

    def get_courses(self):
        """Retrieves all courses."""
        from app import DATABASE_MANAGER

        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)

        # Check if cache is valid
        if (
            courses_cache["data"]
            and courses_cache["last_updated"]
            and courses_cache["last_updated"] > one_week_ago
        ):
            return courses_cache["data"]

        # Fetch courses from the database
        courses = DATABASE_MANAGER.get_all("courses")

        if courses:
            # Update cache
            self.reset_cache()
            return courses

        return []

    def get_courses_map(self):
        """Get courses map"""
        courses = self.get_courses()
        return {course["course_id"]: course for course in courses}

    def update_course(self, uuid, updated_course):
        """Update course"""
        from app import DATABASE_MANAGER

        original = DATABASE_MANAGER.get_one_by_id("courses", uuid)
        if not original:
            return jsonify({"error": "Course not found"}), 404

        if (
            "course_id" in updated_course
            and updated_course["course_id"] != original["course_id"]
        ):
            match = DATABASE_MANAGER.get_one_by_field(
                "courses", "course_id", updated_course["course_id"]
            )
            if match:
                return jsonify({"error": "Course ID already exists"}), 400
        DATABASE_MANAGER.update_one_by_id("courses", uuid, updated_course)

        students = DATABASE_MANAGER.get_all("students")
        for student in students:
            if "course" in student and original["course_id"] == student["course"]:
                student["course"] = updated_course["course_id"]
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        for opportunity in opportunities:
            if (
                "courses_required" in opportunity
                and original["course_id"] in opportunity["courses_required"]
            ):
                opportunity["courses_required"].remove(original["course_id"])
                opportunity["courses_required"].append(updated_course["course_id"])
                DATABASE_MANAGER.update_one_by_id(
                    "opportunities", opportunity["_id"], opportunity
                )
        self.reset_cache()
        return jsonify({"message": "Course was updated"}), 200

    def delete_all_courses(self):
        """Deletes all courses from the database."""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("courses")
        courses_cache["data"] = []
        courses_cache["last_updated"] = datetime.now()

        students = DATABASE_MANAGER.get_all("students")
        DATABASE_MANAGER.delete_all("students")
        updated_students = []
        for student in students:
            if "course" in student:
                student["course"] = None
            updated_students.append(student)

        if updated_students:
            DATABASE_MANAGER.insert_many("students", updated_students)

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        DATABASE_MANAGER.delete_all("opportunities")
        updated_opportunities = []
        for opp in opportunities:
            if "courses_required" in opp:
                opp["courses_required"] = []
            updated_opportunities.append(opp)

        if updated_opportunities:
            DATABASE_MANAGER.insert_many("opportunities", updated_opportunities)

        return jsonify({"message": "All courses deleted"}), 200

    def download_all_courses(self):
        """Download all courses"""
        from app import DATABASE_MANAGER

        courses = DATABASE_MANAGER.get_all("courses")

        for course in courses:
            course_data = course["course_name"].rsplit(", ", 1)
            course["Course_name"] = course_data[0]
            course["Qualification"] = course_data[1] if len(course_data) > 1 else ""
            course["UCAS_code"] = course.pop("course_id")
            course["Course_description"] = course.pop("course_description")

            del course["_id"]
        # Create a DataFrame from the courses
        df = pd.DataFrame(courses)

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            file_path = temp_file.name

            # Save the DataFrame to the temporary Excel file
            df.to_excel(
                file_path,
                index=False,
                columns=[
                    "UCAS_code",
                    "Course_name",
                    "Qualification",
                    "Course_description",
                ],
            )

            # Send the file as an attachment
            return send_file(
                file_path, download_name="courses.xlsx", as_attachment=True
            )

    def upload_course_data(self, file):
        """Add courses from an Excel file."""
        from app import DATABASE_MANAGER

        # Read the Excel file
        df = pd.read_excel(file)

        # Convert the DataFrame to a list of dictionaries
        courses = df.to_dict(orient="records")

        clean_data = []
        current_ids = set(
            course["course_id"] for course in DATABASE_MANAGER.get_all("courses")
        )
        ids = set()

        for i, course in enumerate(courses):
            temp = {
                "_id": uuid.uuid4().hex,
                "course_id": course.get("UCAS_code", ""),
                "course_name": f"{course.get('Course_name', '')}, {course.get('Qualification', '')}",
                "course_description": course.get("Course_description", ""),
            }
            if not temp["course_id"] or not temp["course_name"]:
                return jsonify({"error": "Invalid data in row " + str(i + 1)}), 400
            if temp["course_id"] in ids:
                return (
                    jsonify({"error": "Duplicate course ID in row " + str(i + 1)}),
                    400,
                )
            if temp["course_id"] in current_ids:
                return jsonify({"error": "Course ID already exists"}), 400
            clean_data.append(temp)
            ids.add(temp["course_id"])

        DATABASE_MANAGER.insert_many("courses", clean_data)

        # Update cache
        courses = DATABASE_MANAGER.get_all("courses")
        courses_cache["data"] = courses
        courses_cache["last_updated"] = datetime.now()

        return jsonify({"message": "Uploaded"}), 200
