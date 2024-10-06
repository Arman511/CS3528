from flask import Flask, render_template
import sys
import os
from app import app


def test_create_app():
    client = app.test_client()
    url = ""
    
    response = client.get(url)
    
    
