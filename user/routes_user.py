"""
This module defines the routes for user-related actions in the Flask application.

Routes:
    /user/register (POST): Registers a new user.
    /user/signout: Signs out the current user.
    /user/login: Renders the login page.
    /user/login_attempt (POST): Attempts to log in a user.
"""
from flask import redirect, render_template, session
from .models import User

def add_user_routes(app):
    @app.route('/user/register_attempt', methods=['POST'])
    def register_user_attempt():
        """Registers a new user."""
        return User().register()

    @app.route('/user/register')
    def register():
        """Give page to register a new user."""
        return render_template('register.html')

    @app.route('/user/signout')
    def signout():
        """Signs out the current user."""
        return User().signout()

    @app.route('/user/login')
    def login():
        """Gives login form to user."""
        if "logged_in" in session:
            return redirect('/')
        return render_template('login.html')

    @app.route('/user/login_attempt', methods=['POST'])
    def login_user_attempt():
        """Processes login form."""
        return User().login()
