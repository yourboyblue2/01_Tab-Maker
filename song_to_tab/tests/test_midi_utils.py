from utils.midi_utils import map_midi_to_string_fret


def test_map_open_strings():
    # low E (40) should map to string 0 fret 0
    assert map_midi_to_string_fret(40) == (0,0)
    # high e (64) maps to string 5 fret 0
    assert map_midi_to_string_fret(64) == (5,0)
    # A (45) -> string 1 fret 0
    assert map_midi_to_string_fret(45) == (1,0)
