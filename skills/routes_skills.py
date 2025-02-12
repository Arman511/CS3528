"""Handles the routes for the skills module."""

import uuid
from flask import jsonify, redirect, render_template, request, send_file
from core import handlers
from .models import Skill


def add_skills_routes(app):
    """Skills routes"""

    @app.route("/skills/attempt_add_skill_student", methods=["POST"])
    @handlers.student_login_required
    def attempt_add_skill_student():
        """Attempt to add a skill to a student."""
        skill_name = request.json.get("skill_name").lower()
        if not skill_name:
            return jsonify({"error": "Missing skill name"}), 400

        return Skill().attempt_add_skill(skill_name)

    @app.route("/skills/add_skill", methods=["POST", "GET"])
    @handlers.login_required
    def add_skill():
        if request.method == "GET":
            return render_template(
                "/skills/adding_skills.html", user_type="admin", page="skills"
            )

        if not request.form.get("skill_name") or not request.form.get(
            "skill_description"
        ):
            return jsonify({"error": "One of the inputs is blank"}), 400

        skill = {
            "_id": uuid.uuid1().hex,
            "skill_name": request.form.get("skill_name"),
            "skill_description": request.form.get("skill_description"),
        }
        if skill["skill_name"] == "" or skill["skill_description"] == "":
            return jsonify({"error": "One of the inputs is blank"}), 400
        return Skill().add_skill(skill)

    @app.route("/skills/search", methods=["GET"])
    @handlers.login_required
    def list_skills():
        return render_template(
            "/skills/search.html",
            user_type="admin",
            skills=Skill().get_skills(),
            page="skills",
        )

    @app.route("/skills/delete", methods=["DELETE"])
    @handlers.login_required
    def delete_skill():
        skill_id = request.args.get("skill_id")
        if not skill_id:
            return jsonify({"error": "Missing skill ID"}), 400
        return Skill().delete_skill(skill_id)

    @app.route("/skills/update", methods=["POST", "GET"])
    @handlers.login_required
    def update_skill():
        if request.method == "POST":
            skill_id = request.form.get("skill_id")
            skill_name = request.form.get("skill_name")
            skill_description = request.form.get("skill_description")

            if not skill_id or not skill_name or not skill_description:
                return jsonify({"error": "Missing fields"}), 400

            return Skill().update_skill(skill_id, skill_name, skill_description)

        skill_id = request.args.get("skill_id")
        skill = Skill().find_skill(None, skill_id)
        if skill is None:
            return redirect("/404")
        return render_template(
            "/skills/update_skill.html", skill=skill, user_type="admin", page="skills"
        )

    @app.route("/skills/attempted_skill_search", methods=["GET"])
    @handlers.login_required
    def search_attempt_skills():
        """Approval page for attempted Skills"""
        attempted_skills = Skill().get_list_attempted_skills()

        return render_template(
            "/skills/skill_approval.html",
            attempted_skills=attempted_skills,
            user_type="admin",
            page="skills",
        )

    @app.route("/skills/approve_skill", methods=["POST"])
    @handlers.login_required
    def approve_skill():
        uuid = request.args.get("attempt_skill_id")
        description = request.json.get("skill_description")

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
            skill = Skill().get_attempted_skill(skill_id)
            if skill is None:
                return redirect("/404")
            return render_template(
                "/skills/update_attempt_skill.html", skill=skill, page="skills"
            )
        else:
            skill_id = request.form.get("skill_id")
            skill_name = request.form.get("skill_name").lower()
            skill_description = request.form.get("skill_description")
            if not skill_name or not skill_description:
                return jsonify({"error": "One of the inputs is blank"}), 400
            return Skill().update_attempt_skill(skill_id, skill_name, skill_description)

    @app.route("/skills/download_all", methods=["GET"])
    @handlers.login_required
    def download_all_skills():
        """Download all skills"""
        return Skill().download_all()

    @app.route("/skills/download_attempted", methods=["GET"])
    @handlers.login_required
    def download_all_attempted_skills():
        """Download attempted skills"""
        return Skill().download_attempted()

    @app.route("/skills/upload", methods=["GET", "POST"])
    @handlers.login_required
    def upload_skills():
        """Upload skills from an excel file"""
        if request.method == "GET":
            return render_template(
                "/skills/upload.html", user_type="admin", page="skills"
            )
        else:
            file = request.files["file"]
            if not file:
                return jsonify({"error": "No file uploaded"}), 400
            if not handlers.allowed_file(file.filename, ["xlsx"]):
                return jsonify({"error": "Invalid file type"}), 400
            return Skill().upload_skills(file)

    @app.route("/skills/download_template", methods=["GET"])
    @handlers.login_required
    def download_skills_template():
        """Download the skills template"""
        return send_file(
            "data_model_upload_template/skills_template.xlsx", as_attachment=True
        )

    @app.route("/skills/delete_all_attempted_skill", methods=["DELETE"])
    @handlers.login_required
    def delete_all_attempted_skill():
        """Delete all attempted skills"""
        return Skill().delete_all_attempted_skill()

    @app.route("/skills/delete_all_skills", methods=["DELETE"])
    @handlers.login_required
    def delete_all_skills():
        """Delete all skills"""
        return Skill().delete_all_skills()
