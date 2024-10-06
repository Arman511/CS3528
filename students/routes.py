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
from app import app
from core import handlers


@app.route('/students/add_student', methods=['POST'])
@handlers.login_required
def register_student_attempt():
    """Adding new student."""
    return Student().add_student()

@app.route('/students/upload_csv', methods=['POST'])
@handlers.login_required
def upload_csv():
    return Student().import_from_csv()


@app.route('/students/upload_xlsx', methods=['POST'])
@handlers.login_required
def upload_xlsx():
    return Student().import_from_xlsx()

@app.route('/students/get_student_by_id', methods=['GET'])
@handlers.login_required
def get_student_by_id():
    """Getting student."""
    return Student().get_student_by_id()

    
        
