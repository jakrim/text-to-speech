# Text to Speech Converter

This script converts text from a spreadsheet (CSV or Excel) to speech using Google's Text-to-Speech (gTTS) service.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The script accepts both CSV and Excel files. Your spreadsheet should have at least one column containing the text you want to convert to speech.

Basic usage:
```bash
python text_to_speech.py your_spreadsheet.csv "Text Column"
```

With optional filename column and language:
```bash
python text_to_speech.py your_spreadsheet.xlsx "Text Column" --filename-column "Filename Column" --language "en"
```

### Arguments:
- `file_path`: Path to your spreadsheet file (required)
- `text_column`: Name of the column containing text to convert (required)
- `--filename-column`: Name of the column containing filenames (optional)
- `--language`: Language code (optional, defaults to 'en' for English)

The script will create an `audio_files` directory and save all generated MP3 files there.

## Supported Languages

The script supports all languages available in Google Text-to-Speech. Some common language codes:
- English: 'en'
- Spanish: 'es'
- French: 'fr'
- German: 'de'
- Italian: 'it'
- Japanese: 'ja'
- Korean: 'ko'
- Chinese: 'zh'
