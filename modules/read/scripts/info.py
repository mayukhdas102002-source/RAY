#!/usr/bin/env python3
"""Fetch metadata (and optionally top comments) for an ONLINE video, without
downloading it.

Title, uploader, duration, views/likes, upload date, description, hashtags and
- when asked - the top comments. Cheap: one yt-dlp metadata call, no media
transfer. Use this before deciding whether to fetch/transcribe anything.

Usage:
    python info.py URL [--comments N] [--json]
"""
from __future__ import annotations

import argparse
import json
import re

from common import (COOKIE_HELP, cookie_args, die, is_url, needs_cookies,
                    platform_of, require, run)


def human(n) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "?"
    for unit in ("", "K", "M", "B"):
        if abs(n) < 1000:
            return f"{n}{unit}" if unit == "" else f"{n:.1f}{unit}"
        n /= 1000.0
    return f"{n:.1f}T"


def hms(seconds) -> str:
    try:
        seconds = int(float(seconds))
    except (TypeError, ValueError):
        return "?"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def main() -> None:
    ap = argparse.ArgumentParser(description="Metadata for an online video URL.")
    ap.add_argument("url")
    ap.add_argument("--comments", type=int, default=0,
                    help="include up to N top comments (slower; 0 = skip)")
    ap.add_argument("--json", action="store_true", help="emit raw yt-dlp JSON")
    args = ap.parse_args()

    if not is_url(args.url):
        die("info.py takes a URL. For a local file use probe.py.")
    if needs_cookies(args.url):
        die(f"{platform_of(args.url)} is login-walled and no cookies are configured.\n"
            + COOKIE_HELP)

    ytdlp = require("yt-dlp")
    cmd = [ytdlp, "-J", "--no-playlist", "--no-warnings", *cookie_args(args.url)]
    if args.comments > 0:
        cmd += ["--write-comments", "--extractor-args",
                f"youtube:comment_sort=top;max_comments={args.comments},all,{args.comments}"]
    cmd.append(args.url)

    proc = run(cmd)
    try:
        info = json.loads(proc.stdout)
    except json.JSONDecodeError:
        die("yt-dlp returned no usable metadata for this URL.")

    if args.json:
        print(json.dumps(info, indent=2)[:200000])
        return

    desc = (info.get("description") or "").strip()
    tags = sorted(set(re.findall(r"#\w+", desc)))
    date = info.get("upload_date") or ""
    if len(date) == 8:
        date = f"{date[:4]}-{date[4:6]}-{date[6:]}"

    print(f"Title    : {info.get('title', '?')}")
    print(f"Platform : {platform_of(args.url)}")
    print(f"Uploader : {info.get('uploader') or info.get('channel') or '?'}")
    print(f"Duration : {hms(info.get('duration'))}")
    print(f"Uploaded : {date or '?'}")
    print(f"Views    : {human(info.get('view_count'))}    "
          f"Likes: {human(info.get('like_count'))}    "
          f"Comments: {human(info.get('comment_count'))}")
    subs = sorted(set(info.get("subtitles") or {}))
    autos = sorted(set(info.get("automatic_captions") or {}))
    print(f"Captions : manual={', '.join(subs[:8]) or 'none'}  "
          f"auto={', '.join(autos[:8]) or 'none'}")
    if tags:
        print(f"Hashtags : {' '.join(tags[:20])}")
    if desc:
        print("\nDescription:")
        print(desc[:2000] + ("\n[...truncated]" if len(desc) > 2000 else ""))

    if args.comments > 0:
        comments = info.get("comments") or []
        print(f"\nTop comments ({min(len(comments), args.comments)}):")
        if not comments:
            print("  (none returned - the platform may not expose them)")
        for c in comments[:args.comments]:
            text = " ".join((c.get("text") or "").split())[:300]
            print(f"  - {c.get('author', '?')} ({human(c.get('like_count'))} likes): {text}")


if __name__ == "__main__":
    main()
