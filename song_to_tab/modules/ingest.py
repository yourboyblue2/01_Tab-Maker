"""Module 1: Audio ingestion using yt-dlp."""
from yt_dlp import YoutubeDL
from pathlib import Path
import subprocess
import os


def _get_ffmpeg_exe() -> str | None:
    """Return the full path to the ffmpeg binary (imageio-ffmpeg bundled or system)."""
    # Check system PATH first
    import shutil as sh
    sys_ffmpeg = sh.which('ffmpeg')
    if sys_ffmpeg:
        return sys_ffmpeg
    # Fall back to imageio-ffmpeg bundled binary
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def download_audio(youtube_url: str, output_wav_path: str, verbose: bool = False, ffmpeg_location: str = None) -> str:
    """Download audio from YouTube and convert to WAV 44.1kHz.
    Downloads in native format first, then converts with ffmpeg directly
    to avoid needing ffprobe.
    """
    out_path = Path(output_wav_path)
    out_dir = out_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Download raw audio (no postprocessor — avoids ffprobe dependency)
    # Force direct HTTP streams only to avoid DASH/HLS info:// scheme errors
    ydl_opts = {
        'format': 'bestaudio[protocol=https]/bestaudio[protocol=http]/bestaudio',
        'outtmpl': str(out_dir / 'raw_download.%(ext)s'),
        'noplaylist': True,
        'quiet': not verbose,
        'no_warnings': not verbose,
        'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)

    title = info.get('title', 'song')

    # Find the downloaded file
    raw_file = None
    for ext in ('m4a', 'webm', 'opus', 'mp4', 'mp3', 'ogg', 'wav'):
        candidate = out_dir / f'raw_download.{ext}'
        if candidate.exists():
            raw_file = candidate
            break

    if raw_file is None:
        raise FileNotFoundError('Downloaded audio file not found after yt-dlp')

    # Step 2: Convert to WAV using ffmpeg directly (no ffprobe needed)
    ffmpeg_exe = ffmpeg_location or _get_ffmpeg_exe()
    if not ffmpeg_exe:
        raise RuntimeError('ffmpeg not found. Install via: winget install Gyan.FFmpeg')

    result = subprocess.run(
        [ffmpeg_exe, '-y', '-i', str(raw_file), '-ar', '44100', '-ac', '2', str(out_path)],
        capture_output=True, text=True
    )
    raw_file.unlink(missing_ok=True)

    if not out_path.exists():
        raise RuntimeError(f'ffmpeg conversion failed: {result.stderr[-500:]}')

    safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return safe_title.replace(' ', '_') or 'song'
