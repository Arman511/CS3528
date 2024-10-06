from dotenv import load_dotenv
from flask import Flask
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core import handlers

load_dotenv()

print(type(os.getenv("IS_GITHUB_ACTIONS")))