import os
import json
import webbrowser
from pathlib import Path

def create_credentials_template():
    """Create the credentials.json template"""
    credentials = {
        "installed": {
            "client_id": "",
            "project_id": "tactical-snow-433017-h5",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "",
            "redirect_uris": ["http://localhost"]
        }
    }

    with open('credentials.json', 'w') as f:
        json.dump(credentials, f, indent=2)

    print("\nCreated credentials.json template")
    print("Please fill in the client_id and client_secret from the Google Cloud Console")

def setup_instructions():
    """Print setup instructions"""
    print("\n=== Google Drive API Setup Instructions ===")
    print("\nIMPORTANT: Make sure you're logged into Google Cloud Console with jesse@getmentors.ai")
    print("If you're currently logged in with a different account, please log out and switch accounts first.")

    print("\n1. Set up project access:")
    print("   a. Go to IAM & Admin > IAM:")
    print("      https://console.cloud.google.com/iam-admin/iam?project=tactical-snow-433017-h5")
    print("   b. Click '+ GRANT ACCESS'")
    print("   c. Enter your email: jesse@getmentors.ai")
    print("   d. Add these roles:")
    print("      - Project Owner")
    print("      - Cloud Console Admin")

    print("\n2. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/apis/dashboard?project=tactical-snow-433017-h5")

    print("\n3. Enable the Google Drive API:")
    print("   - Click '+ ENABLE APIS AND SERVICES'")
    print("   - Search for 'Google Drive API'")
    print("   - Click 'Enable'")

    print("\n4. Configure OAuth consent screen:")
    print("   - Go to 'OAuth consent screen' in the left sidebar")
    print("   - Choose 'External' user type")
    print("   - Set the app name to 'Get Mentors TTS'")
    print("   - Add your email (jesse@getmentors.ai) as a test user")
    print("   - Fill in required fields (can use getmentors.ai for homepage)")
    print("   - Under 'Scopes for Google APIs', add these scopes:")
    print("     * .../auth/drive.file (Google Drive API - Limited file access)")
    print("     This scope allows the app to view and manage files that it creates,")
    print("     but not access all files in your Drive.")

    print("\n5. Create OAuth 2.0 credentials:")
    print("   - Go to 'Credentials' in the left sidebar")
    print("   - Click '+ CREATE CREDENTIALS' and select 'OAuth client ID'")
    print("   - Choose 'Desktop app' as the application type")
    print("   - Name it 'Get Mentors TTS'")
    print("   - Click 'Create'")

    print("\n6. Download the credentials:")
    print("   - Click the download icon (JSON) for your OAuth 2.0 client")
    print("   - Save it as 'credentials.json' in this directory")
    print("   - Replace the existing credentials.json file if it exists")

    # Ask if user wants to open the IAM console first
    response = input("\nWould you like to open the IAM settings page now? (y/n): ")
    if response.lower() == 'y':
        webbrowser.open('https://console.cloud.google.com/iam-admin/iam?project=tactical-snow-433017-h5')

def main():
    print("Setting up Get Mentors Text-to-Speech Google Drive integration...")

    # Create credentials template
    if not os.path.exists('credentials.json'):
        create_credentials_template()

    # Show setup instructions
    setup_instructions()

    print("\nAfter completing the setup, you can run:")
    print("python text_to_speech.py [file_path] --voice-name \"Alicia Speaks-Unique and Pleasant\" --person-name \"[Person Name]\"")

if __name__ == "__main__":
    main()
