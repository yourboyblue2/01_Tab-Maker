#!/usr/bin/env python3
"""CLI entrypoint for song-to-tab pipeline."""
import argparse
import os
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE_DIR))

from modules import ingest, separate, transcribe, render
from utils.rhythm_utils import detect_bpm


def main():
    parser = argparse.ArgumentParser(description="Song-to-Guitar-Tab Transcription Tool")
    parser.add_argument('url', help='YouTube URL to process')
    parser.add_argument('--output', help='Output file path', default=None)
    parser.add_argument('--ffmpeg-location', help='Path to ffmpeg/ffprobe binary (if not on PATH)', default=None)
    parser.add_argument('--no-separate', help='Skip guitar isolation', action='store_true')
    parser.add_argument('--confidence', type=float, default=0.5, help='Minimum note confidence threshold')
    parser.add_argument('--bpm', type=int, default=None, help='Override tempo detection')
    parser.add_argument('--time-sig', type=str, default='4/4', help='Override time signature')
    parser.add_argument('--grid', type=int, default=16, help='Rhythmic quantization grid (default 16)')
    parser.add_argument('--stem', type=str, choices=['guitar','other'], default='guitar', help='Demucs stem to use')
    parser.add_argument('--keep-audio', action='store_true', help='Retain intermediate WAV files')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    workdir = Path.cwd()
    raw_audio = workdir / 'audio_raw.wav'
    guitar_audio = workdir / 'audio_guitar.wav'

    try:
        if args.verbose:
            print(f"[1/4] Downloading audio from {args.url} -> {raw_audio}")
        title = ingest.download_audio(args.url, str(raw_audio), verbose=args.verbose, ffmpeg_location=args.ffmpeg_location)

        if args.no_separate:
            if args.verbose:
                print("[2/4] Skipping separation (--no-separate set)")
            guitar_src = str(raw_audio)
        else:
            if args.verbose:
                print(f"[2/4] Running source separation (stem={args.stem})")
            guitar_src = separate.separate_audio(str(raw_audio), str(guitar_audio), stem=args.stem, verbose=args.verbose)

        if args.bpm:
            bpm = args.bpm
        else:
            if args.verbose:
                print('[3/4] Detecting BPM')
            bpm = detect_bpm(guitar_src) or 120

        if args.verbose:
            print('[3/4] Transcribing audio -> note events')
        note_events = transcribe.transcribe(guitar_src, min_confidence=args.confidence, verbose=args.verbose)

        out_path = args.output or f"{title}_tab.txt"
        if args.verbose:
            print(f"[4/4] Rendering tab -> {out_path}")
        render.render_tab(note_events, bpm=bpm, grid=args.grid, time_sig=args.time_sig, output_path=out_path, title=title, url=args.url)

        if not args.keep_audio:
            try:
                raw_audio.unlink()
            except Exception:
                pass
            try:
                Path(guitar_src).unlink()
            except Exception:
                pass

        print(f"Done. Tab written to {out_path}")

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
