#!/usr/bin/env python3
"""
Process all mentor text files in the mentors directory with appropriate voices.

This script helps automate the generation of audio files for all mentor text files
found in the mentors directory. It assigns appropriate voices to each mentor.
"""

import os
import subprocess
import glob
from pathlib import Path

# Configuration for each mentor file and the voice to use
MENTOR_VOICE_MAP = {
    "serena_williams.txt": "Natasha -  African American Woman",
    "usain_bolt.txt": "Jamahal",
    "tom_brady.txt": "Christian",
    # Add more mappings as needed
}

# Default voice settings
DEFAULT_STABILITY = 0.6
DEFAULT_SIMILARITY_BOOST = 0.75
DEFAULT_STYLE = 0.0

def get_mentor_files():
    """Get all text files in the mentors directory."""
    mentor_dir = Path("mentors")
    if not mentor_dir.exists():
        print(f"Error: Mentors directory not found: {mentor_dir}")
        return []

    return list(mentor_dir.glob("*.txt"))

def process_mentor(mentor_file, voice_name=None):
    """Process a single mentor file with the specified voice."""
    if not os.path.exists(mentor_file):
        print(f"Error: Mentor file not found: {mentor_file}")
        return False

    # Get the mentor filename
    mentor_filename = os.path.basename(mentor_file)

    # If voice not specified, try to get it from the mapping
    if not voice_name and mentor_filename in MENTOR_VOICE_MAP:
        voice_name = MENTOR_VOICE_MAP[mentor_filename]

    # If still no voice, use default
    if not voice_name:
        print(f"Warning: No voice specified for {mentor_filename}, using default voice")
        command = [
            "python", "text_to_speech.py", str(mentor_file),
            "--stability", str(DEFAULT_STABILITY),
            "--similarity-boost", str(DEFAULT_SIMILARITY_BOOST),
            "--style", str(DEFAULT_STYLE)
        ]
    else:
        print(f"Processing {mentor_filename} with voice: {voice_name}")
        command = [
            "python", "text_to_speech.py", str(mentor_file),
            "--voice-name", voice_name,
            "--stability", str(DEFAULT_STABILITY),
            "--similarity-boost", str(DEFAULT_SIMILARITY_BOOST),
            "--style", str(DEFAULT_STYLE)
        ]

    # Run the command
    try:
        result = subprocess.run(command, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error processing {mentor_filename}: {e}")
        return False

def main():
    """Main function to process all mentor files."""
    print("===== Processing All Mentor Files =====")

    # Get all mentor files
    mentor_files = get_mentor_files()
    if not mentor_files:
        print("No mentor files found in the mentors directory.")
        return

    print(f"Found {len(mentor_files)} mentor files to process.\n")

    # Process each mentor file
    successful = 0
    for mentor_file in mentor_files:
        mentor_filename = os.path.basename(mentor_file)
        print(f"------ Processing: {mentor_filename} ------")

        # Get the voice for this mentor
        voice_name = MENTOR_VOICE_MAP.get(mentor_filename)

        # Process the mentor file
        if process_mentor(mentor_file, voice_name):
            successful += 1
            print(f"Successfully processed {mentor_filename}")
        else:
            print(f"Failed to process {mentor_filename}")

        print()  # Add a blank line for separation

    print(f"===== Processing Complete: {successful}/{len(mentor_files)} files processed successfully =====")

if __name__ == "__main__":
    main()
