from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.exceptions import RefreshError
import os
import pickle
from pathlib import Path
import webbrowser
import socket

class GoogleDriveManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.creds = None
        self.service = None
        self.root_folder_name = 'mentors_audio'
        self.root_folder_id = None
        self.current_mentor_folder_id = None

    def authenticate(self):
        """Authenticate with Google Drive"""
        try:
            # Try to load existing credentials
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)

            # If credentials don't exist or are invalid, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        self.creds.refresh(Request())
                    except RefreshError:
                        # If refresh fails, remove the token and start fresh
                        os.remove('token.pickle')
                        self.creds = None

                if not self.creds:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json',
                        self.SCOPES
                    )

                    print(f"\nIMPORTANT: Please make sure to:")
                    print("1. Sign in with jesse@getmentors.ai")
                    print("2. If a different account is shown, click 'Use another account'")
                    print("3. Accept the requested permissions\n")

                    self.creds = flow.run_local_server(
                        port=8080,
                        host='localhost',
                        prompt='consent',
                        success_message='Authentication successful! You may close this window.',
                        open_browser=True
                    )

                    # Save the credentials for future use
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(self.creds, token)

            # Build the service
            self.service = build('drive', 'v3', credentials=self.creds)
            return True

        except Exception as e:
            print(f"\nAuthentication Error: {str(e)}")
            print("\nPlease ensure:")
            print("1. You are using the correct Google account (jesse@getmentors.ai)")
            print("2. The OAuth consent screen is properly configured")
            print("3. You have proper internet connectivity")
            if os.path.exists('token.pickle'):
                print("\nRemoving existing token to force new authentication...")
                os.remove('token.pickle')
            return False

    def create_or_get_folder(self, folder_name, parent_id=None):
        """Create a folder in Google Drive or get its ID if it exists"""
        if not self.service:
            self.authenticate()

        # Build the query to find folders with the given name
        query = [
            f"name='{folder_name}'",
            "mimeType='application/vnd.google-apps.folder'",
            "trashed=false"
        ]

        # If parent_id is specified, only look for folders with that parent
        if parent_id:
            query.append(f"'{parent_id}' in parents")

        # Combine all query conditions
        query_string = " and ".join(query)

        results = self.service.files().list(
            q=query_string,
            spaces='drive',
            fields='files(id, name, parents)'
        ).execute()

        folders = results.get('files', [])

        # If parent_id is specified, ensure we only get folders that are direct children
        if parent_id and folders:
            folders = [f for f in folders if parent_id in f.get('parents', [])]

        if folders:
            return folders[0]['id']
        else:
            # Create new folder with specified parent
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            return folder['id']

    def ensure_mentor_folder(self, mentor_name):
        """Ensure the root and mentor-specific folders exist"""
        if not self.service:
            self.authenticate()

        # Always try to create/get root folder first
        self.root_folder_id = self.create_or_get_folder(self.root_folder_name)
        print(f"\nRoot folder '{self.root_folder_name}' ID: {self.root_folder_id}")

        # Create or get mentor folder inside root folder
        self.current_mentor_folder_id = self.create_or_get_folder(mentor_name, self.root_folder_id)
        print(f"Mentor folder '{mentor_name}' ID: {self.current_mentor_folder_id}")

        return self.current_mentor_folder_id

    def upload_file(self, file_path, mentor_name):
        """Upload a file to the mentor's folder in Google Drive"""
        if not self.service:
            self.authenticate()

        # Ensure folders exist
        if not self.current_mentor_folder_id or self.current_mentor_folder_id != mentor_name:
            self.ensure_mentor_folder(mentor_name)

        # Upload the file
        file_metadata = {
            'name': Path(file_path).name,
            'parents': [self.current_mentor_folder_id]
        }

        media = MediaFileUpload(
            file_path,
            mimetype='audio/mpeg',
            resumable=True
        )

        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file['id']

    def upload_folder(self, local_folder_path, mentor_name):
        """Upload all files from a local folder to Google Drive"""
        if not self.service:
            self.authenticate()

        # Ensure mentor folder exists
        self.ensure_mentor_folder(mentor_name)

        folder_path = Path(local_folder_path)
        if not folder_path.exists():
            raise ValueError(f"Folder not found: {local_folder_path}")

        print(f"\nUploading files from {local_folder_path} to Google Drive mentor folder: {mentor_name}")
        uploaded_files = []
        for file_path in folder_path.glob('*.mp3'):
            print(f"Uploading: {file_path.name}")
            file_id = self.upload_file(str(file_path), mentor_name)
            uploaded_files.append({
                'file_name': file_path.name,
                'file_id': file_id
            })
            print(f"Successfully uploaded: {file_path.name}")

        return uploaded_files
