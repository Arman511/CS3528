"""Routes for employers module"""

import os
from flask import jsonify, request, render_template, session
from itsdangerous import URLSafeSerializer
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
        otp_serializer = URLSafeSerializer(str(os.getenv("SECRET_KEY", "secret")))

        if "OTP" not in session:
            return jsonify({"error": "OTP not sent."}), 400
        elif request.form.get("otp") != otp_serializer.loads(session["OTP"]):
            return jsonify({"error": "Invalid OTP."}), 400

        return Employers().start_session()

    @app.route("/employers/add_employer", methods=["GET", "POST"])
    @handlers.login_required
    def add_employer():
        if request.method == "POST":
            return Employers().register_employer()
        return render_template("employers/add_employer.html")
