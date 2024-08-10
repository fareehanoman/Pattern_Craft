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
headers = {"Authorization": f"API Token Bearer"}

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
@login_required
def generatedpattern():
    return render_template('generated-pattern.html')

@app.route('/gallery.html')
@login_required                     # Added login decorator to protect routes
def gallery():
    return render_template('gallery.html')

@app.route('/about.html')
@login_required
def about():
    return render_template('about.html')

@app.route('/home.html')
@login_required
def home():
    return render_template('home.html')

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    if not session.get('logged_in'):
        return redirect(url_for('loginpage'))

    prompt_text = request.form.get('prompt')
    design = request.form.get('design')
    colour = request.form.get('colour')
    bg_colour = request.form.get('bg_colour')
    additional = request.form.get('additional')

    # Logging the received form data
    print(f"Received form data - prompt: {prompt_text}, design: {design}, colour: {colour}, bg_colour: {bg_colour}, additional: {additional}")

    if prompt_text:
        print("Calling generate_image function")
        image_bytes = Prompt.generate_image(prompt_text)
    elif design or colour or bg_colour or additional:
        print("Calling generate_image_v2 function")
        prompt_text = f"{design} pattern"
        if colour:
            prompt_text += f" having {colour} colour"
        if bg_colour:
            prompt_text += f" and {bg_colour} background"
        if additional:
            prompt_text += f" with {additional}"
        prompt_text += " for textile"
        image_bytes = Prompt.generate_image(prompt_text)
    else:
        return redirect(url_for('home'))

    if image_bytes:
        base64_bytes = base64.b64encode(image_bytes)
        base64_string = base64_bytes.decode('utf-8')
        
        prompt = {
            "_id": uuid.uuid4().hex,
            "user_id": session['user']['sub'],
            "prompt": prompt_text,
            "image": base64_string,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        db.prompts.insert_one(prompt)
        return render_template('generated-pattern.html', image_data=base64_string, prompt=prompt_text)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
