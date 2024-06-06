from app import app
from prompts.prompt import Prompt

prompt_model = Prompt()

@app.route('/generate-image', methods=['POST'])
def generate_image():
  return prompt_model.generate_image()