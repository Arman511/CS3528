"""
This module defines the Skill class and manages the caching and database operations for skills.
Classes:
    Skill: A class used to represent and manage skills in the database.
Functions:
    add_skill():
        Adds a new skill to the database. If the skill already exists and 
        overwrite is not allowed, returns an error.
        Updates the cache after adding the skill.
    delete_skill():
        Deletes a skill from the database based on the skill ID. If the 
        skill is not found, returns an error.
        Updates the cache after deleting the skill.
    get_skill_by_id():
        Retrieves a skill from the database based on the skill ID. If the 
        skill is not found, returns an error.
    get_skills():
        Retrieves all skills from the database. If the cache is valid 
        (updated within the last week), returns the cached data.
        Updates the cache if the data is fetched from the database.
"""

import uuid
from datetime import datetime, timedelta
from flask import jsonify, request
from core import database

# Cache to store skills and the last update time
skills_cache = {"data": [], "last_updated": datetime.now()}


class Skill:
    """
    A class used to represent and manage skills in the database."""

    def find_skill(self, skill_name=None, skill_id=None):
        """Check if a skill exists in the database."""
        # Check if the skill is already in the cache
        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)

        # Check if cache is valid
        if not skills_cache["data"] or skills_cache["last_updated"] <= one_week_ago:
            skills_cache["data"] = list(database.skills_collection.find())
            skills_cache["last_updated"] = current_time

        # Check if the skill is in the cache
        for skill in skills_cache["data"]:
            if skill["skill_name"] == skill_name:
                return skill
            if skill["_id"] == skill_id:
                return skill

        return None

    def add_skill(self):
        """Add Skill to database"""
        if not request.form.get("skill_name") or not request.form.get(
            "skill_description"
        ):
            return jsonify({"error": "One of the inputs is blank"}), 400

        skill = {
            "_id": uuid.uuid1().hex,
            "skill_name": request.form.get("skill_name"),
            "skill_description": request.form.get("skill_description"),
        }

        # Check if skill already exists#
        if self.find_skill(skill["skill_name"], None) is not None:
            return jsonify({"error": "Skill already in database"}), 400

        database.skills_collection.insert_one(skill)

        if skill:
            # Update cache
            skills_cache["data"].append(skill)
            skills_cache["last_updated"] = datetime.now()
            return jsonify(skill), 200

        return jsonify({"error": "Skill not added"}), 400

    def delete_skill(self, skill_id):
        """Delete kill from database"""
        if not self.find_skill(None, skill_id):
            return jsonify({"error": "Skill not found"}), 404

        database.skills_collection.delete_one({"_id": request.form.get("skill_id")})

        # Update cache
        skills = list(database.skills_collection.find())
        skills_cache["data"] = skills
        skills_cache["last_updated"] = datetime.now()

        return jsonify({"message": "Deleted"}), 200

    def get_skill_by_id(self):
        """Get skill by ID tag"""
        skill_id = request.form.get("skill_id")
        skill = self.find_skill(None, skill_id)

        if skill:
            return jsonify(skill), 200

        return jsonify({"error": "Skill not found"}), 404

    def get_skills(self):
        """Get full list of skills if chached get that instead"""
        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)

        # Check if cache is valid
        if (
            skills_cache["data"]
            and skills_cache["last_updated"]
            and skills_cache["last_updated"] > one_week_ago
        ):
            return jsonify(skills_cache["data"]), 200

        # Fetch skills from the database
        skills = list(database.skills_collection.find())

        if skills:
            # Update cache
            skills_cache["data"] = skills
            skills_cache["last_updated"] = current_time
            return jsonify(skills), 200

        return jsonify({"error": "No skills found"}), 404

    def attempt_add_skill(self):
        """Add skill to attempted skills"""
        skill_name = request.json.get("skill_name")
        found_skill = database.attempted_skills_collection.find_one(
            {"skill_name": skill_name}
        )

        if found_skill:
            database.attempted_skills_collection.update_one(
                {"_id": found_skill["_id"]}, {"$inc": {"used": 1}}
            )
            return jsonify(found_skill), 200

        new_skill = {
            "_id": uuid.uuid1().hex,
            "skill_name": skill_name,
            "skill_description": "",
            "used": 1,
        }

        database.attempted_skills_collection.insert_one(new_skill)
        return jsonify(new_skill), 200
