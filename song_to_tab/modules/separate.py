"""Module 2: Guitar isolation using Demucs (htdemucs preferred)."""
import subprocess
from pathlib import Path


def separate_audio(input_wav: str, output_wav: str, stem: str = 'guitar', keep: bool = False, verbose: bool = False) -> str:
    input_p = Path(input_wav)
    if not input_p.exists():
        raise FileNotFoundError(f"Input audio not found: {input_wav}")

    outdir = input_p.parent / 'separated'
    outdir.mkdir(exist_ok=True)

    # Run demucs with explicit --out so output is always in our temp dir
    cmd = ['demucs', '--out', str(outdir), '--two-stems', 'guitar', str(input_p)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            if verbose:
                print('demucs stderr:', result.stderr[-500:])
            # Retry with default 4-stem model
            cmd2 = ['demucs', '--out', str(outdir), str(input_p)]
            result2 = subprocess.run(cmd2, capture_output=True, text=True)
            if result2.returncode != 0:
                raise RuntimeError(f'Demucs failed:\n{result2.stderr[-500:]}')
    except FileNotFoundError:
        raise RuntimeError('demucs CLI not found on PATH.')

    # Search for guitar or other stem in the output directory
    found = None
    for wav in outdir.rglob('*.wav'):
        if stem in wav.stem.lower():
            found = wav
            break

    if not found:
        for wav in outdir.rglob('*.wav'):
            if 'other' in wav.stem.lower():
                found = wav
                break

    if not found:
        all_wavs = list(outdir.rglob('*.wav'))
        raise RuntimeError(f'Could not find stem in demucs output. Found: {[str(w) for w in all_wavs]}')

    out_p = Path(output_wav)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    found.replace(out_p)
    return str(out_p)
