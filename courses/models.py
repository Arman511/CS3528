"""
Courses model."""

from datetime import datetime, timedelta
from flask import jsonify

# Cache to store courses and the last update time
courses_cache = {"data": None, "last_updated": None}


class Course:
    """Course data model"""

    def add_course(self, course):
        """Adds a course to the database."""
        # course = {
        #     "_id": uuid.uuid1().hex,
        #     "course_id": request.form.get("course_id"),
        #     "course_name": request.form.get("course_name"),
        #     "course_description": request.form.get("course_description"),
        # }
        from app import DATABASE_MANAGER

        if DATABASE_MANAGER.get_one_by_field(
            "courses", "course_id", course["course_id"]
        ):
            return jsonify({"error": "Course already in database"}), 400

        DATABASE_MANAGER.insert("courses", course)

        if course:
            # Update cache
            courses = DATABASE_MANAGER.get_all("courses")
            courses_cache["data"] = courses
            courses_cache["last_updated"] = datetime.now()
            return jsonify(course), 200

        return jsonify({"error": "Course not added"}), 400

    def delete_course(self, course_id):
        """Deletes a course from the database."""
        from app import DATABASE_MANAGER

        course = DATABASE_MANAGER.get_one_by_field("courses", "course_id", course_id)

        if not course:
            return jsonify({"error": "Course not found"}), 404

        DATABASE_MANAGER.delete_by_id("courses", course["_id"])
        # Update cache
        courses = DATABASE_MANAGER.get_all("courses")
        courses_cache["data"] = courses
        courses_cache["last_updated"] = datetime.now()

        return jsonify(course), 200

    def get_course_by_id(self, course_id=None):
        """Retrieves a course by its ID."""
        from app import DATABASE_MANAGER

        course = DATABASE_MANAGER.get_one_by_field("courses", "course_id", course_id)

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
            courses_cache["data"] = courses
            courses_cache["last_updated"] = current_time
            return courses

        return []

    def get_courses_map(self):
        """Get courses map"""
        courses = self.get_courses()
        return {course["course_id"]: course for course in courses}
