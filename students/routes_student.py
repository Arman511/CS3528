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
from core import handlers
from ..courses.models import Course
from ..skills.models import Skill

def add_student_routes(app):
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
    
    @app.route('/students/search')
    @handlers.login_required
    def search_page():
        """Getting student."""
        return render_template("search_student.html",skills=Skill().get_skills(),courses=Course().get_courses())
    
    @app.route('/students/search_students', methods=['POST'])
    @handlers.login_required
    def search_students():
        """Getting student."""
        return Student().search_students()
    
    @app.route('/students/delete_student/<int:student_id>', methods=['DELETE'])
    @handlers.login_required
    def delete_student(student_id):
        """Delete student."""
        return Student().delete_student_by_id(student_id)

    @app.route('/student/update/<int:student_id>', methods=['GET', 'POST'])
    @handlers.login_required
    def update_student(student_id):
        """Update student."""
        if request.method == 'POST':
            return Student().update_student_by_id(student_id, request.form)
        student = Student().get_student_by_id(student_id)
        
        return render_template("update_student.html", student=student,skills=Skill().get_skills(),courses=Course().get_courses())
    
        
