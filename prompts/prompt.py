from flask import Flask, jsonify, request, session
from app import db
import uuid
import requests
import base64
from datetime import datetime, timezone

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"YOUR_API_TOKEN"}

class Prompt:

  def generate_image(self):
    # Check if user is logged in
    if not session.get('logged_in'):
      return jsonify({ "error": "Unauthorized" }), 401

    # Get the prompt from the request
    prompt_text = request.json.get('prompt')
    if not prompt_text:
      return jsonify({ "error": "No prompt provided" }), 400

    # Add "pattern for textile" if not already present
    keywords = ["pattern", "textile"]
    if not any(keyword in prompt_text.lower() for keyword in keywords):
        prompt_text += " pattern for textile"

    # Call Hugging Face API to generate the image
    response = requests.post(
      HUGGINGFACE_API_URL,
      headers=headers,
      json={"inputs": prompt_text}
    )

    if response.status_code == 200:
      # Handle the response content
      image_bytes = response.content

      # Convert image bytes to base64 encoded string
      base64_bytes = base64.b64encode(image_bytes)
      base64_string = base64_bytes.decode('utf-8')

      # Create the prompt object
      prompt = {
        "_id": uuid.uuid4().hex,
        "user_id": session['user']['_id'],
        "prompt": prompt_text,
        "image": base64_string,
        "created_at": datetime.now(timezone.utc).isoformat()  # Use current datetime in UTC
      }

      # Save the prompt to the database
      if db.prompts.insert_one(prompt):
        return jsonify({ 
          "message": "Image Generated Successfully", 
          "image_data": base64_string, 
          "prompt": prompt_text 
        }), 201

      return jsonify({ "error": "Failed to save prompt" }), 500

    return jsonify({ "error": "Failed to generate image" }), response.status_code

  def generate_image_v2(self):
    # Check if user is logged in
    if not session.get('logged_in'):
      return jsonify({ "error": "Unauthorized" }), 401

    # Get the prompt from the request
    design = request.json.get('design')
    colour = request.json.get('colour')
    bg_colour = request.json.get('bg_colour')
    additional = request.json.get('additional')

    if not design:
      return jsonify({ "error": "No design provided" }), 400

    # Combine variables into a single prompt
    prompt_text = f"{design} pattern"
    if colour:
        prompt_text += f" having {colour} colour"
    if bg_colour:
        prompt_text += f" and {bg_colour} background"
    if additional:
        prompt_text += f" with {additional}"

    prompt_text += " for textile"

    # Call Hugging Face API to generate the image
    response = requests.post(
      HUGGINGFACE_API_URL,
      headers=headers,
      json={"inputs": prompt_text}
    )

    if response.status_code == 200:
      # Handle the response content
      image_bytes = response.content

      # Convert image bytes to base64 encoded string
      base64_bytes = base64.b64encode(image_bytes)
      base64_string = base64_bytes.decode('utf-8')

      # Create the prompt object
      prompt = {
        "_id": uuid.uuid4().hex,
        "user_id": session['user']['_id'],
        "prompt": prompt_text,
        "image": base64_string,
        "created_at": datetime.now(timezone.utc).isoformat()  # Use current datetime in UTC
      }

      # Save the prompt to the database
      if db.prompts.insert_one(prompt):
        return jsonify({ 
          "message": "Image Generated Successfully", 
          "image_data": base64_string, 
          "prompt": prompt_text 
        }), 201

      return jsonify({ "error": "Failed to save prompt" }), 500

    return jsonify({ "error": "Failed to generate image" }), response.status_code

  def get_user_prompts(self):
    # Check if user is logged in
    if not session.get('logged_in'):
        return jsonify({ "error": "Unauthorized" }), 401
    
    # Get the user id from the session
    user_id = session['user']['_id']
    
    # Query the database for prompts by this user, sorted in descending order by created_at
    user_prompts = db.prompts.find({"user_id": user_id}).sort("created_at", -1)
    
    # Convert the cursor to a list of dictionaries
    prompts_list = []
    for prompt in user_prompts:
        prompt['_id'] = str(prompt['_id'])  # Convert ObjectId to string if necessary
        prompts_list.append(prompt)
    
    return jsonify({ "prompts": prompts_list }), 200
