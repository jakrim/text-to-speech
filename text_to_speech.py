from elevenlabs import (
    generate,
    play,
    save,
    set_api_key,
    voices,
    Voice,
    VoiceSettings,
)
import os
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
import re
from google_drive_manager import GoogleDriveManager
import sys

# Load environment variables
load_dotenv()

class ElevenLabsManager:
    def __init__(self, api_key=None):
        """Initialize the ElevenLabs Manager with API key and default settings"""
        self.api_key = api_key or os.getenv('ELEVEN_LABS_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set ELEVEN_LABS_API_KEY environment variable or pass it directly.")

        set_api_key(self.api_key)
        self.base_dir = Path('audio_files')
        self.base_dir.mkdir(exist_ok=True)

        # Initialize Google Drive manager but don't authenticate yet
        self.drive_manager = None

    def init_drive_manager(self):
        """Initialize and authenticate Google Drive manager when needed"""
        if self.drive_manager is None:
            self.drive_manager = GoogleDriveManager()
            if not self.drive_manager.authenticate():
                print("\nFailed to authenticate with Google Drive. Files will be saved locally only.")
                return False
        return True

    def list_available_voices(self):
        """Get all available voices"""
        try:
            all_voices = voices()
            return all_voices
        except Exception as e:
            print(f"Error fetching voices: {str(e)}")
            return []

    def find_voice_by_name(self, voice_name):
        """Find a voice by its name"""
        all_voices = self.list_available_voices()
        for voice in all_voices:
            if voice.name.lower() == voice_name.lower():
                return voice
        return None

    def generate_audio(self, text, voice_name=None, voice_id=None, output_filename=None, output_dir=None, model="eleven_multilingual_v2", stability=0.5, similarity_boost=0.75, style=0.0):
        """Generate audio from text using specified voice and settings"""
        try:
            # First identify the question at the end before cleaning newlines
            original_text = text

            # The question is in the last part after the final \n\n
            parts = original_text.split("\\n\\n")
            if len(parts) > 1:
                last_part = parts[-1].strip()
                # Find the question in the last part
                if "?" in last_part:
                    # Get the sentence that ends with a question mark
                    sentences = re.split(r'(?<=[.!?])\s+', last_part)
                    for sentence in reversed(sentences):
                        if sentence.strip().endswith("?"):
                            question = sentence.strip()
                            # Remember the question for later formatting
                            question_to_format = question
                            break

            # Now clean the text of newlines
            text = text.replace("\\n\\n", " ")  # Replace literal \n\n string
            text = text.replace("\\n", " ")     # Replace literal \n string
            text = text.replace("\n\n", " ")    # Replace actual double newlines
            text = text.replace("\n", " ")      # Replace actual single newlines
            text = re.sub(r'\s+', ' ', text)    # Replace multiple spaces with a single space
            text = text.strip()                 # Remove leading/trailing whitespace

            # Format the identified question
            if 'question_to_format' in locals() and question_to_format in text:
                # Add sentence-final punctuation to enhance rising intonation
                formatted_question = f'; {question_to_format}'  # Semi-colon creates a pause and helps with rising intonation

                # Replace the question in the cleaned text
                text = text.replace(question_to_format, formatted_question)

                # Use a slightly lower stability for the entire text to allow more expressiveness
                stability = 0.4  # Balance between consistency and expressiveness

                # Use higher similarity boost to maintain voice characteristics
                similarity_boost = 0.85

            # Create voice settings
            voice_settings = VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=style
            )

            # Determine which voice to use
            if voice_id:
                # Use voice ID with custom settings
                selected_voice = Voice(voice_id=voice_id, settings=voice_settings)
            elif voice_name:
                # Find voice by name and create with custom settings
                voice = self.find_voice_by_name(voice_name)
                if voice:
                    selected_voice = Voice(voice_id=voice.voice_id, settings=voice_settings)
                else:
                    raise ValueError(f"Voice '{voice_name}' not found")
            else:
                # Use the first available voice if none specified
                available_voices = self.list_available_voices()
                if not available_voices:
                    raise ValueError("No voices available")
                selected_voice = Voice(voice_id=available_voices[0].voice_id, settings=voice_settings)

            # Generate the audio with custom voice settings
            audio = generate(
                text=text,
                voice=selected_voice,
                model=model
            )

            # Determine output directory
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = self.base_dir
            output_path.mkdir(exist_ok=True)

            # Save the audio file
            if output_filename:
                # Ensure filename is lowercase
                output_filename = output_filename.lower()
                final_path = output_path / f"{output_filename}.mp3"
            else:
                final_path = output_path / "output.mp3"

            save(audio, str(final_path))
            print(f"Created: {final_path}")

            return str(final_path)

        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            raise

    def process_text_file(self, file_path, voice_name=None, voice_id=None, upload_to_drive=True, stability=0.5, similarity_boost=0.75, style=0.0):
        """Process a text file and convert each line to speech.
        Each line represents a complete story, regardless of internal newlines."""
        try:
            # Verify the file exists
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as file:
                # Each line in the file is a separate story
                pieces = [line.strip() for line in file if line.strip()]

            if not pieces:
                raise ValueError("The input file is empty")

            # Get the filename without extension to use as the base for audio files
            file_stem = Path(file_path).stem.lower()  # Ensure lowercase
            # Create mentor-specific directory inside audio_files
            output_dir = self.base_dir / file_stem

            output_dir.mkdir(exist_ok=True, parents=True)
            generated_files = []

            # Generate all audio files
            print(f"\nProcessing {len(pieces)} stories...")
            for index, piece in enumerate(pieces, 1):
                if piece:  # Skip empty pieces
                    # Format index as two digits (01, 02, etc.)
                    filename = f"{file_stem}_{index:02d}"
                    try:
                        file_path = self.generate_audio(
                            text=piece,
                            voice_name=voice_name,
                            voice_id=voice_id,
                            output_filename=filename,
                            output_dir=output_dir,
                            stability=stability,
                            similarity_boost=similarity_boost,
                            style=style
                        )
                        generated_files.append(file_path)
                        print(f"Generated file {index}/{len(pieces)}: {filename}")
                    except Exception as e:
                        print(f"Error generating audio for story {index}: {str(e)}")

            # Upload to Google Drive if requested
            if upload_to_drive and generated_files:
                print(f"\nPreparing to upload files to Google Drive...")
                if self.init_drive_manager():
                    try:
                        uploaded_files = self.drive_manager.upload_folder(
                            str(output_dir),
                            file_stem  # Use the filename (without extension) as the mentor folder name
                        )
                        print(f"Successfully uploaded {len(uploaded_files)} files to Google Drive")
                        for file in uploaded_files:
                            print(f"Uploaded: {file['file_name']}")
                    except Exception as e:
                        print(f"\nError uploading to Google Drive: {str(e)}")
                        print("Files are still saved locally in the audio_files directory")
                else:
                    print("\nSkipping Google Drive upload due to authentication failure")
                    print(f"Files are saved locally in: {output_dir}")

            return generated_files

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return []

    def list_voices_info(self):
        """Print detailed information about available voices"""
        all_voices = self.list_available_voices()
        voice_info = []

        for voice in all_voices:
            info = {
                "name": voice.name,
                "voice_id": voice.voice_id,
                "category": voice.category,
                "description": voice.description
            }
            voice_info.append(info)

            print(f"\nVoice: {voice.name}")
            print(f"ID: {voice.voice_id}")
            print(f"Category: {voice.category}")
            print(f"Description: {voice.description}")
            print("-" * 50)

        return voice_info

def main():
    parser = argparse.ArgumentParser(description='Convert text to speech using Eleven Labs API')
    parser.add_argument('file_path', help='Path to the text file')
    parser.add_argument('--voice-name', help='Name of the voice to use')
    parser.add_argument('--voice-id', help='ID of the voice to use')
    parser.add_argument('--list-voices', action='store_true', help='List available voices')
    parser.add_argument('--api-key', help='Eleven Labs API key (optional if set in .env file)')
    parser.add_argument('--no-upload', action='store_true', help='Skip uploading to Google Drive')
    parser.add_argument('--stability', type=float, default=0.5, help='Voice stability (0.0-1.0). Lower values = more emotional range')
    parser.add_argument('--similarity-boost', type=float, default=0.75, help='Voice similarity boost (0.0-1.0)')
    parser.add_argument('--style', type=float, default=0.0, help='Style exaggeration (0.0-1.0)')

    args = parser.parse_args()

    try:
        manager = ElevenLabsManager(api_key=args.api_key)

        if args.list_voices:
            manager.list_voices_info()
            return

        manager.process_text_file(
            file_path=args.file_path,
            voice_name=args.voice_name,
            voice_id=args.voice_id,
            upload_to_drive=not args.no_upload,
            stability=args.stability,
            similarity_boost=args.similarity_boost,
            style=args.style
        )

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
