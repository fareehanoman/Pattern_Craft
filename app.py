from flask import Flask, render_template, session, redirect, url_for
from functools import wraps
import pymongo

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
client = pymongo.MongoClient('localhost', 27017)
db = client.user_login_system

# Decorators
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

# Routes
from user import routes
from prompts import routes

# Sign up / Sign In Functionality
@app.route('/')
def landingpage():
  return render_template('landing-page.html')

@app.route('/login.html')
def loginpage():
  return render_template('login.html')

@app.route('/signup.html')
def signuppage():
  return render_template('signup.html')

# Frontend 
@app.route('/generated-pattern.html')
def generatedpattern():
  return render_template('generated-pattern.html')

@app.route('/gallery.html')
def gallery():
  return render_template('gallery.html')

@app.route('/about.html')
def about():
  return render_template('about.html')

@app.route('/index2.html/')
def index2():
  return render_template('index2.html')

if __name__ == '__main__':
    app.run(debug=True)
