from flask import Flask, render_template
from app import app
from user.models import User

@app.route('/user/register', methods=['POST'])
def signup():
  return User().register()

@app.route('/user/signout')
def signout():
  return User().signout()

@app.route('/user/login')
def login():
  return render_template('login.html')

@app.route('/user/login_attempt', methods=['POST'])
def login_attempt():
  return User().login()