"""
This module initializes a Flask application, connects to a MongoDB database,
and defines routes with login-required decorators.
"""
import os
import sys
from dotenv import load_dotenv
from flask import Flask
from .core import handlers
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB
handlers.configure_routes(app)

if __name__ == "__main__":
    app.run()
