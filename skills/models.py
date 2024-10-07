import uuid
from flask import jsonify, request
from ..core import database
from datetime import datetime, timedelta

# Cache to store skills and the last update time
skills_cache = {
    "data": None,
    "last_updated": None
}

class Skill:
    def add_skill(self):
        skill = {
            "_id": uuid.uuid4().hex,
            "skill_name": request.form.get('skill_name'),
            "skill_description": request.form.get('skill_description')
        }
        overwrite = bool(request.form.get('overwrite'))
        
        if not overwrite and database.skills_collection.find_one({"skill_name": request.form.get('skill_name')}):
            return jsonify({"error": "Skill already in database"}), 400
        
        database.skills_collection.insert_one(skill)
        
        if skill:
            # Update cache
            skills = list(database.skills_collection.find())
            skills_cache["data"] = skills
            skills_cache["last_updated"] = datetime.now()
            return jsonify(skill), 200
        
        return jsonify({"error": "Skill not added"}), 400
    
    def delete_skill(self):
        skill = database.skills_collection.find_one({"skill_id": request.form.get('skill_id')})
        
        if not skill:
            return jsonify({"error": "Skill not found"}), 404
        
        database.skills_collection.delete_one({"skill_id": request.form.get('skill_id')})
        
        # Update cache
        skills = list(database.skills_collection.find())
        skills_cache["data"] = skills
        skills_cache["last_updated"] = datetime.now()
        
        return jsonify(skill), 200
    
    def get_skill_by_id(self):
        skill = database.skills_collection.find_one({"skill_id": request.form.get('skill_id')})
        
        if skill:
            return jsonify(skill), 200
        
        return jsonify({"error": "Skill not found"}), 404
    
    def get_skills(self):
        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)

        # Check if cache is valid
        if skills_cache["data"] and skills_cache["last_updated"] and skills_cache["last_updated"] > one_week_ago:
            return jsonify(skills_cache["data"]), 200

        # Fetch skills from the database
        skills = list(database.skills_collection.find())

        if skills:
            # Update cache
            skills_cache["data"] = skills
            skills_cache["last_updated"] = current_time
            return jsonify(skills), 200

        return jsonify({"error": "No skills found"}), 404