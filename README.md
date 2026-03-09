# YT Downloader

Simple Windows GUI for `yt-dlp` built with Tkinter.

## Download

[Download beta build](https://github.com/Butterfly908/yt-downloader/releases/download/v0.1.0-beta/YT.Downloader.v0.1.0-beta.7z)

Do not use **Code -> Download ZIP** unless you want the source code.

You may need 7-Zip or another compatible archive tool to extract the package.

## Features

- Paste a video URL
- Load available quality options
- Choose simple or advanced quality mode
- Download video or audio
- Cancel running downloads
- Save application logs for troubleshooting

## Notes

This project is a desktop GUI wrapper around `yt-dlp` for personal, archival, and other lawful uses where permitted.

Users are responsible for complying with applicable laws, platform terms, and copyright rules in their jurisdiction.

This project does not provide copyrighted media, account bypassing, DRM circumvention, or any hosted content.

## Requirements

- Windows
- Python 3.x
- `yt-dlp`
- `ffmpeg` available in system PATH for audio extraction / merging

## Run from source

    pip install yt-dlp
    python gui_downloader.py

## Build

Example PyInstaller command:

    py -m PyInstaller --clean --noconfirm --onedir --windowed --icon "app.ico" --add-data "app.ico;." --name "YT downloader" gui_downloader.py

## Feedback

If you test the app, please include:

- What URL you tested
- What quality mode you selected
- What happened
- The saved log file from the app, if available

## Disclaimer

This software is provided as-is, without warranty of any kind.

The author is not responsible for how the software is used. Use it only where you have the legal right and permission to download or archive media.
