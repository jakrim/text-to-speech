# Text to Speech Converter using ElevenLabs API

This application converts text to speech using the ElevenLabs API. It processes text files where each line represents a separate piece of content to be converted to audio.

## Required Dependencies

Install the required dependencies:
```bash
pip install -r requirements.txt
```

This project uses ElevenLabs API version 1.55.0 or newer.

## Directory Structure

The application uses or creates the following directories:

- `audio_files/`: Main directory where all generated audio files are stored
  - Inside this directory, subdirectories are created for each text file processed (named after the file)
- `mentors/`: Contains text files with content to be converted to speech
  - Each line in these text files will be converted to a separate audio file
- `.env`: Contains your ElevenLabs API key (not tracked by Git)
- `credentials.json`: Google Drive API credentials file (not tracked by Git)
- `token.pickle`: Google Drive authentication token (not tracked by Git)

## How It Works

1. **Text File Format**:
   - Create a text file with each line representing a separate piece of content
   - Each line will be converted to a separate MP3 file
   - The application cleans text by removing newlines and extra spaces
   - Questions in the text are automatically detected and formatted for better intonation

2. **Audio Generation**:
   - Files are saved in the format: `[filename]_[index].mp3`
   - For example, the 1st line from `michael_jordan.txt` becomes `michael_jordan_01.mp3`
   - High-quality audio at 44.1kHz, 128kbps MP3 format

3. **Google Drive Integration**:
   - Optionally uploads generated audio files to Google Drive
   - Creates a folder structure on Drive: `mentors_audio/[filename]/`
   - Note: Google Drive integration requires proper credentials setup

## Usage

Basic usage:
```bash
python text_to_speech.py your_text_file.txt
```

With voice specification:
```bash
python text_to_speech.py your_text_file.txt --voice-name "Rachel"
```

List available voices:
```bash
python text_to_speech.py dummy.txt --list-voices
```

### Arguments:
- `file_path`: Path to your text file (required)
- `--voice-name`: Name of the ElevenLabs voice to use
- `--voice-id`: ID of the ElevenLabs voice to use
- `--no-upload`: Skip uploading to Google Drive
- `--stability`: Voice stability (0.0-1.0). Lower values = more emotional range
- `--similarity-boost`: Voice similarity boost (0.0-1.0)
- `--style`: Style exaggeration (0.0-1.0)
- `--no-speaker-boost`: Disable speaker boost (improves clarity for numbers and complex words)
- `--api-key`: ElevenLabs API key (optional if set in .env file)

## Voice Settings Explained

- **Stability (default: 0.5)**: Controls how consistent the voice sounds. Lower values allow more variation and expressiveness, higher values provide more consistent pronunciation.

- **Similarity Boost (default: 0.75)**: Determines how closely the voice matches the original voice. Higher values make the voice more consistent with its base sound.

- **Style (default: 0.0)**: Controls the amount of style transfer or character to apply to the voice. At 0.0, the style is neutral.

- **Speaker Boost (enabled by default)**: Enhances the clarity of speech, particularly for numbers and complex words. This helps produce clearer and more articulate speech. Use `--no-speaker-boost` to disable.

## Recommended Voice Settings

For optimal results:
- For conversational content: `--stability 0.6 --similarity-boost 0.75 --style 0.0`
- For emotional content: `--stability 0.4 --similarity-boost 0.8 --style 0.0`
- For clear educational content: `--stability 0.7 --similarity-boost 0.7 --style 0.0`

## Environment Setup

Create a `.env` file with your ElevenLabs API key:
```
ELEVEN_LABS_API_KEY=your_api_key_here
```

## Google Drive Integration

To use the Google Drive upload functionality:

1. Create a Google Cloud project and enable the Google Drive API
2. Create OAuth 2.0 credentials and download as `credentials.json`
3. Place `credentials.json` in the root directory of this project
4. The first time you run the script with uploads, it will prompt for authentication

Note: All Google Drive credentials are excluded from Git tracking for security.

