import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not found in .env file.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            
        self.model_id = 'gemini-3.1-pro-preview'
        
        self.default_prompt = (
            "Please explain this to me. Also try not to be very verbose and give some examples. Many thanks"
        )

    def query(self, image_pil, prompt=None):
        if not self.client:
            return "**Error:** `GEMINI_API_KEY` is missing. Please add it to the `.env` file in the application directory."
            
        if not prompt:
            prompt = self.default_prompt
            
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[image_pil, prompt],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level="HIGH"
                    )
                )
            )
            return response.text
        except Exception as e:
            return f"**Error communicating with AI:** {e}"

if __name__ == "__main__":
    # Simple test (requires a test.png file and a valid API key)
    from PIL import Image
    try:
        img = Image.new('RGB', (100, 100), color = 'white')
        client = AIClient()
        print("Testing AI Client (might fail if no API key is set)...")
        # response = client.query(img)
        # print("Response:", response)
        print("AI Client initialized successfully.")
    except Exception as e:
        print(f"Test failed: {e}")
