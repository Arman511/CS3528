"""
Handles the base routes, adds the module routes, and includes decorators 
to enforce user access levels.
"""

from functools import wraps
from flask import render_template, session, redirect
from user import routes_user
from students import routes_student
from opportunities import routes_opportunites
from skills import routes_skills
from courses import routes_courses
from course_modules import routes_modules
from employers import routes_employers


def allowed_file(filename, types):
    """Check if file type is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in types


# Decorators
def login_required(f):
    """
    This decorator ensures that a user is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)

        return redirect("/students/login")

    return wrap


def student_login_required(f):
    """
    This decorator ensures that a student is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "student_logged_in" in session:
            return f(*args, **kwargs)
        return redirect("/students/login")

    return wrap


def employers_login_required(f):
    """
    This decorator ensures that a employer is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "employer_logged_in" in session:
            return f(*args, **kwargs)
        return redirect("/employer/login")

    return wrap


def configure_routes(app):
    """Configures the routes for the given Flask application.
    This function sets up the routes for user and student modules by calling their respective
    route configuration functions. It also defines the home route and the privacy policy route.
    Args:
        app (Flask): The Flask application instance.
    Routes:
        /: The home route which needs the user to be logged in and renders the 'home.html' template.
        /privacy-policy: The privacy policy route which renders the 'privacy_policy.html' template.
    """

    routes_user.add_user_routes(app)
    routes_student.add_student_routes(app)
    routes_opportunites.add_opportunities_routes(app)
    routes_skills.add_skills_routes(app)
    routes_courses.add_course_routes(app)
    routes_modules.add_module_routes(app)
    routes_employers.add_employer_routes(app)

    @app.route("/")
    @login_required
    def index():
        """The home route which needs the user to be logged in and renders the 'home.html' template.

        Returns:
            str: Rendered HTML template for the home page.
        """
        return render_template("/user/home.html")

    @app.route("/privacy_policy")
    def privacy_policy():
        """The privacy policy route which renders the 'privacy_policy.html' template.

        Returns:
            str: Rendered HTML template for the privacy policy page.
        """
        return render_template("privacy_policy.html")

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
        session.clear()
        return redirect("/")
