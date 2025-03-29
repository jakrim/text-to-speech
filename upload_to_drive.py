from google_drive_manager import GoogleDriveManager
from pathlib import Path

def upload_mentor_files(mentor_name):
    """Upload existing audio files for a mentor to Google Drive"""
    drive_manager = GoogleDriveManager()
    if drive_manager.authenticate():
        audio_folder = Path('audio_files') / mentor_name
        if audio_folder.exists():
            print(f"\nUploading files from {audio_folder} to Google Drive...")
            uploaded_files = drive_manager.upload_folder(str(audio_folder), mentor_name)
            print(f"\nSuccessfully uploaded {len(uploaded_files)} files to Google Drive")
            for file in uploaded_files:
                print(f"Uploaded: {file['file_name']}")
        else:
            print(f"Error: Folder {audio_folder} not found")
    else:
        print("Failed to authenticate with Google Drive")

if __name__ == "__main__":
    upload_mentor_files('michael_jordan')
