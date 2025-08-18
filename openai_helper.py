import openai
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Set the API key
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai_chat(user_message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for ASPR Treatment Locations."},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"
