# YouTube to FLAC Converter

This Python script is designed to download videos from a YouTube playlist(pending-to-download) move them to the "downloaded" playlist then convert them to FLAC audio format(FLAC choice was arbitrary you could use anything ffmpeg supports). It uses the YouTube Data API v3, yt-dlp for downloading videos, and FFmpeg for audio conversion. It also uses SQLite to keep track of processed directories. 

## Dependencies

- Python 3
- FFmpeg
- yt-dlp
- SQLite
- Google Client Library
- google-auth-oauthlib
- googleapiclient
- PyInstaller

### FYI
  This script installs chocolatey(if not installed) by default if you wish to remove this feature you have to modify the script, everything that is related to chocolatey and ffmpeg is before line 87.

## Installation

1. Install Python 3 and pip (Python package installer).
2. Install the required Python packages using pip:

```bash
pip install google-auth-oauthlib googleapiclient yt-dlp pyinstaller
```

3. Install FFmpeg. The script includes a function to install FFmpeg using Chocolatey on Windows. If you're using a different operating system, you'll need to install FFmpeg manually.

## Usage

1. You need to create a `client_secret.json` file for the YouTube Data API v3. Follow the instructions [here](https://developers.google.com/youtube/registering_an_application) to create a project, enable the YouTube Data API v3, and obtain your client secrets file. Place this file in the same directory as the script.

2. Run the script:

```bash
python yt-to-flac.py
```

The script will prompt you to log in to your Google account and give the script permission to manage your YouTube playlists. It will then download all videos from the 'pending-to-download' playlist, convert them to FLAC, and move them to the 'downloaded' playlist.

## Building an Executable with PyInstaller

You can use PyInstaller to build an executable version of the script. This can be run without needing to have Python installed.

1. Install PyInstaller using pip:

```bash
pip install pyinstaller
```

2. Run PyInstaller on the script:

```bash
pyinstaller --onefile yt-to-flac.py
```

This will create a single executable file in the `dist` directory. Add this directory to your path or move the executable to somewhere added to path in order use it from terminal.

## Functions

- `is_installed(program)`: Checks if a program is installed.
- `install_choco()`: Installs Chocolatey on Windows.
- `install(program)`: Installs a program using Chocolatey.
- `update(program)`: Updates a program using Chocolatey.
- `convert_to_flac()`: Converts m4a and mp4 files to FLAC using FFmpeg.
- `create_playlist(youtube, title)`: Creates a new YouTube playlist.
- `get_or_create_playlist(youtube, title)`: Gets the ID of a playlist with a given title, or creates a new playlist if one doesn't exist.
- `move_video(youtube, video_id, from_playlist_id, to_playlist_id)`: Moves a video from one playlist to another.
- `sanitize_title(title)`: Removes invalid characters from a string to create a valid filename.
- `download_videos(youtube, pending_playlist_id, downloaded_playlist_id)`: Downloads videos from the 'pending-to-download' playlist and moves them to the 'downloaded' playlist.
- `main()`: The main function of the script. Sets up the YouTube API client, gets or creates the necessary playlists, downloads videos, and converts them to FLAC.


  

https://github.com/LausBelphegor/yt-to-flac/assets/69310891/663a52cb-00b2-4e3d-b3eb-c5462d8ec690

