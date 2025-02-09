"""
Courses model."""

from datetime import datetime, timedelta
from flask import jsonify

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

    def delete_course_by_id(self, course_id):

        """Deletes a course from the database."""
        from app import DATABASE_MANAGER

        course = DATABASE_MANAGER.get_one_by_id("courses", id_val)

        if not course:
            return jsonify({"error": "Course not found"}), 404

        students = DATABASE_MANAGER.get_all_by_field("students", "course_id", course_id)

        if students and len(students) > 0:
            return jsonify({"error": "Course has students enrolled"}), 400

        opportunities = DATABASE_MANAGER.get_all("opportunities")

        for opportunity in opportunities:
            if (
                "courses_required" in opportunity
                and course_id in opportunity["courses_required"]
            ):
                opportunity["courses_required"].remove(course_id)
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
        DATABASE_MANAGER.update_one_by_id("courses", uuid, updated_course)

        students = DATABASE_MANAGER.get_all("students")
        for student in students:
            if "course" in student and original["course_id"] == student["course"]:
                student["course"] = updated_course["course_id"]
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)
        self.reset_cache()
        return jsonify({"message": "Course was updated"}), 200
