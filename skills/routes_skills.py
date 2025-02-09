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

    @app.route("/skills/search", methods=["GET"])
    @handlers.login_required
    def list_skills():
        return render_template(
            "/skills/list.html", user_type="admin", skills=Skill().get_skills()
        )

    @app.route("/skills/delete", methods=["POST"])
    @handlers.login_required
    def delete_skill():
        skill_id = request.form.get("skill_id")
        if not skill_id:
            return jsonify({"error": "Missing skill ID"}, 400)
        return Skill().delete_skill(skill_id)

    @app.route("/skills/update", methods=["POST", "GET"])
    @handlers.login_required
    def update_skill():
        skill_id = request.form.get("skill_id")
        skill_name = request.form.get("skill_name")
        skill_description = request.form.get("skill_description")

        if not skill_id or not skill_name or not skill_description:
            return jsonify({"error": "Missing fields"}), 400

        updated_skill = {
            "_id": skill_id,
            "skill_name": skill_name,
            "skill_description": skill_description,
        }

        return Skill().update_skill(updated_skill)
