"""Routes for opportunities"""

import uuid
from flask import flash, redirect, render_template, request, session, url_for
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
        user = session.get("user")
        employer = session.get("employer")

        user_type = "admin" if user else "employer"
        print(f"[DEBUG] User type: {user_type}")

        # Common opportunity search parameters
        company_name = employer.get("company_name") if employer else ""
        title = ""

        # Fetch opportunities based on user type
        opportunities = Opportunity().search_opportunities(
            title=title, company_name=company_name
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
            )

        if request.method == "POST":
            opportunity = {
                "_id": request.form.get("_id"),
                "title": request.form.get("title"),
                "description": request.form.get("description"),
                "url": request.form.get("url"),
                "employer_id": None,
                "location": request.form.get("location"),
                "modules_required": request.form.get("modules_required")[1:-1]
                .replace('"', "")
                .split(","),
                "courses_required": request.form.get("courses_required")[1:-1]
                .replace('"', "")
                .split(","),
                "spots_available": request.form.get("spots_available"),
                "duration": request.form.get("duration"),
            }
            if handlers.is_admin():
                opportunity["employer_id"] = request.form.get("employer_id")
                return Opportunity().add_update_opportunity(opportunity, True)
            else:
                if (
                    Opportunity().get_opportunity_by_id(opportunity["_id"])[
                        "employer_id"
                    ]
                    != session["employer"]["_id"]
                ):
                    return {"error": "Unauthorized Access."}, 401
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

        return render_template(
            "opportunities/employer_add_update_opportunity.html",
            opportunity=opportunity,
            courses=Course().get_courses(),
            modules=Module().get_modules(),
            user_type="admin" if "logged_in" in session else "employer",
            employer=employer,  # Add employer to the template context
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
