import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("AIzaSyDZppleQ_jtFcvNhozIT6rBzECQQYagmZU"))

model = genai.GenerativeModel("gemini-pro")

def call_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"
