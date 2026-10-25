#!/usr/bin/env python3
"""Transcribe speech from a video/audio file (or URL) to timestamped text.

For a URL, try captions.py FIRST - platform captions are instant and free.
This script is the fallback when a video has no captions, or the input is a
local file.

Prefers `faster-whisper` (fast, no torch); falls back to `openai-whisper`.
Audio is extracted to 16 kHz mono WAV via ffmpeg first, so any container works.
If given a URL it downloads audio only via yt-dlp, then transcribes that.

Output: a timestamped transcript to stdout, e.g.
    [00:00 -> 00:04] Welcome back to the channel.
Also writes transcript.txt and transcript.srt to the output dir.

Usage:
    python transcribe.py INPUT [--model MODEL] [--language LANG]
                               [--start S] [--end S] [--out DIR]

MODEL: tiny | base | small | medium | large-v3  (default: base)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import (COOKIE_HELP, cookie_args, die, is_url, needs_cookies,
                    out_dir, platform_of, require, run)


def fetch_audio(url: str, dest: Path) -> str:
    """Download audio only for a URL; return the local path."""
    if needs_cookies(url):
        die(f"{platform_of(url)} is login-walled and no cookies are configured.\n"
            + COOKIE_HELP)
    ytdlp = require("yt-dlp")
    before = set(dest.iterdir())
    run([ytdlp, "-f", "bestaudio/best", "--no-playlist", "--restrict-filenames",
         *cookie_args(url), "-o", str(dest / "source.%(ext)s"), url])
    new = sorted((p for p in set(dest.iterdir()) - before if p.is_file()),
                 key=lambda p: p.stat().st_mtime, reverse=True)
    if not new:
        die("audio download produced no file.")
    return str(new[0])


def extract_audio(input_path: str, dest: Path, start: float, end: float) -> Path:
    ffmpeg = require("ffmpeg")
    wav = dest / "audio.wav"
    trim: list[str] = []
    if start:
        trim += ["-ss", str(start)]
    if end and end > start:
        trim += ["-t", str(end - start)]
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *trim,
         "-i", input_path, "-vn", "-ac", "1", "-ar", "16000",
         "-f", "wav", str(wav)])
    return wav


def ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def srt_ts(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def transcribe(wav: Path, model: str, language: str | None):
    """Yield (start, end, text) segments using whichever backend is installed."""
    try:
        from faster_whisper import WhisperModel  # type: ignore
        m = WhisperModel(model, device="cpu", compute_type="int8")
        segments, _ = m.transcribe(str(wav), language=language, vad_filter=True)
        for seg in segments:
            yield seg.start, seg.end, seg.text.strip()
        return
    except ImportError:
        pass

    try:
        import whisper  # type: ignore
    except ImportError:
        die("no transcription backend found. Install one with:\n"
            "    pip install faster-whisper      (recommended, no torch)\n"
            "    pip install openai-whisper      (alternative)")

    m = whisper.load_model(model)
    result = m.transcribe(str(wav), language=language)
    for seg in result.get("segments", []):
        yield seg["start"], seg["end"], seg["text"].strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe speech from a video/audio file or URL.")
    ap.add_argument("input")
    ap.add_argument("--model", default="base",
                    help="tiny|base|small|medium|large-v3 (default base)")
    ap.add_argument("--language", default=None, help="force a language code, e.g. en")
    ap.add_argument("--start", type=float, default=0.0, help="start offset in seconds")
    ap.add_argument("--end", type=float, default=0.0, help="end offset in seconds (0 = end)")
    ap.add_argument("--out", default="", help="output directory (default: temp)")
    args = ap.parse_args()

    dest = Path(args.out) if args.out else out_dir(args.input)
    dest.mkdir(parents=True, exist_ok=True)

    source = fetch_audio(args.input, dest) if is_url(args.input) else args.input
    wav = extract_audio(source, dest, args.start, args.end)

    segments = list(transcribe(wav, args.model, args.language))
    if not segments:
        die("no speech detected.")

    offset = args.start
    lines, srt = [], []
    for i, (start, end, text) in enumerate(segments, 1):
        if not text:
            continue
        start, end = start + offset, end + offset
        lines.append(f"[{ts(start)} -> {ts(end)}] {text}")
        srt.append(f"{i}\n{srt_ts(start)} --> {srt_ts(end)}\n{text}\n")

    transcript = "\n".join(lines)
    (dest / "transcript.txt").write_text(transcript + "\n", encoding="utf-8")
    (dest / "transcript.srt").write_text("\n".join(srt) + "\n", encoding="utf-8")

    print(transcript)
    print(f"\nSaved: {dest / 'transcript.txt'}  and  {dest / 'transcript.srt'}")


if __name__ == "__main__":
    main()
