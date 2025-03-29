from elevenlabs import voices, set_api_key
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ELEVEN_LABS_API_KEY')
set_api_key(api_key)

all_voices = voices()
print("\nAvailable voices:")
for voice in all_voices:
    print(f"- {voice.name}")
