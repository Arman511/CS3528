"""
Skills model.
"""

import tempfile
import uuid
from flask import jsonify, send_file
import pandas as pd


class Skill:
    """
    A class used to represent and manage skills in the database."""

    def find_skill(self, skill_name="", skill_id=""):
        """Check if a skill exists in the database."""
        from app import DATABASE_MANAGER

        if skill_name:
            return DATABASE_MANAGER.get_one_by_field("skills", "skill_name", skill_name)
        if skill_id:
            return DATABASE_MANAGER.get_one_by_id("skills", skill_id)

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

        if self.find_skill(skill["skill_name"], None):
            return jsonify({"error": "Skill already in database"}), 400

        DATABASE_MANAGER.insert("skills", skill)

        return jsonify(skill), 200

    def delete_skill(self, skill_id):
        """Delete kill from database"""
        from app import DATABASE_MANAGER

        result = DATABASE_MANAGER.delete_by_id("skills", skill_id)

        if result.deleted_count == 0:
            return jsonify({"error": "Skill not found"}), 404

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

        # Fetch skills from the database
        skills = DATABASE_MANAGER.get_all("skills")

        return skills

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
            "skill_description": "",
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
            return jsonify({"error": "Attempted skill not found"}), 404

        del skill["used"]
        if description == "":
            return jsonify({"error": "Description is empty"}), 400
        skill["skill_description"] = description
        skill["skill_name"] = skill["skill_name"].capitalize()
        DATABASE_MANAGER.insert("skills", skill)
        DATABASE_MANAGER.delete_by_id("attempted_skills", skill_id)

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
            return jsonify({"error": "Attempted skill not found"}), 404

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

        original = self.find_skill(None, skill_id)
        if not original:
            return jsonify({"error": "Skill not found"}), 404

        skills = DATABASE_MANAGER.get_all_by_field(
            "skills", "skill_name", skill_name.capitalize()
        )
        skills.extend(
            DATABASE_MANAGER.get_all_by_field("skills", "skill_name", skill_name)
        )
        for skill in skills:
            if skill["_id"] != original["_id"]:
                return jsonify({"error": "Skill name already in use"}), 400

        updated_skill = {
            "_id": skill_id,
            "skill_name": skill_name.capitalize(),
            "skill_description": skill_description,
        }

        DATABASE_MANAGER.update_one_by_id("skills", skill_id, updated_skill)

        return jsonify({"message": "Updated"}), 200

    def download_all(self):
        """Returns a xlsx file with all skills"""
        from app import DATABASE_MANAGER

        skills = DATABASE_MANAGER.get_all("skills")
        clean_data = []

        for skill in skills:
            temp = {}
            temp["Skill_Name"] = skill.pop("skill_name")
            temp["Skill_Description"] = skill.pop("skill_description")
            clean_data.append(temp)

        df = pd.DataFrame(clean_data)

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            df.to_excel(tmp.name, index=False)
            tmp_file = tmp.name

            return send_file(tmp_file, as_attachment=True, download_name="skills.xlsx")

    def download_attempted(self):
        """Returns a xlsx file with all attempted skills"""
        from app import DATABASE_MANAGER

        skills = DATABASE_MANAGER.get_all("attempted_skills")
        clean_data = []
        for skill in skills:
            temp = {}
            temp["Skill_Name"] = skill.pop("skill_name")
            if "skill_description" in skill:
                temp["Skill_Description"] = skill.pop("skill_description")
            else:
                temp["Skill_Description"] = ""
            temp["Used"] = skill.pop("used")
            clean_data.append(temp)

        df = pd.DataFrame(clean_data)
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            df.to_excel(tmp.name, index=False)
            tmp_file = tmp.name

            return send_file(
                tmp_file, as_attachment=True, download_name="attempted_skills.xlsx"
            )

    def upload_skills(self, file):
        """Upload skills"""

        try:
            df = pd.read_excel(file)
        except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError):
            return jsonify({"error": "Invalid file"}), 400

        skills = df.to_dict(orient="records")

        from app import DATABASE_MANAGER

        current_skills = set(
            skill["skill_name"].lower() for skill in DATABASE_MANAGER.get_all("skills")
        )
        skill_names = set()
        clean_data = []
        try:
            for skill in skills:
                temp = {
                    "_id": uuid.uuid4().hex,
                    "skill_name": skill["Skill_Name"],
                    "skill_description": skill["Skill_Description"],
                }

                if (
                    temp["skill_name"].lower() in current_skills
                    or temp["skill_name"].lower() in skill_names
                ):
                    continue
                skill_names.add(temp["skill_name"].lower())

                clean_data.append(temp)
        except Exception:
            return jsonify({"error": "Invalid file"}), 400

        DATABASE_MANAGER.insert_many("skills", clean_data)

        return jsonify({"message": "Uploaded"}), 200

    def delete_all_skills(self):
        """Delete all skills"""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("skills")

        students = DATABASE_MANAGER.get_all("students")

        for student in students:
            if "skills" in student:
                student["skills"] = []
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        return jsonify({"message": "Deleted"}), 200

    def delete_all_attempted_skill(self):
        """Delete all attempted skills"""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("attempted_skills")

        students = DATABASE_MANAGER.get_all("students")

        for student in students:
            if "attempted_skills" in student:
                student["attempted_skills"] = []
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        return jsonify({"message": "Deleted"}), 200
