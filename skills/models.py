"""
Skills model.
"""

import uuid
from datetime import datetime, timedelta
from flask import jsonify

# Cache to store skills and the last update time
skills_cache = {"data": [], "last_updated": datetime.now()}


class Skill:
    """
    A class used to represent and manage skills in the database."""

    def find_skill(self, skill_name="", skill_id=""):
        """Check if a skill exists in the database."""
        from app import DATABASE_MANAGER

        # Check if the skill is already in the cache
        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)

        # Check if cache is valid
        if not skills_cache["data"] or skills_cache["last_updated"] <= one_week_ago:
            skills_cache["data"] = DATABASE_MANAGER.get_all("skills")
            skills_cache["last_updated"] = current_time

        # Check if the skill is in the cache
        for skill in skills_cache["data"]:
            if skill_name and skill["skill_name"].lower() == skill_name.lower():
                return skill
            if skill_id and skill["_id"] == skill_id:
                return skill

        return None

    def add_skill(self, skill):
        """Add Skill to database"""
        # skill = {
        #     "_id": uuid.uuid1().hex,
        #     "skill_name": request.form.get("skill_name"),
        #     "skill_description": request.form.get("skill_description"),
        # }

        # Check if skill already exists#
        from app import DATABASE_MANAGER

        if self.find_skill(skill["skill_name"], None) is not None:
            return jsonify({"error": "Skill already in database"}), 400

        DATABASE_MANAGER.insert("skills", skill)

        if skill:
            # Update cache
            skills_cache["data"].append(skill)
            skills_cache["last_updated"] = datetime.now()

        return jsonify(skill), 200

    def delete_skill(self, skill_id):
        """Delete kill from database"""
        from app import DATABASE_MANAGER

        if not self.find_skill(None, skill_id):
            return jsonify({"error": "Skill not found"}), 404

        DATABASE_MANAGER.delete_by_id("skills", skill_id)

        # Update cache
        skills = DATABASE_MANAGER.get_all("skills")
        skills_cache["data"] = skills
        skills_cache["last_updated"] = datetime.now()

        students = DATABASE_MANAGER.get_all("students")

        for student in students:
            if skill_id in student.get("skills", []):
                student["skills"].remove(skill_id)
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        return jsonify({"message": "Deleted"}), 200

    def get_skill_by_id(self, skill_id):
        """Get skill by ID tag"""
        skill = self.find_skill(None, skill_id)

        if skill:
            return skill

        return None

    def get_skill_name_by_id(self, skill_id):
        """Get skill name by id"""
        skill = self.get_skill_by_id(skill_id)
        if not skill:
            return None
        return skill["skill_name"]

    def get_skills(self):
        """Get full list of skills if cached get that instead"""
        from app import DATABASE_MANAGER

        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)

        # Check if cache is valid
        if (
            skills_cache["data"]
            and skills_cache["last_updated"]
            and skills_cache["last_updated"] > one_week_ago
        ):
            return skills_cache["data"]

        # Fetch skills from the database
        skills = DATABASE_MANAGER.get_all("skills")

        if skills:
            # Update cache
            skills_cache["data"] = skills
            skills_cache["last_updated"] = current_time
            return skills

        return []

    def get_skills_map(self):
        """Get skills map"""
        skills = self.get_skills()
        return {skill["_id"]: skill for skill in skills}

    def attempt_add_skill(self, skill_name):
        """Add skill to attempted skills"""
        from app import DATABASE_MANAGER

        found_skill = DATABASE_MANAGER.get_one_by_field(
            "attempted_skills", "skill_name", skill_name
        )

        if found_skill:
            DATABASE_MANAGER.increment(
                "attempted_skills", found_skill["_id"], "used", 1
            )
            return jsonify(found_skill), 200

        new_skill = {
            "_id": uuid.uuid1().hex,
            "skill_name": skill_name,
            "used": 1,
        }

        DATABASE_MANAGER.insert("attempted_skills", new_skill)
        return jsonify(new_skill), 200

    def get_list_attempted_skills(self):
        """Get list of attempted skills"""
        from app import DATABASE_MANAGER

        attempted_skills = DATABASE_MANAGER.get_all("attempted_skills")

        if not attempted_skills:
            return []

        return attempted_skills

    def get_attempted_skill(self, skill_id):
        """Get attempted skill"""
        from app import DATABASE_MANAGER

        skill = DATABASE_MANAGER.get_one_by_id("attempted_skills", skill_id)

        if not skill:
            return None

        return skill

    def approve_skill(self, skill_id, description):
        """Approve skill"""
        from app import DATABASE_MANAGER

        skill = DATABASE_MANAGER.get_one_by_id("attempted_skills", skill_id)

        if not skill:
            return jsonify({"error": "Skill not found"}), 404

        del skill["used"]
        if description == "":
            return jsonify({"error": "Description is empty"}), 400
        skill["skill_description"] = description
        skill["skill_name"] = skill["skill_name"].capitalize()
        DATABASE_MANAGER.insert("skills", skill)
        DATABASE_MANAGER.delete_by_id("attempted_skills", skill_id)

        # Update cache
        skills = DATABASE_MANAGER.get_all("skills")
        skills_cache["data"] = skills
        skills_cache["last_updated"] = datetime.now()

        # Update students
        students = DATABASE_MANAGER.get_all("students")
        for student in students:
            if skill_id in student.get("attempted_skills", []):
                student["skills"].append(skill_id)
                student["attempted_skills"].remove(skill_id)
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        return jsonify({"message": "Approved"}), 200

    def reject_skill(self, skill_id):
        """Reject skill"""
        from app import DATABASE_MANAGER

        skill = DATABASE_MANAGER.get_one_by_id("attempted_skills", skill_id)

        if not skill:
            return jsonify({"error": "Skill not found"}), 404

        DATABASE_MANAGER.delete_by_id("attempted_skills", skill_id)

        # Update students
        students = DATABASE_MANAGER.get_all("students")
        for student in students:
            if skill_id in student.get("attempted_skills", []):
                student["attempted_skills"].remove(skill_id)
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        return jsonify({"message": "Rejected"}), 200

    def update_attempt_skill(self, skill_id, skill_name, skill_description):
        """Update attempted skill"""
        from app import DATABASE_MANAGER

        skill = DATABASE_MANAGER.get_one_by_id("attempted_skills", skill_id)

        if not skill:
            return jsonify({"error": "Skill not found"}), 404

        skill["skill_name"] = skill_name
        skill["skill_description"] = skill_description
        DATABASE_MANAGER.update_one_by_id("attempted_skills", skill_id, skill)

        return jsonify({"message": "Updated"}), 200

    def update_skill(self, skill_id, skill_name: str, skill_description):
        """Updates a skill"""

        from app import DATABASE_MANAGER

        original = DATABASE_MANAGER.get_one_by_id("skills", skill_id)
        if not original:
            return jsonify({"error": "Skill not found"}), 404

        skills = DATABASE_MANAGER.get_all_by_field(
            "skills", "skill_name", skill_name.capitalize()
        )
        for skill in skills:
            if skill["_id"] != original["_id"]:
                return jsonify({"error": "Skill name already in use"}), 400

        skill = {
            "_id": skill_id,
            "skill_name": skill_name.capitalize(),
            "skill_description": skill_description,
        }

        DATABASE_MANAGER.update_one_by_id("skills", skill_id, original)

        # Update cache
        skills = DATABASE_MANAGER.get_all("skills")
        skills_cache["data"] = skills
        skills_cache["last_updated"] = datetime.now()

        return jsonify({"message": "Updated"}), 200
