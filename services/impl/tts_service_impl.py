import requests
import os
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_1dd1f02fe206b1602ee7df99144ac6dba61c751cb15b94ad")
VOICE_ID = os.getenv("VOICE_ID", "mRdG9GYEjJmIzqbYTidv")

class TTSServiceImpl:
    def synthesize_speech(self, text: str) -> bytes:
        # Check if environment variables are set
        if not ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set")
        if not VOICE_ID:
            raise ValueError("VOICE_ID environment variable is not set")
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            # Add timeout to prevent hanging
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.Timeout:
            print("Error: ElevenLabs API request timed out")
            raise
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to ElevenLabs API")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error calling ElevenLabs API: {e}")
            raise 