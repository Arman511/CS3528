import uuid
from flask import jsonify, request
from ..core import database
from datetime import datetime, timedelta

# Cache to store courses and the last update time
courses_cache = {
    "data": None,
    "last_updated": None
}
class Course:
    def add_course(self):
        course = {
            "_id": uuid.uuid4().hex,
            "course_id": request.form.get('course_id'),
            "course_name": request.form.get('course_name'),
            "course_description": request.form.get('course_description')
        }
        overwrite = bool(request.form.get('overwrite'))
        
        if not overwrite and database.courses_collection.find_one({"course_id": request.form.get('course_id')}):
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
        course = database.courses_collection.find_one({"course_id": request.form.get('course_id')})
        
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        database.courses_collection.delete_one({"course_id": request.form.get('course_id')})
        
        # Update cache
        courses = list(database.courses_collection.find())
        courses_cache["data"] = courses
        courses_cache["last_updated"] = datetime.now()
        
        return jsonify(course), 200
    
    def get_course_by_id(self):
        course = database.courses_collection.find_one({"course_id": request.form.get('course_id')})
        
        if course:
            return jsonify(course), 200
        
        return jsonify({"error": "Course not found"}), 404
    

    def get_courses(self):
        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)

        # Check if cache is valid
        if courses_cache["data"] and courses_cache["last_updated"] and courses_cache["last_updated"] > one_week_ago:
            return jsonify(courses_cache["data"]), 200

        # Fetch courses from the database
        courses = list(database.courses_collection.find())

        if courses:
            # Update cache
            courses_cache["data"] = courses
            courses_cache["last_updated"] = current_time
            return jsonify(courses), 200

        return jsonify({"error": "No courses found"}), 404