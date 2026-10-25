#!/usr/bin/env python3
"""Download a video/audio from a URL to a local file via yt-dlp.

Prints the absolute path of the downloaded file prefixed with 'FILE:' so the
calling agent can hand it to probe.py / frames.py / transcribe.py / audiomap.py.

Handles login-walled sites (Facebook, Instagram, Douyin) via cookies from
VIDREADER_COOKIES_FILE or VIDREADER_COOKIES_BROWSER, and never sends cookies
to YouTube/TikTok (YouTube breaks when it gets them).

Usage:
    python fetch.py URL [--max-height H] [--audio-only] [--out DIR]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from common import (COOKIE_HELP, cookie_args, die, is_url, needs_cookies,
                    out_dir, platform_of, require, run)


def main() -> None:
    ap = argparse.ArgumentParser(description="Download a video by URL with yt-dlp.")
    ap.add_argument("url")
    ap.add_argument("--max-height", type=int, default=720,
                    help="cap video height to keep downloads small (default 720)")
    ap.add_argument("--audio-only", action="store_true",
                    help="fetch audio only (best/cheapest for transcription)")
    ap.add_argument("--out", default="", help="output directory (default: temp)")
    args = ap.parse_args()

    if not is_url(args.url):
        die("argument does not look like a URL (expected http:// or https://).")
    if needs_cookies(args.url):
        die(f"{platform_of(args.url)} is login-walled and no cookies are configured.\n"
            + COOKIE_HELP)

    ytdlp = require("yt-dlp")
    dest = Path(args.out) if args.out else out_dir(args.url.rsplit("/", 1)[-1] or "download")
    dest.mkdir(parents=True, exist_ok=True)
    template = str(dest / "%(title).60s.%(ext)s")

    if args.audio_only:
        fmt = "bestaudio/best"
    else:
        fmt = (f"bestvideo[height<={args.max_height}]+bestaudio/"
               f"best[height<={args.max_height}]/best")

    before = set(dest.iterdir())
    run([ytdlp, "-f", fmt, "--no-playlist", "--restrict-filenames",
         *cookie_args(args.url), "-o", template, args.url])

    new = sorted((p for p in set(dest.iterdir()) - before if p.is_file()),
                 key=lambda p: p.stat().st_mtime, reverse=True)
    downloaded = new[0] if new else None
    if not downloaded:
        media = sorted((p for p in dest.glob("*.*") if p.suffix.lower() not in
                        (".txt", ".srt", ".vtt", ".json")),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        downloaded = media[0] if media else None
    if not downloaded:
        die("download reported success but no file was found.")

    print(f"FILE: {downloaded}")


if __name__ == "__main__":
    main()
