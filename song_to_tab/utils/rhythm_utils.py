"""Rhythm helpers: BPM detection and quantization helpers."""
import librosa
from typing import Optional


def detect_bpm(audio_path: str) -> Optional[int]:
    try:
        y, sr = librosa.load(audio_path, sr=44100, mono=True)
        # Use a wide tempo range to avoid defaulting to 120 for slow songs
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=90, tightness=80)
        bpm = int(round(float(tempo)))
        # If result looks like a doubling/halving artifact, correct it
        if bpm > 160:
            bpm = bpm // 2
        elif bpm < 50:
            bpm = bpm * 2
        return bpm
    except Exception:
        return None
