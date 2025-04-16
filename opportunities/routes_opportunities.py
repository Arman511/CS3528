"""Routes for opportunities"""

from html import escape
import uuid
from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from core import handlers
from course_modules.models import Module
from courses.models import Course
from employers.models import Employers
from .models import Opportunity


def add_opportunities_routes(app):
    """Add routes for opportunities"""

    @app.route("/opportunities/search", methods=["GET"])
    @handlers.admin_or_employers_required
    def search_opportunities():
        """
        Unified route for searching opportunities by admins and employers.
        Determines user type from session.
        """
        # Fetch user session details

        user_type = handlers.get_user_type()
        employer = session.get("employer", None)
        print(f"[DEBUG] User type: {user_type}")
        # Fetch opportunities based on user type
        if user_type == "admin":
            opportunities = Opportunity().get_opportunities_for_search(_id=None)
        else:
            opportunities = Opportunity().get_opportunities_for_search(
                _id=employer.get("_id", None)
            )

        # Prepare context for rendering
        context = {
            "opportunities": opportunities,
            "user_type": user_type,
            "courses": Course().get_courses(),
            "modules": Module().get_modules(),
        }

        # Add employers map if admin
        if user_type == "admin":
            employers_map = {
                employer["_id"]: employer for employer in Employers().get_employers()
            }
            context["employers_map"] = employers_map
            context["page"] = "opportunities"

        return render_template("opportunities/search.html", **context)

    @app.route(
        "/opportunities/employer_add_update_opportunity", methods=["GET", "POST"]
    )
    @handlers.admin_or_employers_required
    def employer_add_update_opportunity():
        # Check if the details deadline has passed and the employer is in the session
        from app import DEADLINE_MANAGER

        if DEADLINE_MANAGER.is_past_details_deadline() and "employer" in session:
            return render_template(
                "employers/past_deadline.html",
                data=(
                    "Adding/Updating details deadline has passed as of "
                    f"{DEADLINE_MANAGER.get_details_deadline()}"
                ),
                referrer=request.referrer,
                employer=session["employer"],  # Pass employer to the template
                user_type="employer",
                deadline_type=DEADLINE_MANAGER.get_deadline_type(),
            )

        if request.method == "POST":
            try:
                opportunity = {
                    "_id": request.form.get("_id"),
                    "title": request.form.get("title"),
                    "description": request.form.get("description"),
                    "url": request.form.get("url", ""),
                    "employer_id": None,
                    "location": request.form.get("location"),
                    "modules_required": [
                        module.strip()
                        for module in request.form.get("modules_required")[1:-1]
                        .replace('"', "")
                        .split(",")
                    ],
                    "courses_required": [
                        course.strip()
                        for course in request.form.get("courses_required")[1:-1]
                        .replace('"', "")
                        .split(",")
                    ],
                    "spots_available": int(request.form.get("spots_available")),
                    "duration": request.form.get("duration"),
                }

                # Check if any required field is empty
                for key, value in opportunity.items():
                    if not value and key not in {
                        "employer_id",
                        "url",
                        "modules_required",
                        "courses_required",
                    }:
                        raise ValueError(
                            f"Field {key} is required and cannot be empty."
                        )
                if opportunity["modules_required"] == [""]:
                    opportunity["modules_required"] = []
                if opportunity["courses_required"] == [""]:
                    opportunity["courses_required"] = []

                if opportunity["spots_available"] < 1:
                    raise ValueError("Spots available must be at least 1.")
                if opportunity["duration"] not in [
                    "1_day",
                    "1_week",
                    "1_month",
                    "3_months",
                    "6_months",
                    "12_months",
                ]:
                    raise ValueError("Invalid duration value.")
            except Exception as e:
                return jsonify({"error": str(e)}), 400

            opportunity["title"] = escape(opportunity["title"])
            opportunity["description"] = escape(opportunity["description"])
            opportunity["url"] = escape(opportunity["url"])
            opportunity["location"] = escape(opportunity["location"])
            opportunity["duration"] = escape(opportunity["duration"])
            opportunity["modules_required"] = [
                escape(module) for module in opportunity["modules_required"]
            ]
            opportunity["courses_required"] = [
                escape(course) for course in opportunity["courses_required"]
            ]

            if handlers.is_admin():
                opportunity["employer_id"] = request.form.get("company")
                return Opportunity().add_update_opportunity(opportunity, True)

            original = Opportunity().get_opportunity_by_id(opportunity["_id"])
            if original and original["employer_id"] != session["employer"]["_id"]:
                return jsonify({"error": "Unauthorized Access."}), 401
            opportunity["employer_id"] = session["employer"]["_id"]
            return Opportunity().add_update_opportunity(opportunity, False)

        # Get the opportunity by ID if it exists
        opportunity_id = request.args.get("opportunity_id")
        if opportunity_id is not None:
            opportunity = Opportunity().get_opportunity_by_id(opportunity_id)
        else:
            opportunity = {"_id": uuid.uuid4().hex, "spots_available": 1}

        # Include employer in the context
        employer = session.get("employer", None)
        user_type = "admin" if handlers.is_admin() else "employer"
        employers = Employers().get_employers()
        return render_template(
            "opportunities/employer_add_update_opportunity.html",
            opportunity=opportunity,
            courses=Course().get_courses(),
            modules=Module().get_modules(),
            user_type=user_type,
            employer=employer,  # Add employer to the template context
            page="opportunities",
            employers=employers,
            deadline_type=DEADLINE_MANAGER.get_deadline_type(),
        )

    @app.route("/opportunities/employer_delete_opportunity", methods=["POST", "GET"])
    @handlers.admin_or_employers_required
    def employer_delete_opportunity():
        opportunity_id = request.args.get("opportunity_id")
        if not opportunity_id:
            flash("Opportunity ID is required", "error")
            return redirect(request.referrer)

        Opportunity().delete_opportunity_by_id(opportunity_id)
        flash("Opportunity deleted successfully", "success")
        return redirect(url_for("search_opportunities"))

    @app.route("/opportunities/upload", methods=["GET", "POST"])
    @handlers.admin_or_employers_required
    def upload_opportunities():
        from app import DEADLINE_MANAGER

        user_type = "admin" if handlers.is_admin() else "employer"

        if request.method == "POST":
            file = request.files["file"]
            if not file:
                return jsonify({"error": "No file provided"}), 400
            if not handlers.allowed_file(file.filename, ["xlsx", "xls"]):
                return jsonify({"error": "Invalid file type"}), 400

            if user_type == "admin":
                return Opportunity().upload_opportunities(file, True)

            return Opportunity().upload_opportunities(file, False)

        return render_template(
            "opportunities/upload.html",
            user_type=user_type,
            page="opportunities",
            deadline_type=DEADLINE_MANAGER.get_deadline_type(),
        )

    @app.route("/opportunities/download_all", methods=["GET"])
    @handlers.admin_or_employers_required
    def download_opportunities():
        user_type = "admin" if handlers.is_admin() else "employer"
        if user_type == "admin":
            return Opportunity().download_opportunities(True)
        return Opportunity().download_opportunities(False)

    @app.route("/opportunities/download_template", methods=["GET"])
    @handlers.admin_or_employers_required
    def download_opportunities_template():
        user_type = "admin" if handlers.is_admin() else "employer"

        if user_type == "admin":
            return send_file(
                "data_model_upload_template/admin_opportunities_template.xlsx",
                as_attachment=True,
            )
        return send_file(
            "data_model_upload_template/employer_opportunities_template.xlsx",
            as_attachment=True,
        )

    @app.route("/opportunities/delete_all", methods=["DELETE"])
    @handlers.admin_or_employers_required
    def delete_all_opportunities():
        user_type = "admin" if handlers.is_admin() else "employer"
        if user_type == "admin":
            return Opportunity().delete_all_opportunities(True)
        return Opportunity().delete_all_opportunities(False)
