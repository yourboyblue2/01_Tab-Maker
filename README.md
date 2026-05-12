# Song-to-Tab (v1)

A CLI tool that downloads a YouTube audio track, isolates the guitar part, transcribes notes, and renders ASCII guitar tablature.

This repository contains a v1 implementation with sensible fallbacks. For best results, install the heavy ML packages listed in `requirements.txt`.

Quick start (Windows PowerShell):

```powershell
python -m pip install -r requirements.txt
# Ensure ffmpeg is installed and on PATH
python song_to_tab.py "https://www.youtube.com/watch?v=..." --verbose
```

Notes:
- If `basic-pitch` is installed the tool will attempt to use it for polyphonic transcription. Otherwise a librosa-based monophonic fallback is used.
- `demucs` must be installed for source separation. Alternatively use `--no-separate` if your audio is already isolated.
