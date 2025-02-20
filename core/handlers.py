"""
Handles the base routes, adds the module routes, and includes decorators
to enforce user access levels.
"""

from functools import wraps
from flask import jsonify, render_template, session, redirect
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
        elif "superuser" in session:
            return redirect("/user/search")
        elif "employer_logged_in" in session:
            return redirect("/employers/home")
        return redirect("/students/login")

    return wrap


def is_admin():
    return session.get("logged_in") is not None


def student_login_required(f):
    """
    This decorator ensures that a student is logged in before accessing certain routes.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "student_logged_in" in session:
            return f(*args, **kwargs)
        elif "employer_logged_in" in session:
            return redirect("/employers/home")
        elif "superuser" in session:
            return redirect("/user/search")
        elif "logged_in" in session:
            return redirect("/")
        return redirect("/students/login")

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
        elif "superuser" in session:
            return redirect("/user/search")
        elif "logged_in" in session:
            return redirect("/")

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
        elif "superuser" in session:
            return redirect("/user/search")
        return redirect("/students/login")

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
    user = session.get("user")
    employer = session.get("employer")
    student = session.get("student")
    superuser = session.get("superuser")

    # Determine user_type based on session data
    if user:
        user_type = "admin"
    elif employer:
        user_type = "employer"
    elif student:
        user_type = "student"
    elif superuser:
        user_type = "superuser"
    else:
        user_type = None
    return user_type


def configure_routes(app, cache):
    """Configures the routes for the given Flask application.
    This function sets up the routes for user and student modules by calling their respective
    route configuration functions. It also defines the home route and the privacy policy route.
    Args:
        app (Flask): The Flask application instance.
    Routes:
        /: The home route which needs the user to be logged in and renders the 'home.html' template.
        /privacy-policy: The privacy policy route which renders the 'privacy_policy.html' template.
    """

    routes_user.add_user_routes(app, cache)
    routes_student.add_student_routes(app)
    routes_opportunities.add_opportunities_routes(app)
    routes_skills.add_skills_routes(app)
    routes_courses.add_course_routes(app)
    routes_modules.add_module_routes(app)
    routes_employers.add_employer_routes(app)
    routes_superuser.add_superuser_routes(app)

    @app.route("/")
    @login_required
    def index():
        """The home route which needs the user to be logged in and renders the 'home.html' template.

        Returns:
            str: Rendered HTML template for the home page.
        """
        return render_template("/user/home.html", user_type="admin")

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

    @app.route("/favicon.ico")
    def favicon():
        """The favicon route which renders the 'favicon.ico' template.

        Returns:
            str: Rendered favicon.ico template.
        """
        return app.send_static_file("favicon.ico")

    @app.route("/404")
    def error_404():
        """The 404 route which renders the '404.html' template.

        Returns:
            str: Rendered 404.html template.
        """
        return render_template("404.html", user_type=get_user_type()), 404

    @app.route("/500")
    def error_500():
        """The 500 route which renders the '500.html' template.

        Returns:
            str: Rendered 500.html template.
        """
        return render_template("500.html", user_type=get_user_type()), 500

    @app.route("/sitemap")
    @app.route("/sitemap/")
    @app.route("/sitemap.xml")
    def sitemap():
        """
        Route to dynamically generate a sitemap of your website/application.
        lastmod and priority tags omitted on static pages.
        lastmod included on dynamic content such as blog posts.
        """
        from flask import make_response, request, render_template
        from urllib.parse import urlparse

        host_components = urlparse(request.host_url)
        host_base = host_components.scheme + "://" + host_components.netloc

        # Static routes with static content
        static_urls = list()
        for rule in app.url_map.iter_rules():
            if not str(rule).startswith("/admin") and not str(rule).startswith("/user"):
                if "GET" in rule.methods and len(rule.arguments) == 0:
                    url = {"loc": f"{host_base}{str(rule)}"}
                    static_urls.append(url)

        xml_sitemap = render_template(
            "sitemap.xml",
            static_urls=static_urls,
            host_base=host_base,
        )
        response = make_response(xml_sitemap)
        response.headers["Content-Type"] = "application/xml"

        return response
