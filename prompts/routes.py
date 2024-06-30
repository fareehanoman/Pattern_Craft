from app import app
from prompts.prompt import Prompt

prompt_model = Prompt()

@app.route('/generate-image', methods=['POST'])
def generate_image():
  return prompt_model.generate_image()

@app.route('/generate-image-v2', methods=['POST'])
def generate_image_v2():
  return prompt_model.generate_image_v2()

@app.route('/get-user-prompts', methods=['POST'])
def get_user_prompts():
  return prompt_model.get_user_prompts()