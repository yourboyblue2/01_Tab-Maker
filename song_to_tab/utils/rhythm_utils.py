"""Rhythm helpers: BPM detection and quantization helpers."""
import librosa
from typing import Optional


def detect_bpm(audio_path: str) -> Optional[int]:
    try:
        y, sr = librosa.load(audio_path, sr=44100, mono=True)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        return int(round(tempo))
    except Exception:
        return None
