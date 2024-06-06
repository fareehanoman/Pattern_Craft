from flask import Flask, jsonify, request, session
from app import db
import uuid
import requests
import base64

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer YOUR_API_TOKEN"}

class Prompt:

  def generate_image(self):
    # Check if user is logged in
    if not session.get('logged_in'):
      return jsonify({ "error": "Unauthorized" }), 401

    # Get the prompt from the request
    prompt_text = request.json.get('prompt')
    if not prompt_text:
      return jsonify({ "error": "No prompt provided" }), 400

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
        "created_at": request.form.get('created_at')
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
