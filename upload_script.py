import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Define Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """
    Authenticate with Google Drive API using service account credentials.
    """
    try:
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file('service-account.json', scopes=SCOPES)
        return credentials
    except FileNotFoundError:
        print("Error: service-account.json file not found.")
        return None

def check_existing_files(service, folder_id):
    """
    Check existing files in the specified folder.
    """
    try:
        results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
        files = results.get('files', [])
        return {file['name']: file['id'] for file in files}
    except Exception as e:
        print(f'Error checking existing files: {e}')
        return {}

def upload_files(folder_path, folder_id):
    """
    Upload files from a folder to a folder in Google Drive.
    """
    try:
        # Authenticate
        creds = authenticate()
        if not creds:
            return

        # Build Google Drive service
        service = build('drive', 'v3', credentials=creds)

        # Get existing files in the destination folder
        existing_files = check_existing_files(service, folder_id)

        # Iterate over files in the folder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            # Check if the file already exists
            if file_name in existing_files:
                print(f'File "{file_name}" already exists in the destination folder.')
                continue

            # Create MediaFileUpload object
            media = MediaFileUpload(file_path, resumable=True)

            # Upload the file to the specified folder
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f'File "{file_name}" uploaded successfully to folder with ID: {folder_id}')
    except Exception as e:
        print(f'Error uploading files: {e}')

def main():
    # Specify the path of the folder to be uploaded and the ID of the destination folder
    folder_path = 'uploads'  # Update with the correct folder path
    folder_id = '1RniXadmT7FpyC1pSXlOa5ddy2vgW9pRH'  # Update with the correct folder ID

    upload_files(folder_path, folder_id)

if __name__ == '__main__':
    main()

