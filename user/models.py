from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db
import re
import uuid

class User:

  def start_session(self, user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    return jsonify(user), 200

  def validate_email(self, email):
    email_regex = r'^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$'
    return re.match(email_regex, email)

  def signup(self):
    print(request.form)

    # Create the user object
    user = {
      "_id": uuid.uuid4().hex,
      "name": request.form.get('name'),
      "email": request.form.get('email'),
      "password": request.form.get('password')
    }

    # Validate email
    if not self.validate_email(user['email']):
      return jsonify({ "error": "Invalid email address" }), 400

    # Validate password length
    if len(user['password']) < 8:
      return jsonify({ "error": "Password must be at least 8 characters long" }), 400

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

    # Check for existing email address
    if db.users.find_one({ "email": user['email'] }):
      return jsonify({ "error": "Email address already in use" }), 400

    if db.users.insert_one(user):
      return self.start_session(user)

    return jsonify({ "error": "Signup failed" }), 400
  
  # Redirects to landing page
  def signout(self):
    session.clear()
    return redirect('/')
  
  def login(self):
    email = request.form.get('email')
    password = request.form.get('password')

    # Validate email
    if not self.validate_email(email):
      return jsonify({ "error": "Invalid email address" }), 400

    # Validate password length
    if len(password) < 8:
      return jsonify({ "error": "Password must be at least 8 characters long" }), 400

    user = db.users.find_one({
      "email": email
    })

    if user and pbkdf2_sha256.verify(password, user['password']):
      return self.start_session(user)
    
    return jsonify({ "error": "Invalid login credentials" }), 401
