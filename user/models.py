
"""
This module defines the User class which handles user authentication and session management.
Classes:
  User: A class to handle user registration, login, session management, and signout.
Methods:
  start_session(user):
    Starts a session for the given user by storing user information in the session.
    Args:
      user (dict): A dictionary containing user information.
    Returns:
      Response: A JSON response with user information and HTTP status code 200.
  register():
    Registers a new user with the provided name, email, and password.
    Returns:
      Response: A JSON response indicating the success or failure of the registration process.
  signout():
    Signs out the current user by clearing the session.
    Returns:
      Response: A redirect response to the home page.
  login():
    Logs in a user by validating their credentials.
    Returns:
      Response: A JSON response indicating the success or failure of the login process.
"""
from flask import jsonify, request, session, redirect
import uuid
# from passlib.hash import pbkdf2_sha256 

class User:
  """
  A class used to represent a User and handle user-related operations such as session management, registration, login, and signout."""

  def start_session(self, user):
    """Starts a session for the given user by removing the password from the user dictionary, setting session variables, and returning a JSON response."""
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    return jsonify(user), 200

  def register(self):
    """Registers a new user by creating a user dictionary with a unique ID, name, email, and password, and returns a JSON response indicating failure."""
    user = {
      "_id": uuid.uuid4().hex,
      "name": request.form.get('name'),
      "email": request.form.get('email'),
      "password": request.form.get('password')
    }

    return jsonify({ "error": "Signup failed" }), 400
  
  def signout(self):
    """Clears the current session and redirects to the home page."""
    session.clear()
    return redirect('/')
  
  def login(self):
    """Validates user credentials and returns a JSON response indicating invalid login credentials."""
    # todo: validate user
     
    return jsonify({ "error": "Invalid login credentials" }), 401