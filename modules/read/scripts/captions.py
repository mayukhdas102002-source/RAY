#!/usr/bin/env python3
"""Grab the platform's OWN captions for an online video - fast and free.

Always try this before transcribe.py for a URL: YouTube and most platforms
already have manual or auto-generated subtitles, so there is no reason to
download the media and run speech-to-text. Exits non-zero if no captions
exist, which is your cue to fall back to fetch.py --audio-only + transcribe.py.

Usage:
    python captions.py URL [--lang en] [--no-auto] [--out DIR] [--plain]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import (COOKIE_HELP, cookie_args, die, is_url, needs_cookies,
                    out_dir, platform_of, require, run, vtt_to_text)


def main() -> None:
    ap = argparse.ArgumentParser(description="Download platform captions for a URL.")
    ap.add_argument("url")
    ap.add_argument("--lang", default="en",
                    help="preferred language code(s), comma-separated (default en). "
                         "Use 'any' to accept whatever exists.")
    ap.add_argument("--no-auto", action="store_true",
                    help="only accept human-made subtitles, not auto-generated")
    ap.add_argument("--plain", action="store_true", help="strip timestamps")
    ap.add_argument("--out", default="", help="output directory (default: temp)")
    args = ap.parse_args()

    if not is_url(args.url):
        die("captions.py takes a URL. For a local file use transcribe.py.")
    if needs_cookies(args.url):
        die(f"{platform_of(args.url)} is login-walled and no cookies are configured.\n"
            + COOKIE_HELP)

    ytdlp = require("yt-dlp")
    dest = Path(args.out) if args.out else out_dir(args.url.rsplit("/", 1)[-1] or "captions")
    dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("*.vtt"):
        old.unlink()

    langs = "*" if args.lang.strip().lower() == "any" else args.lang
    cmd = [ytdlp, "--skip-download", "--write-subs", "--no-warnings", "--no-playlist",
           "--sub-langs", langs, "--sub-format", "vtt/best", "--convert-subs", "vtt",
           *cookie_args(args.url), "-o", str(dest / "subs.%(ext)s"), args.url]
    if not args.no_auto:
        cmd.insert(3, "--write-auto-subs")
    run(cmd, check=False)

    files = sorted(dest.glob("*.vtt"), key=lambda p: p.stat().st_size, reverse=True)
    if not files:
        die("no captions available for this video. Fall back to:\n"
            "    python fetch.py \"<URL>\" --audio-only\n"
            "    python transcribe.py \"<FILE>\"", code=2)

    text = vtt_to_text(files[0], with_timestamps=not args.plain)
    if not text.strip():
        die("captions file was empty; fall back to fetch.py --audio-only + transcribe.py",
            code=2)

    saved = dest / "captions.txt"
    saved.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\nSource: {files[0].name}   Saved: {saved}")


if __name__ == "__main__":
    main()
