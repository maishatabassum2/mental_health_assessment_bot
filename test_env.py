import os
from dotenv import load_dotenv
load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("OPENAI_API_KEY is loaded successfully!")
else:
    print("OPENAI_API_KEY is missing or not loaded.")

    print(f"OPENAI_API_KEY: {api_key}")