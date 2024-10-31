"""Routes for employers module"""

from flask import jsonify, request, render_template, session
from core import handlers
from .models import Employers


def add_employer_routes(app):
    """Add employer routes."""

    @app.route("/employers/login", methods=["GET", "POST"])
    def employer_login():
        if request.method == "POST":
            return Employers().employer_login()

        return render_template("employers/employer_login.html")

    @app.route("/employers/home", methods=["GET"])
    @handlers.employers_login_required
    def employer_home():
        return render_template(
            "employers/employer_home.html", employer=session["employer"]
        )

    @app.route("/employers/otp", methods=["POST"])
    def employer_otp():
        if "OTP" not in session:
            return jsonify({"error": "OTP not sent."}), 400
        elif request.form.get("otp") != session["OTP"]:
            return jsonify({"error": "Invalid OTP."}), 400

        return Employers().start_session()

    @app.route("/employers/add_employer", methods=["GET", "POST"])
    @handlers.login_required
    def add_employer():
        if request.method == "POST":
            return Employers().register_employer()
        return render_template("employers/add_employer.html")
