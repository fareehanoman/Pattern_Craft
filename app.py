from flask import Flask, render_template, session, redirect, url_for, request
from functools import wraps
import pymongo
import uuid
import requests
import base64
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'

# Database
client = pymongo.MongoClient('localhost', 27017)
db = client.user_login_system

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer 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"}

# Decorators
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')
    return wrap

class Prompt:
    @staticmethod
    def generate_image(prompt_text):
        response = requests.post(
            HUGGINGFACE_API_URL,
            headers=headers,
            json={"inputs": prompt_text}
        )
        if response.status_code == 200:
            return response.content
        return None

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

@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/generate', methods=['POST'])
def generate():
    if not session.get('logged_in'):
        return redirect(url_for('loginpage'))

    prompt_text = request.form.get('prompt')
    #print(prompt_text)
    if not prompt_text:
        return redirect(url_for('home'))

    image_bytes = Prompt.generate_image(prompt_text)
    if image_bytes:
        base64_bytes = base64.b64encode(image_bytes)
        base64_string = base64_bytes.decode('utf-8')
        
        prompt = {
            "_id": uuid.uuid4().hex,
            "user_id": session['user']['_id'],
            "prompt": prompt_text,
            "image": base64_string,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        db.prompts.insert_one(prompt)
        return render_template('generated-pattern.html', image_data=base64_string, prompt=prompt_text)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
