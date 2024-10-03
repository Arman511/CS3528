"""
This module defines the routes for user-related actions in the Flask application.

Routes:
    /user/register (POST): Registers a new user.
    /user/signout: Signs out the current user.
    /user/login: Renders the login page.
    /user/login_attempt (POST): Attempts to log in a user.
"""
from flask import render_template
from app import app
from user.models import User

@app.route('/user/register', methods=['POST'])
def signup():
    """Registers a new user."""
    return User().register()

@app.route('/user/signout')
def signout():
    """Signs out the current user."""
    return User().signout()

@app.route('/user/login')
def login():
    """Gives login form to user."""
    return render_template('login.html')

@app.route('/user/login_attempt', methods=['POST'])
def login_attempt():
    """Processes login form."""
    return User().login()
