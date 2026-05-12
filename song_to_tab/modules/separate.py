"""Module 2: Guitar isolation using Demucs (htdemucs preferred).
This implementation calls the demucs CLI if available. Falls back gracefully.
"""
import os
import subprocess
from pathlib import Path


def separate_audio(input_wav: str, output_wav: str, stem: str='guitar', keep: bool=False, verbose: bool=False) -> str:
    """Run demucs to separate stems and return path to isolated guitar wav.
    If demucs not available, raise an informative error.
    """
    input_p = Path(input_wav)
    if not input_p.exists():
        raise FileNotFoundError(f"Input audio not found: {input_wav}")

    # Use demucs CLI to run htdemucs (6-stem) into a temporary directory
    outdir = input_p.parent / 'separated'
    outdir.mkdir(exist_ok=True)

    # Try 6-stem first
    cmd = ['demucs', '--two-stems', 'none', '--model', 'htdemucs', str(input_wav)]
    try:
        if verbose:
            print('Running:', ' '.join(cmd))
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise RuntimeError('demucs not found. Please install with `pip install demucs` and ensure the `demucs` CLI is on PATH.')
    except subprocess.CalledProcessError:
        # try a simpler demucs call
        try:
            cmd2 = ['demucs', str(input_wav)]
            if verbose:
                print('Retry running:', ' '.join(cmd2))
            subprocess.run(cmd2, check=True)
        except Exception as e:
            raise RuntimeError('Demucs failed: ' + str(e))

    # demucs creates a folder named 'separated' by default; search for the output file
    # The exact path can vary: typically `separated/htdemucs/<track>/<stem>.wav` or `separated/<track>/<stem>.wav`
    found = None
    for root, dirs, files in os.walk('separated'):
        for f in files:
            if f.lower().startswith(input_p.stem.lower()) and f.lower().endswith('.wav') and stem in f.lower():
                found = Path(root) / f
                break
        if found:
            break

    # fallback: look for any file named '*guitar.wav' or '*other.wav'
    if not found:
        for root, dirs, files in os.walk('separated'):
            for f in files:
                if f.lower().endswith('.wav') and stem in f.lower():
                    found = Path(root) / f
                    break
            if found:
                break

    if not found:
        # if requested stem not found, attempt 'other'
        if stem != 'other':
            for root, dirs, files in os.walk('separated'):
                for f in files:
                    if f.lower().endswith('.wav') and 'other' in f.lower():
                        found = Path(root) / f
                        break
                if found:
                    break

    if not found:
        raise RuntimeError('Could not locate separated stem (guitar/other). Check demucs output in ./separated')

    # copy/move to output_wav
    out_p = Path(output_wav)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    found.replace(out_p)
    return str(out_p)
