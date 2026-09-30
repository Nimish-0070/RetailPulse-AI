import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

model = "gemini-3.8-flash"

for attempt in range(1, 6):
    print(f"\nAttempt {attempt}/5...")

    try:
        response = client.models.generate_content(
            model=model,
            contents="Say exactly: RetailPulse-AI Gemini connection successful."
        )

        print("\nSUCCESS!")
        print(response.text)
        break

    except errors.ServerError as e:
        if attempt == 5:
            print("\nGemini is still unavailable after 5 attempts.")
            print("Error:", e)
            break

        wait_time = 2 ** attempt
        print(f"Gemini returned 503. Retrying in {wait_time} seconds...")
        time.sleep(wait_time)

    except Exception as e:
        print("\nUnexpected error:")
        print(e)
        break