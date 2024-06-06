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
# Assuming user.py and prompts.py are in the same directory as this script
import user
import prompts

# Sign up / Sign In Functionality
@app.route('/')
def home():
    return render_template('landing-page.html')

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

# Uncomment and modify this route if you need the dashboard
#@app.route('/dashboard/')
#@login_required
#def dashboard():
#    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
