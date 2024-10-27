from core import handlers
from flask import request, render_template
from .models import Employers


def add_employer_routes(app):
    @app.route("/employers/login", methods=["GET", "POST"])
    def employer_login():
        if request.method == "POST":
            return Employers().employer_login()

        return render_template("employers/employer_login.html")
