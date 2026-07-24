import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

response = requests.get(
    "https://generativelanguage.googleapis.com/v1beta/models",
    params={"key": api_key},
    timeout=30,
)

print("Status:", response.status_code)
print(response.text)