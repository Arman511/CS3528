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
from functools import wraps
import pymongo
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect


load_dotenv()
 
app = Flask(__name__)

client = pymongo.MongoClient(os.getenv(("DB_LOGIN")))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except pymongo.errors.ConfigurationError as e:
    print(f"Configuration error: {e}")
except pymongo.errors.OperationFailure as e:
    print(f"Operation failure: {e}")

# Decorators
def login_required(f):
    """This decorator ensures that a user is logged in before accessing certain routes.
    """
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/user/login')
  
    return wrap
    
@app.route('/')
@login_required
def index():
    """The home route which requires the user to be logged in and renders the 'home.html' template.

    Returns:
        str: Rendered HTML template for the home page.
    """
    return render_template('home.html')
 