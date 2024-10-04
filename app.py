"""
This module initializes a Flask application, connects to a MongoDB database, and defines routes with login-required decorators.
Modules:
    flask: A micro web framework for Python.
    functools: Higher-order functions and operations on callable objects.
    pymongo: Python driver for MongoDB.
    dotenv: Reads key-value pairs from a .env file and can set them as environment variables.
    os: Provides a way of using operating system dependent functionality.
    user.routes: Custom module for user-related routes.
Functions:
    login_required(f): A decorator to ensure that a user is logged in before accessing certain routes.
Routes:
    /: The home route which requires the user to be logged in and renders the 'home.html' template.
"""
import os
from dotenv import load_dotenv
from flask import Flask
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core import handlers

load_dotenv()
 
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 # 16 MB
handlers.configure_routes(app)

if __name__ == "__main__":
    app.run()