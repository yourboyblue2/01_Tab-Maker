"""MIDI and guitar position utilities."""
from typing import Optional, Tuple, List

# Standard tuning (low E to high e)
STANDARD_TUNING_STRINGS: List[int] = [40, 45, 50, 55, 59, 64]
MAX_FRET = 24


def map_midi_to_string_fret(midi: int) -> Optional[Tuple[int,int]]:
    """Map a MIDI pitch to (string_index, fret) where string_index 0 = low E, 5 = high e.
    Choose the mapping with the lowest fret <= MAX_FRET.
    """
    candidates = []
    for idx, open_midi in enumerate(STANDARD_TUNING_STRINGS):
        fret = midi - open_midi
        if 0 <= fret <= MAX_FRET:
            candidates.append((idx, fret))
    if not candidates:
        return None
    # pick lowest fret, tiebreaker prefer higher string (larger idx) for playability
    candidates.sort(key=lambda x: (x[1], -x[0]))
    return candidates[0]
