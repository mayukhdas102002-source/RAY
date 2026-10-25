"""Shared helpers for the master-brand-video-pipeline scripts.

Stdlib only (Python 3.9+). Works on Windows, macOS and Linux.
"""
from __future__ import annotations

import json
import mimetypes
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SKILL_DIR = Path(__file__).resolve().parent.parent

# Default local service endpoints (override with env vars).
VOICEBOX_URLS = [os.environ.get("VOICEBOX_URL", ""), "http://127.0.0.1:17493", "http://127.0.0.1:17600"]
VOICESTUDIO_URLS = [os.environ.get("VOICESTUDIO_URL", ""), "http://127.0.0.1:3900"]


def eprint(*a: Any) -> None:
    print(*a, file=sys.stderr)


def die(msg: str, code: int = 1) -> None:
    eprint(f"ERROR: {msg}")
    sys.exit(code)


def which(name: str) -> Optional[str]:
    return shutil.which(name)


def run(cmd: List[str], check: bool = True, capture: bool = False, cwd: Optional[str] = None,
        timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """Run a command list. On Windows, npx/npm are .cmd shims, so resolve them first."""
    exe = cmd[0]
    resolved = shutil.which(exe) or exe
    full = [resolved] + list(cmd[1:])
    try:
        return subprocess.run(full, check=check, cwd=cwd, timeout=timeout,
                              stdout=subprocess.PIPE if capture else None,
                              stderr=subprocess.PIPE if capture else None,
                              text=True if capture else None)
    except FileNotFoundError:
        die(f"'{exe}' not found on PATH. Run scripts/doctor.py for install steps.")
        raise  # unreachable


def need(binary: str, hint: str) -> str:
    p = which(binary)
    if not p:
        die(f"'{binary}' is required. {hint}")
    return p  # type: ignore[return-value]


FFMPEG_HINT = "Install FFmpeg 7+: Windows `winget install Gyan.FFmpeg`, macOS `brew install ffmpeg`, Linux `sudo apt install ffmpeg`."


def ffprobe_json(path: str) -> Dict[str, Any]:
    need("ffprobe", FFMPEG_HINT)
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path], capture=True)
    return json.loads(r.stdout or "{}")


def media_duration(path: str) -> float:
    info = ffprobe_json(path)
    d = info.get("format", {}).get("duration")
    if d is None:
        for s in info.get("streams", []):
            if s.get("duration"):
                d = s["duration"]
                break
    return float(d or 0.0)


def read_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, data: Any) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_text(path: str | Path, text: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------- HTTP

def http(method: str, url: str, *, json_body: Any = None, data: bytes | None = None,
         headers: Optional[Dict[str, str]] = None, timeout: float = 600) -> Tuple[int, Dict[str, str], bytes]:
    h = dict(headers or {})
    body = data
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers.items()), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers.items()) if e.headers else {}, e.read() or b""


def multipart(fields: Dict[str, Any], files: Dict[str, str] | None = None) -> Tuple[bytes, str]:
    """Encode multipart/form-data. `fields` values may be str/int/float/bool or a list (repeated field)."""
    boundary = "----bvp" + uuid.uuid4().hex
    out: List[bytes] = []

    def add_field(name: str, value: Any) -> None:
        if isinstance(value, bool):
            value = "true" if value else "false"
        out.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8"))

    for k, v in fields.items():
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            for item in v:
                add_field(k, item)
        else:
            add_field(k, v)
    for k, p in (files or {}).items():
        fname = os.path.basename(p)
        ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
        with open(p, "rb") as f:
            content = f.read()
        out.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fname}\"\r\nContent-Type: {ctype}\r\n\r\n".encode("utf-8")
            + content + b"\r\n")
    out.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(out), f"multipart/form-data; boundary={boundary}"


def first_live(urls: Iterable[str], path: str = "/health", timeout: float = 2.0) -> Optional[str]:
    for base in urls:
        if not base:
            continue
        try:
            code, _, _ = http("GET", base.rstrip("/") + path, timeout=timeout)
            if code < 500:
                return base.rstrip("/")
        except Exception:
            continue
    return None


# ---------------------------------------------------------------- timing helpers

def ts_srt(t: float) -> str:
    t = max(0.0, t)
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ts_vtt(t: float) -> str:
    return ts_srt(t).replace(",", ".")


def load_words(path: str) -> Dict[str, Any]:
    """Load any supported transcript into {text, duration, words:[{text,start,end}]} (seconds).

    Accepts: this skill's transcript.json, herk-edit-kit / ElevenLabs Scribe ({words:[...]} with type),
    HyperFrames transcript.json (array of {text,start,end}), OpenAI/VoiceStudio verbose_json
    ({words:[{word,start,end}]} or {segments:[{words:[...]}]}), Remotion Caption[] (startMs/endMs).
    """
    data = read_json(path)
    words: List[Dict[str, Any]] = []

    def push(w: Dict[str, Any]) -> None:
        if w.get("type") not in (None, "word"):
            return
        text = w.get("text", w.get("word", ""))
        if "startMs" in w:
            start, end = w["startMs"] / 1000.0, w["endMs"] / 1000.0
        else:
            start, end = w.get("start"), w.get("end")
        if text is None or start is None or end is None:
            return
        words.append({"text": str(text).strip(), "start": float(start), "end": float(end)})

    if isinstance(data, list):
        for w in data:
            push(w)
        duration = words[-1]["end"] if words else 0.0
        text = " ".join(w["text"] for w in words)
    else:
        if data.get("words"):
            for w in data["words"]:
                push(w)
        elif data.get("segments"):
            for seg in data["segments"]:
                for w in seg.get("words", []) or []:
                    push(w)
        duration = float(data.get("duration") or data.get("audio_duration_secs") or (words[-1]["end"] if words else 0.0))
        text = data.get("text") or " ".join(w["text"] for w in words)
    words = [w for w in words if w["text"]]
    words.sort(key=lambda w: w["start"])
    return {"text": text, "duration": duration, "words": words}
