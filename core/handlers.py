"""
Handles the base routes, adds the module routes, and includes decorators
to enforce user access levels.
"""

from datetime import datetime, timezone
from functools import wraps
import os
from flask import (
    jsonify,
    render_template,
    send_from_directory,
    session,
    redirect,
    make_response,
    request,
)
import pandas as pd
from core import routes_debug
from core import routes_error
from user import routes_user
from students import routes_student
from opportunities import routes_opportunities
from skills import routes_skills
from courses import routes_courses
from course_modules import routes_modules
from employers import routes_employers
from superuser import routes_superuser


def allowed_file(filename, types):
    """Check if file type is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in set(types)


# Decorators
def login_required(f):
    """
    This decorator ensures that a user is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        if "superuser" in session:
            return redirect("/user/search")
        if "employer_logged_in" in session:
            return redirect("/employers/home")
        return redirect("/")

    return wrap


def is_admin():
    """Check if the user is an admin."""
    return session.get("logged_in") is not None


def student_login_required(f):
    """
    This decorator ensures that a student is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "student_logged_in" in session:
            return f(*args, **kwargs)
        if "employer_logged_in" in session:
            return redirect("/employers/home")
        if "superuser" in session:
            return redirect("/user/search")
        if "logged_in" in session:
            return redirect("/user/home")
        return redirect("/")

    return wrap


def employers_login_required(f):
    """
    This decorator ensures that a employer is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "employer_logged_in" in session:
            employer = session.get("employer")
            return f(employer, *args, **kwargs)
        if "superuser" in session:
            return redirect("/user/search")
        if "logged_in" in session:
            return redirect("/user/home")

        return redirect("/employers/login")

    return wrap


def admin_or_employers_required(f):
    """
    This decorator ensures that a employer or admin is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "employer_logged_in" in session or "logged_in" in session:
            return f(*args, **kwargs)
        if "superuser" in session:
            return redirect("/user/search")
        return redirect("/")

    return wrap


def superuser_required(f):
    """
    This decorator ensures that a superuser is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "superuser" in session and session.get("superuser"):
            return f(*args, **kwargs)
        return redirect("/")

    return wrap


def get_user_type():
    """Get the user type from the session data."""
    user = session.get("user")
    employer = session.get("employer")
    student = session.get("student")
    superuser = session.get("superuser")

    user_type = None
    # Determine user_type based on session data
    if superuser:
        user_type = "superuser"
    elif user:
        user_type = "admin"
    elif employer:
        user_type = "employer"
    elif student:
        user_type = "student"
    return user_type


def clear_session_save_theme():
    """Clear the session and save the theme."""
    if "theme" not in session:
        session["theme"] = "light"

    theme = session["theme"]
    session.clear()
    session["theme"] = theme


def excel_verifier_and_reader(file, expected_columns: set[str]):
    """
    Verifies and reads an Excel file.
    Args:
        file (FileStorage): The uploaded Excel file.
        expected_columns (set): A set of expected column names.
    Returns:
        pd.DataFrame: The DataFrame containing the data from the Excel file.
    Raises:
        ValueError: If the file is not a valid Excel file, if the file size exceeds the limit,
                    or if the expected columns are missing.
    """
    dataframe = None
    try:
        filename = file.filename
    except AttributeError:
        try:
            filename = file.name
        except AttributeError:
            filename = file.file_path
    if not filename.lower().endswith(".xlsx"):
        raise ValueError("Invalid file type. Please upload a .xlsx file.")

    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)

    MAX_SIZE_MB = 5
    try:
        dataframe = pd.read_excel(file, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Invalid Excel file: {e}. Please upload a valid .xlsx file.")
    if file_length > MAX_SIZE_MB * 1024 * 1024:
        raise ValueError(
            f"File size exceeds {MAX_SIZE_MB} MB. Please upload a smaller file."
        )
    if dataframe.empty:
        raise ValueError("The uploaded file is empty. Please upload a valid file.")

    missing_columns = expected_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}. Please upload a valid file."
        )

    return dataframe


def configure_routes(app):
    """Configures the routes for the given Flask application.
    This function sets up the routes for user and student modules by calling their respective
    route configuration functions. It also defines the home route and the privacy policy route.
    Args:
        app (Flask): The Flask application instance.
    """

    routes_user.add_user_routes(app)
    routes_student.add_student_routes(app)
    routes_opportunities.add_opportunities_routes(app)
    routes_skills.add_skills_routes(app)
    routes_courses.add_course_routes(app)
    routes_modules.add_module_routes(app)
    routes_employers.add_employer_routes(app)
    routes_superuser.add_superuser_routes(app)
    routes_debug.add_debug_routes(app)
    routes_error.add_error_routes(app)

    @app.route("/landing_page")
    @app.route("/")
    def index():
        """The home route which renders the 'landing_page.html' template."""
        user = get_user_type()
        if user == "student":
            return redirect("/students/login")
        if user == "employer":
            return redirect("/employers/home")
        if user == "admin":
            return redirect("/user/home")
        if user == "superuser":
            return redirect("/superuser/home")
        clear_session_save_theme()
        return render_template("landing_page.html")

    @app.route("/toggle_theme", methods=["GET"])
    def toggle_theme():
        """Toggle the theme between light and dark mode."""
        if "theme" not in session:
            session["theme"] = "dark"
            return redirect(request.referrer)

        session["theme"] = "dark" if session["theme"] == "light" else "light"
        return redirect(request.referrer)

    @app.route("/privacy-agreement", methods=["POST", "GET"])
    def privacy_agreement():
        """
        Handles the privacy agreement submission.
        This route is triggered when a user agrees to the privacy policy.
        """
        if request.method == "GET":
            if session.get("privacy_agreed"):
                return jsonify({"message": True}), 200
            else:
                return jsonify({"message": False}), 200
        data = request.get_json()
        if data and data.get("agreed"):
            session["privacy_agreed"] = True
            response = jsonify({"message": "Agreement recorded successfully."})
            response.set_cookie("privacy_agreed", "true", max_age=30 * 24 * 60 * 60)
            return response, 200
        return jsonify({"error": "Invalid request or missing agreement data."}), 400

    @app.route("/api/session", methods=["GET"])
    @admin_or_employers_required
    def get_session():
        user = session.get("user")
        employer = session.get("employer")

        # Determine user_type based on session data
        if user:
            user_type = user.get("name").lower()
        elif employer:
            user_type = employer.get("company_name")
        else:
            user_type = None
        return jsonify({"user_type": user_type})

    @app.route("/privacy_policy")
    def privacy_policy():
        """The privacy policy route which renders the 'privacy_policy.html' template.

        Returns:
            str: Rendered HTML template for the privacy policy page.
        """
        return render_template("privacy_policy.html", user_type=get_user_type())

    @app.route("/modal_privacy_policy")
    def modal_privacy_policy():
        """The modal privacy policy route which renders the 'modal_privacy_policy.html' template.

        Returns:
            str: Rendered HTML template for the modal privacy policy page.
        """
        return render_template("modal_privacy_policy.html", user_type=get_user_type())

    @app.route("/cookies_policy")
    def cookies_policy():
        """The cookies policy route which renders the 'cookies_policy.html' template.

        Returns:
            str: Rendered HTML template for the cookies policy page.
        """
        return render_template("cookies.html", user_type=get_user_type())

    @app.route("/robots.txt")
    def robots():
        """The robots.txt route which renders the 'robots.txt' template.

        Returns:
            str: Rendered robots.txt template.
        """
        return app.send_static_file("robots.txt")

    @app.route("/signout")
    def signout():
        """Clears the current session and redirects to the home page."""
        clear_session_save_theme()
        return redirect("/")

    @app.route("/favicon.ico")
    def favicon():
        """The favicon route which renders the 'favicon.ico' template.

        Returns:
            str: Rendered favicon.ico template.
        """
        return app.send_static_file("favicon.ico")

    @app.route("/tutorial")
    def tutorial():
        """The tutorial route which renders the page specific to a user type."""
        from app import DEADLINE_MANAGER

        user_type = get_user_type()

        if user_type == "admin":
            return render_template("tutorials/tutorial_admin.html", user_type="admin")
        if user_type == "employer":
            return render_template(
                "tutorials/tutorial_employer.html",
                user_type="employer",
                deadline_type=DEADLINE_MANAGER.get_deadline_type(),
            )
        if user_type == "student":
            return render_template(
                "tutorials/tutorial_student.html", user_type="student"
            )
        if user_type == "superuser":
            return render_template(
                "tutorials/tutorial_superuser.html", user_type="superuser"
            )

        return render_template("tutorials/tutorial_login.html")

    @app.route("/sitemap")
    @app.route("/sitemap/")
    @app.route("/sitemap.xml")
    def sitemap():
        """
        Route to dynamically generate a sitemap of your website/application.
        """

        host_base = f"{request.scheme}://{request.host}"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")

        priority_mapping = {
            "/": "1.0",
            "/privacy_policy": "0.8",
            "/sitemap": "0.5",
        }

        urls = [
            {
                "loc": f"{host_base}{str(rule)}",
                "lastmod": now,
                "priority": priority_mapping.get(str(rule), "0.5"),
            }
            for rule in app.url_map.iter_rules()
            if "GET" in rule.methods
            and not rule.arguments
            and not any(
                str(rule).startswith(prefix)
                for prefix in ["/admin", "/user", "/debug", "/superuser", "/api"]
            )
        ]

        xml_sitemap = render_template(
            "sitemap.xml",
            urls=urls,
            host_base=host_base,
        )
        response = make_response(xml_sitemap)
        response.headers["Content-Type"] = "application/xml"

        return response

    @app.after_request
    def add_cache_control_and_headers(response):
        if response.content_type in {
            "text/css",
            "application/javascript",
            "application/font-woff2",
            "application/font-ttf",
        }:
            response.cache_control.max_age = 3600
        elif "image" in response.content_type or "audio" in response.content_type:
            response.cache_control.max_age = 31536000
            response.cache_control.public = True
        elif (
            response.content_type == "text/html; charset=utf-8"
            or response.content_type == "text/html"
        ):
            response.cache_control.no_store = True
        elif response.content_type == "application/json":
            response.cache_control.no_store = True
        else:
            response.cache_control.max_age = 3600

        response.cache_control.stale_while_revalidate = 3600
        return response

    @app.route("/static/<path:filename>")
    def serve_static(filename):
        response = send_from_directory(os.path.join(app.root_path, "static"), filename)
        if filename.endswith(".woff2"):
            response.headers["Content-Type"] = "font/woff2"
        elif filename.endswith(".webp"):
            response.headers["Content-Type"] = "image/webp"
        elif filename.endswith(".mp3"):
            response.headers["Content-Type"] = "audio/mpeg"

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.before_request
    def refresh_session():
        session.permanent = True
        session.modified = True
