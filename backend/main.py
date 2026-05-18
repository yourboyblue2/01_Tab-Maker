"""FastAPI backend for TabMaker — exposes the song-to-tab pipeline as an HTTP API."""
import os
import sys
import tempfile
import shutil
import warnings
import base64
from pathlib import Path

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the song_to_tab package to path
SONG_TO_TAB_DIR = Path(__file__).resolve().parent.parent / "song_to_tab"
sys.path.insert(0, str(SONG_TO_TAB_DIR))

from modules import ingest, separate, transcribe
from modules.render import render_tab_to_string
from utils.rhythm_utils import detect_bpm

app = FastAPI(title="TabMaker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    url: str


class GenerateResponse(BaseModel):
    title: str
    tab_text: str
    bpm: int
    midi_b64: str | None = None


@app.post("/generate", response_model=GenerateResponse)
async def generate_tab(req: GenerateRequest):
    workdir = Path(tempfile.mkdtemp(prefix="tabmaker_"))
    try:
        raw_audio = workdir / "audio_raw.wav"
        guitar_audio = workdir / "audio_guitar.wav"

        # Step 1: Download
        print(f"[1/4] Downloading: {req.url}")
        try:
            title = ingest.download_audio(req.url, str(raw_audio), verbose=False)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Download failed: {e}")
        print(f"[1/4] Done: {title}")

        # Step 2: Isolate guitar
        print("[2/4] Separating guitar stem...")
        try:
            guitar_src = separate.separate_audio(str(raw_audio), str(guitar_audio), stem="guitar", verbose=False)
            print("[2/4] Separation succeeded")
        except Exception as e:
            print(f"[2/4] Separation failed: {e}")
            print("[2/4] Using raw audio (no stem isolation)")
            guitar_src = str(raw_audio)

        # Step 3: Detect BPM + transcribe
        print("[3/4] Detecting BPM...")
        try:
            bpm = detect_bpm(guitar_src) or 120
        except Exception:
            bpm = 120
        print(f"[3/4] BPM: {bpm}. Transcribing...")

        midi_path = str(workdir / "output.mid")
        try:
            note_events = transcribe.transcribe(guitar_src, min_confidence=0.1, verbose=True, midi_output_path=midi_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
        print(f"[3/4] Got {len(note_events)} note events")

        if not note_events:
            raise HTTPException(status_code=422, detail="No notes detected in audio. Try a different URL or a song with clearer guitar.")

        # Step 4: Render tab via Claude API
        print("[4/4] Calling Claude to generate tab...")
        try:
            tab_text = render_tab_to_string(note_events, bpm=bpm, time_sig="4/4", title=title)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Tab generation failed: {e}")
        print("[4/4] Tab generated")

        midi_b64 = None
        if Path(midi_path).exists():
            midi_b64 = base64.b64encode(Path(midi_path).read_bytes()).decode()

        return GenerateResponse(title=title, tab_text=tab_text, bpm=bpm, midi_b64=midi_b64)

    finally:
        shutil.rmtree(workdir, ignore_errors=True)


@app.get("/health")
async def health():
    return {"status": "ok"}
