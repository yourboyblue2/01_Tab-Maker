"""Module 3: Transcription using basic-pitch if available, otherwise a librosa fallback.
Produces a list of note events: dicts with keys: pitch (midi), onset_time, duration, confidence
"""
from typing import List, Dict
import numpy as np
from pathlib import Path


def transcribe(audio_path: str, min_confidence: float=0.5, verbose: bool=False, midi_output_path: str=None) -> List[Dict]:
    # Try basic_pitch first
    try:
        from basic_pitch.inference import predict
        from basic_pitch import ICASSP_2022_MODEL_PATH
        if verbose:
            print('Using basic-pitch for transcription')
        # Returns (model_output, midi_data, note_events)
        # note_events: list of (start_s, end_s, pitch_midi, amplitude, pitch_bends)
        _, midi_data, note_events = predict(audio_path, ICASSP_2022_MODEL_PATH)
        if midi_output_path:
            midi_data.write(midi_output_path)
        events = []
        for (start_s, end_s, pitch_midi, amplitude, _) in note_events:
            events.append({
                'pitch': int(pitch_midi),
                'onset_time': float(start_s),
                'duration': float(end_s - start_s),
                'confidence': float(amplitude),
            })
        return [e for e in events if e['confidence'] >= min_confidence]
    except Exception:
        if verbose:
            print('basic-pitch not available or failed; using librosa fallback (monophonic).')

    # Librosa fallback (monophonic pYIN-based estimation)
    try:
        import librosa
    except Exception as e:
        raise RuntimeError('basic-pitch not installed and librosa import failed: ' + str(e))

    y, sr = librosa.load(audio_path, sr=44100, mono=True)
    # onset detection
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=False)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    # f0 estimation using pyin
    f0, voiced_flag, voiced_prob = librosa.pyin(y, fmin=librosa.note_to_hz('E2'), fmax=librosa.note_to_hz('E6'), sr=sr)
    times = librosa.times_like(f0, sr=sr)

    events = []
    # For each onset, find the nearest voiced f0 and measure duration until next onset (or 0.5s)
    for i, ot in enumerate(onset_times):
        # find index in times nearest to ot
        idx = np.argmin(np.abs(times - ot))
        # find contiguous voiced region starting at idx
        if not voiced_flag[idx]:
            # search forward up to 0.5s for voiced
            search_idx = idx
            found_idx = None
            while search_idx < len(voiced_flag) and times[search_idx] < ot + 0.5:
                if voiced_flag[search_idx]:
                    found_idx = search_idx
                    break
                search_idx += 1
            if found_idx is None:
                continue
            idx = found_idx

        midi = int(np.round(librosa.hz_to_midi(f0[idx])))
        # duration: until next onset or until voiced stops
        if i+1 < len(onset_times):
            duration = onset_times[i+1] - ot
        else:
            # estimate until voiced ends
            j = idx
            while j < len(voiced_flag) and voiced_flag[j]:
                j += 1
            duration = max(0.05, times[j-1] - times[idx]) if j-1 > idx else 0.1

        confidence = float(voiced_prob[idx]) if voiced_prob is not None else 1.0
        event = {'pitch': midi, 'onset_time': float(ot), 'duration': float(duration), 'confidence': confidence}
        if 40 <= midi <= 88 and confidence >= min_confidence:
            events.append(event)

    return events
