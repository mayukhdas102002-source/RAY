"""Shared helpers for the claude-vidreader skill scripts.

Stdlib only. Every user-facing script imports from here so dependency checks,
cookie handling, output paths and error formatting stay consistent.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

# One-line install hints per platform, shown when a binary is missing.
INSTALL_HINTS = {
    "ffmpeg": {
        "win32": "winget install Gyan.FFmpeg",
        "darwin": "brew install ffmpeg",
        "linux": "sudo apt install ffmpeg  (or your distro's package manager)",
    },
    "ffprobe": {
        "win32": "winget install Gyan.FFmpeg",
        "darwin": "brew install ffmpeg",
        "linux": "sudo apt install ffmpeg",
    },
    "yt-dlp": {
        "win32": "pip install -U yt-dlp",
        "darwin": "pip install -U yt-dlp  (or brew install yt-dlp)",
        "linux": "pip install -U yt-dlp",
    },
}

# Sites that are login-walled: yt-dlp needs the user's cookies for these.
COOKIE_HOSTS = ("facebook.com", "fb.watch", "instagram.com", "douyin.com", "iesdouyin.com")
# Sites that BREAK when cookies are attached - never send cookies here.
NO_COOKIE_HOSTS = ("youtube.com", "youtu.be", "tiktok.com")


def die(msg: str, code: int = 1) -> "None":
    """Print an error to stderr and exit."""
    print(f"vidreader: {msg}", file=sys.stderr)
    sys.exit(code)


def require(binary: str) -> str:
    """Return the resolved path to `binary`, or exit with an install hint."""
    found = shutil.which(binary)
    if found:
        return found
    hint = INSTALL_HINTS.get(binary, {}).get(sys.platform, f"install {binary} and put it on PATH")
    die(f"'{binary}' not found on PATH. Install it with:\n    {hint}")


def run(cmd: list[str], check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    """Run a command, capturing output; raise a clean error on failure."""
    proc = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if check and proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-8:]
        die(f"command failed ({Path(cmd[0]).name}):\n" + "\n".join(tail))
    return proc


def out_dir(name_hint: str) -> Path:
    """A stable per-input output directory under the system temp dir."""
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in Path(name_hint).stem)[:40]
    d = Path(tempfile.gettempdir()) / "claude-vidreader" / (safe or "out")
    d.mkdir(parents=True, exist_ok=True)
    return d


def ffprobe_json(input_path: str) -> dict:
    """Return the parsed ffprobe JSON for an input (format + streams)."""
    ffprobe = require("ffprobe")
    proc = run([
        ffprobe, "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", input_path,
    ])
    return json.loads(proc.stdout)


def duration_seconds(input_path: str) -> float:
    """Best-effort media duration in seconds (0.0 if unknown)."""
    try:
        return float(ffprobe_json(input_path).get("format", {}).get("duration", 0.0))
    except Exception:
        return 0.0


def is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))


def host_of(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower().lstrip("www.")
    except Exception:
        return ""


def platform_of(url: str) -> str:
    """Rough platform label from a URL host."""
    h = host_of(url)
    for name, keys in (
        ("youtube", ("youtube.", "youtu.be")),
        ("tiktok", ("tiktok.",)),
        ("douyin", ("douyin.", "iesdouyin.")),
        ("instagram", ("instagram.",)),
        ("facebook", ("facebook.", "fb.watch")),
        ("twitter/x", ("twitter.", "x.com")),
        ("vimeo", ("vimeo.",)),
    ):
        if any(k in h for k in keys):
            return name
    return h or "unknown"


def cookie_args(url: str) -> list[str]:
    """yt-dlp cookie flags for this URL, honouring env config.

    VIDREADER_COOKIES_FILE    - path to a Netscape cookies.txt (most reliable)
    VIDREADER_COOKIES_BROWSER - browser name to read cookies live from

    Cookies are attached only for login-walled hosts, and deliberately never
    for YouTube/TikTok (YouTube rejects requests that carry them).
    """
    h = host_of(url)
    if any(k in h for k in NO_COOKIE_HOSTS):
        return []
    if not any(k in h for k in COOKIE_HOSTS):
        return []
    path = os.environ.get("VIDREADER_COOKIES_FILE", "").strip()
    if path and Path(path).expanduser().is_file():
        return ["--cookies", str(Path(path).expanduser())]
    browser = os.environ.get("VIDREADER_COOKIES_BROWSER", "").strip()
    if browser:
        return ["--cookies-from-browser", browser]
    return []


def needs_cookies(url: str) -> bool:
    """True if this URL is on a login-walled host and no cookies are configured."""
    h = host_of(url)
    return any(k in h for k in COOKIE_HOSTS) and not cookie_args(url)


COOKIE_HELP = (
    "This site requires your login session. Export cookies once:\n"
    "    yt-dlp --cookies-from-browser chrome --cookies cookies.txt \\\n"
    "        --skip-download \"https://www.youtube.com/watch?v=jNQXAC9IVRw\"\n"
    "then set VIDREADER_COOKIES_FILE=/absolute/path/to/cookies.txt and retry.\n"
    "(Replace 'chrome' with safari/edge/firefox/brave. Cookies expire after "
    "days-to-weeks; re-export when a site suddenly stops working.)"
)


def vtt_to_text(path: str | Path, with_timestamps: bool = True) -> str:
    """Convert a .vtt/.srt subtitle file to plain (optionally timestamped) text."""
    raw = Path(path).read_text(encoding="utf-8", errors="ignore")
    out: list[str] = []
    last = None
    stamp = ""
    for line in raw.splitlines():
        line = line.strip()
        if not line or line in ("WEBVTT",) or line.isdigit():
            continue
        if line.startswith(("NOTE", "Kind:", "Language:", "STYLE")):
            continue
        m = re.match(r"(\d{2}:)?\d{2}:\d{2}[.,]\d{3}\s*-->", line)
        if m:
            stamp = line.split("-->")[0].strip().split(".")[0].split(",")[0]
            continue
        text = re.sub(r"<[^>]+>", "", line).strip()
        if not text or text == last:
            continue
        last = text
        out.append(f"[{stamp}] {text}" if (with_timestamps and stamp) else text)
    return "\n".join(out)
