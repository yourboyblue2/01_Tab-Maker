# TabMaker — Build Log

## What We Built
A web app that takes a YouTube URL and returns guitar tabs + a downloadable MIDI file.

**Pipeline:** YouTube URL → audio download (yt-dlp) → guitar stem isolation (Demucs) → polyphonic transcription (basic-pitch) → AI tab rendering (Claude Haiku) → React frontend

**Stack:** Python 3.11 / FastAPI backend · React/Vite frontend · Anthropic API

---

## Architecture

```
frontend/ (React/Vite, :5173)
    POST /generate { url }
backend/main.py (FastAPI, :8000)
    → ingest.py       — yt-dlp download, ffmpeg WAV conversion
    → separate.py     — Demucs htdemucs guitar stem isolation
    → transcribe.py   — basic-pitch polyphonic MIDI extraction
    → render.py       — Claude Haiku tab generation
    → returns { title, tab_text, bpm, midi_b64 }
```

---

## Key Decisions

**Claude for tab rendering (not an algorithm)**
The original codebase had a hand-rolled ASCII renderer that didn't understand music theory — couldn't do chord voicings or fret position optimization. Replaced with a Claude Haiku prompt. Interview talking point: "the algorithmic approach failed, so I used Claude to handle the guitar music theory."

**basic-pitch over librosa**
basic-pitch (Spotify) gives polyphonic transcription — it detects multiple simultaneous notes (chords). librosa's pYIN fallback is monophonic (one note at a time). The difference is dramatic: 9 events vs 1647 for the same song.

**30-second window for Claude prompt**
Sending all ~1600 notes produces garbage (notes too sparse after trimming). Sending the first 120 notes consecutively gives Claude a dense, readable section. We show the intro/first verse rather than a sparse sample of the whole song.

**imageio-ffmpeg for ffmpeg binary**
System ffmpeg wasn't on PATH. Bundled it via `imageio-ffmpeg`. yt-dlp's postprocessor was bypassed entirely (it needs ffprobe which we didn't have) — instead we download raw audio then convert with ffmpeg directly via subprocess.

**Python 3.11 (not 3.14)**
Python 3.14 broke torchaudio (demucs dependency) and basic-pitch. torchaudio 2.11 defaulted to TorchCodec which isn't available on Windows. Downgraded torchaudio to 2.3.0 (compatible with Python 3.11, uses soundfile backend).

---

## What Broke and Why

| Issue | Cause | Fix |
|---|---|---|
| ffmpeg not found | imageio-ffmpeg binary named `ffmpeg-win-x86_64-v7.1.exe`, not `ffmpeg.exe` | Bypass yt-dlp postprocessor; call ffmpeg binary directly |
| Demucs TorchCodec error | torchaudio 2.11 defaults to TorchCodec on Windows | Downgrade to `torch==2.3.0 torchaudio==2.3.0` |
| basic-pitch wouldn't install | Python 3.14 removed `pkgutil.ImpImporter` used by old build tools | Switch to Python 3.11 venv |
| Tab had 1 note per measure | Evenly sampled 200 notes from full song → large time gaps | Take dense first-30-seconds window instead |
| BPM always 120 | librosa defaulting for slow blues songs | Pass `start_bpm=90, tightness=80`; halve if >160 |

---

## Startup

```powershell
# Terminal 1 — Backend
cd "c:\Zayd\01_Programs\01_Tab Maker"
.\venv311\Scripts\Activate.ps1
$env:ANTHROPIC_API_KEY = "sk-ant-..."
uvicorn backend.main:app --reload

# Terminal 2 — Frontend
cd "c:\Zayd\01_Programs\01_Tab Maker\frontend"
npm run dev
```

Open http://localhost:5173

---

## Interview Talking Points

- **Why now:** Demucs (Meta, 2023) + basic-pitch (Spotify, 2022) made stem separation and polyphonic transcription production-quality. This pipeline wasn't buildable 3 years ago.
- **What the AI got wrong:** Algorithmic tab rendering couldn't handle chord voicings — had to bring Claude in for music theory reasoning.
- **Honest gaps:** Tab quality degrades without clean stem separation. BPM detection is unreliable for blues/jazz with irregular timing.
- **Assign personas:** Guitar teacher, indie musician learning covers, music school owner.
