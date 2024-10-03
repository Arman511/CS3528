"""
This module defines the routes for user-related actions in the Flask application.

Routes:
    /user/register (POST): Registers a new user.
    /user/signout: Signs out the current user.
    /user/login: Renders the login page.
    /user/login_attempt (POST): Attempts to log in a user.
"""
from flask import render_template, request
from .models import Student
from ..app import app
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/students/add_student', methods=['POST'])
def register_attempt():
    """Adding new student."""
    return Student().add_student()

@app.route('/students/upload_csv', methods=['POST'])
def upload_csv():
    return Student().import_from_csv()


@app.route('/students/upload_xlsx', methods=['POST'])
def upload_xlsx():
    return Student().import_from_xlsx()

    
        
