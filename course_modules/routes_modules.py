"""Handles the routes for the Module module."""

import uuid
from flask import render_template, request
from core import handlers
from .models import Module


def add_module_routes(app):
    """Module routes"""

    @app.route("/course_modules/add_module", methods=["POST", "GET"])
    @handlers.login_required
    def add_course_module():
        if request.method == "GET":
            return render_template(
                "course_modules/adding_modules.html", user_type="admin"
            )

        module = {
            "_id": uuid.uuid1().hex,
            "module_id": request.form.get("module_id"),
            "module_name": request.form.get("module_name"),
            "module_description": request.form.get("module_description"),
        }
        return Module().add_module(module)
