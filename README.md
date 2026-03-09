# YT Downloader

Simple Windows GUI for `yt-dlp` built with Tkinter.

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

```bash
pip install yt-dlp
python gui_downloader.py
