"""Module 1: Audio ingestion using yt-dlp."""
from yt_dlp import YoutubeDL
from pathlib import Path
import os


def download_audio(youtube_url: str, output_wav_path: str, verbose: bool=False, ffmpeg_location: str = None) -> str:
    """Download audio from YouTube and convert to WAV 44.1kHz.
    Returns a cleaned song title (safe filename) for output naming.
    """
    out_path = Path(output_wav_path)
    out_dir = out_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(out_dir / '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': not verbose,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'postprocessor_args': ['-ar', '44100', '-ac', '2'],
    }
    if ffmpeg_location:
        # yt-dlp accepts an option to set ffmpeg location
        ydl_opts['ffmpeg_location'] = ffmpeg_location

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)

    title = info.get('title', 'song')
    # find the downloaded wav file (yt-dlp outputs .wav after ffmpeg postprocessor)
    candidate = out_dir / f"{title}.wav"
    if not candidate.exists():
        # try other extensions
        for ext in ('wav','m4a','mp3','webm'):
            p = out_dir / f"{title}.{ext}"
            if p.exists():
                candidate = p
                break

    if not candidate.exists():
        raise FileNotFoundError('Downloaded audio file not found')

    # move/rename to desired output path
    candidate.replace(out_path)
    safe_title = ''.join(c for c in title if c.isalnum() or c in (' ','-','_')).rstrip()
    safe_title = safe_title.replace(' ', '_')
    return safe_title
