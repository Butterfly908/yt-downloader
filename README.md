# YT Downloader

Simple Windows GUI for `yt-dlp` built with Tkinter.

## Download

Choose your preferred version:

- [English build (EN)](https://github.com/Butterfly908/yt-downloader/releases/download/v0.1.0-beta/YT.Downloader.v0.1.0-beta.EN.7z)
- [Russian build (RU)](https://github.com/Butterfly908/yt-downloader/releases/download/v0.1.0-beta/YT.Downloader.v0.1.0-beta.RU.7z)

Do not use **Code -> Download ZIP** unless you want the source code.

The packaged Windows builds include bundled `ffmpeg` / `ffprobe`, so no separate FFmpeg installation is required for normal video/audio merging.

You may need 7-Zip or another compatible archive tool to extract the package.

## Features

- Paste a video URL
- Load available quality options
- Choose simple or advanced quality mode
- Download video or audio
- Cancel running downloads
- Save application logs for troubleshooting
- Separate English and Russian desktop builds

## Notes

This project is a desktop GUI frontend for `yt-dlp` for personal, archival, and other lawful uses where permitted.

Users are responsible for complying with applicable laws, platform terms, and copyright rules in their jurisdiction.

This project does not provide any hosted content, account bypassing, or DRM circumvention features.

The packaged Windows builds include bundled `ffmpeg` / `ffprobe` for merging video and audio streams.

## Full YouTube format support (optional)

The packaged Windows builds already include bundled `ffmpeg` / `ffprobe`, so basic downloading and media merging work without installing FFmpeg separately.

However, some YouTube formats and extraction steps may require a supported external JavaScript runtime used by `yt-dlp`.

If no supported JavaScript runtime is installed, the app may still work, but some formats may be missing from the available quality list.

For the best YouTube format availability, install a supported JavaScript runtime in advance.

Recommended option on Windows: **Deno**

Official installation guide:
https://docs.deno.com/runtime/getting_started/installation/

Common Windows install options include:

```powershell
winget install deno
```

or

```powershell
irm https://deno.land/install.ps1 | iex
```

After installation, restart the app and check qualities again.

For more details about JavaScript runtime support in `yt-dlp`, see:
https://github.com/yt-dlp/yt-dlp/wiki/EJS

## Requirements

### For packaged Windows builds
- Windows
- No separate Python installation required
- No separate FFmpeg installation required for bundled builds

### For running from source
- Windows
- Python 3.x
- `yt-dlp`
- `ffmpeg` in system PATH, or local `ffmpeg` / `ffprobe` binaries available to the app
- A supported JavaScript runtime may be needed for full YouTube support in some cases

## Run from source

1. Install dependencies:

   ```bash
   pip install yt-dlp
   ```

2. Make sure `ffmpeg` / `ffprobe` are installed and available in PATH, or placed locally for the app to use.

3. For full YouTube format availability, install a supported JavaScript runtime such as Deno.

4. Run:

   ```bash
   python gui_downloader.py
   ```

## Build

Example PyInstaller command:

```bash
py -m PyInstaller --clean --noconfirm --onedir --windowed --icon "app.ico" --add-data "app.ico;." --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." --name "YT downloader" gui_downloader.py
```

## Releases

Prebuilt Windows packages, when available, are published in GitHub Releases.

## Feedback

If you test the app, please include:

- What URL you tested
- What quality mode you selected
- What happened
- The saved log file from the app, if available

## Disclaimer

This software is provided as-is, without warranty of any kind.

The author is not responsible for how the software is used. Use it only where you have the legal right and permission to download or archive media.
