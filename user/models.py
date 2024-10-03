
"""
This module defines the User class which handles user authentication and session management.
"""
from flask import jsonify, request, session, redirect
from ..core import database
from passlib.hash import pbkdf2_sha256
import uuid
# from passlib.hash import pbkdf2_sha256

class User:
    """A class used to represent a User and handle user-related operations 
    such as session management, registration, login, and signout."""
    def start_session(self, user):
        """Starts a session for the given user by removing the password from the 
        user dictionary, setting session variables, and returning a JSON response."""
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200

    def register(self):
        """Registers a new user by creating a user dictionary with a unique ID, 
        name, email, and password, and returns a JSON response indicating failure."""
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }
        if database.users_collection.find_one({"email": request.form.get('email')}):
            return jsonify({"error": "Email address already in use"}), 400
        
        user['password'] = pbkdf2_sha256.hash(user['password'])
        database.users_collection.insert_one(user)
        
        if user:
            return self.start_session(user)
    
        return jsonify({"error": "Signup failed"}), 400
    
    def signout(self):
        """Clears the current session and redirects to the home page."""
        session.clear()
        return redirect('/')

    def login(self):
        """Validates user credentials and returns a JSON response indicating 
        invalid login credentials."""
        session.clear()
        user = database.users_collection.find_one({"email": request.form.get("email")})
        
        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.start_session(user)

        return jsonify({"error": "Invalid login credentials"}), 401