"""
Courses model."""

import uuid
from datetime import datetime, timedelta
from flask import jsonify, request
from core import database

# Cache to store courses and the last update time
courses_cache = {"data": None, "last_updated": None}


class Course:
    """Course data model"""

    def add_course(self):
        """Adds a course to the database."""
        course = {
            "_id": uuid.uuid1().hex,
            "course_id": request.form.get("course_id"),
            "course_name": request.form.get("course_name"),
            "course_description": request.form.get("course_description"),
        }

        if database.courses_collection.find_one(
            {"course_id": request.form.get("course_id")}
        ):
            return jsonify({"error": "Course already in database"}), 400

        database.courses_collection.insert_one(course)

        if course:
            # Update cache
            courses = list(database.courses_collection.find())
            courses_cache["data"] = courses
            courses_cache["last_updated"] = datetime.now()
            return jsonify(course), 200

        return jsonify({"error": "Course not added"}), 400

    def delete_course(self):
        """Deletes a course from the database."""
        course = database.courses_collection.find_one(
            {"course_id": request.form.get("course_id")}
        )

        if not course:
            return jsonify({"error": "Course not found"}), 404

        database.courses_collection.delete_one(
            {"course_id": request.form.get("course_id")}
        )

        # Update cache
        courses = list(database.courses_collection.find())
        courses_cache["data"] = courses
        courses_cache["last_updated"] = datetime.now()

        return jsonify(course), 200

    def get_course_by_id(self, module_id=None):
        """Retrieves a course by its ID."""
        if not module_id:
            module_id = request.form.get("course_id")
        course = database.courses_collection.find_one({"course_id": module_id})

        if course:
            return course

        return None

    def get_course_name_by_id(self, module_id):
        """Get course name by id"""
        course = self.get_course_by_id(module_id)
        if not course:
            return None
        return course["course_name"]

    def get_courses(self):
        """Retrieves all courses."""
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
        courses = list(database.courses_collection.find())

        if courses:
            # Update cache
            courses_cache["data"] = courses
            courses_cache["last_updated"] = current_time
            return courses

        return []
