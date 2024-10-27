from core import handlers
from .models import Employer
from flask import request, render_template
def add_employer_routes(app):
    @app.route("/employers/login", methods = ["GET", "POST"])
    def employer_login():
        if request.method == "POST":
            return Employer().employer_login()
             
        return render_template("employers/employer_login.html")