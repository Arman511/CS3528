from flask import Flask, render_template, session, redirect
from functools import wraps
import pymongo
from dotenv import load_dotenv
import os
load_dotenv()
 
app = Flask(__name__)

client = pymongo.MongoClient(os.getenv(("DB_LOGIN")))
from user import routes
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Decorators
def login_required(f):
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
    return render_template('home.html')
 