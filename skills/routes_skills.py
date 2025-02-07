"""Handles the routes for the skills module."""

import uuid
from flask import jsonify, render_template, request
from core import handlers
from .models import Skill


def add_skills_routes(app):
    """Skills routes"""

    @app.route("/skills/attempt_add_skill_student", methods=["POST"])
    @handlers.student_login_required
    def attempt_add_skill_student():
        """Attempt to add a skill to a student."""
        skill_name = request.json.get("skill_name").lower()

        return Skill().attempt_add_skill(skill_name)

    @app.route("/skills/add_skill", methods=["POST", "GET"])
    @handlers.login_required
    def add_skill():
        if request.method == "GET":
            return render_template("/skills/adding_skills.html", user_type="admin")

        if not request.form.get("skill_name") or not request.form.get(
            "skill_description"
        ):
            return jsonify({"error": "One of the inputs is blank"}), 400

        skill = {
            "_id": uuid.uuid1().hex,
            "skill_name": request.form.get("skill_name"),
            "skill_description": request.form.get("skill_description"),
        }
        return Skill().add_skill(skill)

    @app.route("/skills/attempted_skill_search", methods=["GET"])
    @handlers.login_required
    def search_attempt_skills():
        """Approval page for attempted Skills"""
        attempted_skills = Skill().get_list_attempted_skills()

        return render_template(
            "/skills/skill_approval.html", attempted_skills=attempted_skills
        )

    @app.route("/skills/approve_skill", methods=["POST"])
    @handlers.login_required
    def approve_skill():
        uuid = request.args.get("attempt_skill_id")
        description = request.json.get("description")

        return Skill().approve_skill(uuid, description)

    @app.route("/skills/reject_skill", methods=["POST"])
    @handlers.login_required
    def reject_skill():
        uuid = request.args.get("attempt_skill_id")

        return Skill().reject_skill(uuid)

    @app.route("/skills/update_attempted_skill", methods=["GET", "POST"])
    @handlers.login_required
    def update_attempted_skill():
        if request.method == "GET":
            skill_id = request.args.get("attempt_skill_id")
            skill = Skill().get_skill(skill_id)
            return render_template("/skills/update_attempt_skill.html", skill=skill)
        else:
            skill_id = request.form.get("skill_id")
            skill_name = request.form.get("skill_name").lower()
            skill_description = request.form.get("skill_description")
            if not skill_name or not skill_description:
                return jsonify({"error": "One of the inputs is blank"}), 400
            return Skill().update_attempt_skill(skill_id, skill_name, skill_description)
