"""Handles the routes for the Module module."""

import uuid
from flask import redirect, render_template, request
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

    @app.route("/course_modules/search", methods=["GET"])
    @handlers.login_required
    def search_modules():
        """Search modules page"""
        modules = Module().get_modules()
        return render_template(
            "course_modules/search.html", modules=modules, user_type="admin"
        )

    @app.route("/course_modules/delete", methods=["DELETE"])
    @handlers.login_required
    def delete_module():
        module_id = request.args.get("uuid")
        return Module().delete_module_by_uuid(module_id)

    @app.route("/course_modules/update", methods=["GET", "POST"])
    @handlers.login_required
    def update_module():
        if request.method == "GET":
            module_id = request.args.get("uuid")
            module = Module().get_module_by_uuid(module_id)
            if not module:
                return redirect("/404")
            return render_template(
                "course_modules/update.html",
                module=module,
                user_type="admin",
            )
        uuid = request.args.get("uuid")

        module_id = request.form.get("module_id")
        module_name = request.form.get("module_name")
        module_description = request.form.get("module_description")
        return Module().update_module_by_uuid(
            uuid, module_id, module_name, module_description
        )
