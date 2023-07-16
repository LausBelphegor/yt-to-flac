import os
import subprocess
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import yt_dlp
import pickle
import sqlite3
import time

# Function to check if a program is installed


def is_installed(program):
    try:
        if program == 'choco':
            subprocess.check_output([program, '-v'])
        else:
            subprocess.check_output([program, '-version'])
        return True
    except Exception:
        return False

# Function to install Chocolatey


def install_choco():
    script = """
    Set-ExecutionPolicy Bypass -Scope Process -Force;
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    """
    subprocess.run(["powershell", "-Command", script], shell=True)

# Function to install a program


def install(program):
    subprocess.run(['choco', 'install', program, '-y'], shell=True)

# Function to update a program


def update(program):
    subprocess.run(['choco', 'upgrade', program, '-y'], shell=True)


def convert_to_flac():
    # Check if Chocolatey is installed
    if not is_installed('choco'):
        print('Chocolatey is not installed. Installing...')
        install_choco()

    # Check if FFmpeg is installed
    if not is_installed('ffmpeg'):
        print('FFmpeg is not installed. Installing...')
        install('ffmpeg')

    # Create a SQLite database to keep track of processed directories
    conn = sqlite3.connect('processed_dirs.db')
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS directories (name TEXT PRIMARY KEY, last_modified INTEGER)''')

    # Convert m4a and mp4 files to FLAC
    for root, dirs, files in os.walk('.'):
        # Get the last modification time of the directory
        last_modified = int(os.path.getmtime(root))

        # If the directory has already been processed, check the last modification time
        c.execute('SELECT * FROM directories WHERE name=?', (root,))
        row = c.fetchone()
        if row is not None and row[1] >= last_modified:
            continue

        for file in files:
            if file.endswith('.m4a') or file.endswith('.mp4'):
                print(f'Converting {file} to FLAC...')
                subprocess.run(['ffmpeg', '-i', os.path.join(root, file),
                               os.path.splitext(os.path.join(root, file))[0] + '.flac'])

        # Update the directory in the database with the current time
        c.execute('REPLACE INTO directories VALUES (?, ?)',
                  (root, int(time.time())))
        conn.commit()

    conn.close()


def create_playlist(youtube, title):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": title,
                "tags": [
                    "API call"
                ],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )
    response = request.execute()
    return response["id"]


def get_or_create_playlist(youtube, title):
    request = youtube.playlists().list(
        part="snippet",
        mine=True
    )
    response = request.execute()
    for item in response["items"]:
        if item["snippet"]["title"] == title:
            return item["id"]
    return create_playlist(youtube, title)


def move_video(youtube, video_id, from_playlist_id, to_playlist_id):
    # Add to new playlist
    add_request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": to_playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    add_request.execute()

    # Remove from old playlist
    remove_request = youtube.playlistItems().list(
        part="id,snippet",
        maxResults=25,
        playlistId=from_playlist_id
    )
    remove_response = remove_request.execute()
    for item in remove_response["items"]:
        if "snippet" in item and "resourceId" in item["snippet"] and item["snippet"]["resourceId"]["videoId"] == video_id:
            delete_request = youtube.playlistItems().delete(id=item["id"])
            delete_request.execute()


def sanitize_title(title):
    return "".join(c for c in title if c not in r'\/:*?"<>|')


def download_videos(youtube, pending_playlist_id, downloaded_playlist_id):
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=25,
        playlistId=pending_playlist_id
    )
    response = request.execute()
    for item in response["items"]:
        video_id = item["snippet"]["resourceId"]["videoId"]
        video_title = sanitize_title(item["snippet"]["title"])
        download_folder = os.path.join(os.getcwd(), video_title)
        os.makedirs(download_folder, exist_ok=True)
        ydl_opts = {
            'outtmpl': os.path.join(download_folder, video_title + '.%(ext)s'),
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
        move_video(youtube, video_id, pending_playlist_id,
                   downloaded_playlist_id)


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "C:\\temp\\projects\\yt-to-flac\\client_secret.json"
    credentials_file = "credentials.pickle"

    # Get credentials and create an API client
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)

    # Try to load credentials from file
    try:
        with open(credentials_file, 'rb') as f:
            credentials = pickle.load(f)
    except FileNotFoundError:
        credentials = flow.run_local_server(port=0)
        # Save credentials for next run
        with open(credentials_file, 'wb') as f:
            pickle.dump(credentials, f)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    pending_playlist_id = get_or_create_playlist(
        youtube, "pending-to-download")
    downloaded_playlist_id = get_or_create_playlist(youtube, "downloaded")

    download_videos(youtube, pending_playlist_id, downloaded_playlist_id)
    convert_to_flac()


if __name__ == "__main__":
    main()
