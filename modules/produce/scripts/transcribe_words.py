#!/usr/bin/env python3
"""Word-level transcript for captions, cut planning and beat anchoring.

  python scripts/transcribe_words.py vo/S01.wav                         # -> vo/S01.words.json
  python scripts/transcribe_words.py raw/take1.mp4 --backend faster-whisper --model small
  python scripts/transcribe_words.py vo/ --script scenes.json           # every WAV in a folder, fix spellings from the script
  python scripts/transcribe_words.py clip.mp4 --format hyperframes --out transcript.json

Output (default, "herk" shape - also read by herk-edit-kit cutters and this skill's tools):
  {"text": "...", "duration": 12.3, "audio_duration_secs": 12.3, "backend": "...",
   "words": [{"text": "Hello", "start": 0.20, "end": 0.61}]}
--format hyperframes writes the HyperFrames array shape [{"text","start","end"}].

Backends (auto picks the first available, all local first):
  voicestudio     VoiceStudio /v1/audio/transcriptions (WhisperX forced alignment)    local, best timing
  faster-whisper  pip install faster-whisper (word_timestamps=True)                   local
  hyperframes     npx hyperframes transcribe (whisper.cpp / Parakeet)                  local, Node 22
  openai          OpenAI whisper-1 verbose_json + word granularity                     cloud, OPENAI_API_KEY
  elevenlabs      ElevenLabs Scribe speech-to-text                                     cloud, ELEVENLABS_API_KEY
Never use a `.en` model unless the audio is English: `.en` models translate other languages.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (VOICESTUDIO_URLS, die, eprint, first_live, http, load_words, media_duration,  # noqa: E402
                     multipart, read_json, run, which, write_json)

AUDIO_EXT = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".mp4", ".mov", ".mkv", ".webm"}


def extract_audio(src: str) -> str:
    """16 kHz mono WAV for ASR (also strips video)."""
    out = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", out])
    return out


def via_voicestudio(path: str, language: str | None, url: str) -> dict:
    fields = {"model": "whisper-1", "response_format": "verbose_json", "timestamp_granularities[]": ["word", "segment"], "language": language}
    body, ctype = multipart(fields, {"file": path})
    code, _, data = http("POST", f"{url}/v1/audio/transcriptions", data=body, headers={"Content-Type": ctype}, timeout=3600)
    if code == 409:
        die("VoiceStudio has no ASR model installed yet. Install one in the app (Model Catalogue) or use --backend faster-whisper.")
    if code != 200:
        die(f"VoiceStudio transcription -> {code}: {data[:300]!r}")
    return json.loads(data)


def via_faster_whisper(path: str, language: str | None, model: str) -> dict:
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        die("faster-whisper not installed: pip install faster-whisper  (or use --backend voicestudio/hyperframes)")
    m = WhisperModel(model, device="auto", compute_type="auto")
    segments, info = m.transcribe(path, language=language, word_timestamps=True, vad_filter=True)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"text": w.word.strip(), "start": float(w.start), "end": float(w.end)})
    return {"text": " ".join(w["text"] for w in words), "duration": float(info.duration), "words": words}


HF_MODELS = {"tiny.en", "base.en", "small.en", "medium.en", "large-v3"}


def via_hyperframes(path: str, language: str | None, model: str) -> dict:
    if model not in HF_MODELS:
        # HyperFrames ships English-only *.en models plus multilingual large-v3.
        model = f"{model}.en" if language == "en" and f"{model}.en" in HF_MODELS else "large-v3"
        eprint(f"  hyperframes model -> {model} (pass --language en to use a fast .en model on English audio)")
    with tempfile.TemporaryDirectory() as d:
        cmd = ["npx", "--yes", "hyperframes", "transcribe", os.path.abspath(path), "--model", model, "--dir", d]
        if language:
            cmd += ["--language", language]
        run(cmd, cwd=d, timeout=3600)  # writes <dir>/transcript.json
        out = Path(d) / "transcript.json"
        if not out.exists():
            cands = list(Path(d).glob("*.json"))
            if not cands:
                die("hyperframes transcribe produced no transcript.json")
            out = cands[0]
        return load_words(str(out))


def via_openai(path: str, language: str | None) -> dict:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        die("OPENAI_API_KEY not set")
    fields = {"model": "whisper-1", "response_format": "verbose_json", "timestamp_granularities[]": ["word", "segment"], "language": language}
    body, ctype = multipart(fields, {"file": path})
    code, _, data = http("POST", "https://api.openai.com/v1/audio/transcriptions", data=body,
                         headers={"Content-Type": ctype, "Authorization": f"Bearer {key}"}, timeout=3600)
    if code != 200:
        die(f"OpenAI transcription -> {code}: {data[:300]!r}  (25 MB upload limit: split long audio)")
    return json.loads(data)


def via_elevenlabs(path: str, language: str | None) -> dict:
    key = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("XI_API_KEY")
    if not key:
        die("ELEVENLABS_API_KEY not set")
    fields = {"model_id": "scribe_v1", "timestamps_granularity": "word", "diarize": "true", "language_code": language}
    body, ctype = multipart(fields, {"file": path})
    code, _, data = http("POST", "https://api.elevenlabs.io/v1/speech-to-text", data=body,
                         headers={"Content-Type": ctype, "xi-api-key": key}, timeout=3600)
    if code != 200:
        die(f"ElevenLabs -> {code}: {data[:300]!r}  (403 = key lacks speech_to_text access)")
    return json.loads(data)


def normalize(raw: dict) -> dict:
    tmp = Path(tempfile.mkstemp(suffix=".json")[1])
    tmp.write_text(json.dumps(raw), encoding="utf-8")
    try:
        return load_words(str(tmp))
    finally:
        tmp.unlink(missing_ok=True)


_norm = lambda s: re.sub(r"[^\w']+", "", s.lower())  # noqa: E731


def fix_spellings(words: list[dict], script_text: str) -> int:
    """Align ASR tokens to the script and copy the script's spelling where tokens map 1:1.
    Keeps ASR timing; only text changes (brand names, product names, numbers written your way)."""
    script_tokens = [t for t in re.findall(r"\S+", script_text) if _norm(t)]
    a = [_norm(w["text"]) for w in words]
    b = [_norm(t) for t in script_tokens]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    changed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and (i2 - i1) == (j2 - j1)):
            for k in range(i2 - i1):
                new = script_tokens[j1 + k]
                if words[i1 + k]["text"] != new:
                    words[i1 + k]["text"] = new
                    changed += 1
    return changed


def transcribe_one(src: str, a, script_text: str | None) -> dict:
    backend = a.backend
    vs_url = first_live(VOICESTUDIO_URLS) if backend in ("auto", "voicestudio") else None
    if backend == "auto":
        if vs_url:
            backend = "voicestudio"
        else:
            try:
                import faster_whisper  # noqa: F401
                backend = "faster-whisper"
            except ImportError:
                backend = "hyperframes" if which("npx") else ""
        if not backend:
            die("No transcription backend: start VoiceStudio, `pip install faster-whisper`, or install Node 22 for HyperFrames.")
    if backend == "voicestudio" and not vs_url:
        die("VoiceStudio not reachable on :3900")
    audio = src
    if Path(src).suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"} or backend in ("faster-whisper",):
        audio = extract_audio(src)
    eprint(f"[{backend}] {src}")
    if backend == "voicestudio":
        res = normalize(via_voicestudio(audio, a.language, vs_url))
    elif backend == "faster-whisper":
        res = via_faster_whisper(audio, a.language, a.model)
    elif backend == "hyperframes":
        res = via_hyperframes(audio, a.language, a.model)
    elif backend == "openai":
        res = normalize(via_openai(audio, a.language))
    elif backend == "elevenlabs":
        res = normalize(via_elevenlabs(audio, a.language))
    else:
        die(f"unknown backend {backend}")
    if not res.get("duration"):
        res["duration"] = media_duration(src)
    res["audio_duration_secs"] = res["duration"]
    res["backend"] = backend
    res["source"] = os.path.basename(src)
    if script_text:
        n = fix_spellings(res["words"], script_text)
        res["text"] = " ".join(w["text"] for w in res["words"])
        eprint(f"  script alignment: {n} word spellings taken from the script")
    junk = sum(1 for w in res["words"] if re.fullmatch(r"[♪�\W]+", w["text"]))
    if res["words"] and junk / len(res["words"]) > 0.2:
        eprint("  WARNING: >20% junk tokens. Retry with a larger model (medium/large-v3) or another backend.")
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Audio/video file or a folder of them")
    ap.add_argument("--backend", default="auto", choices=["auto", "voicestudio", "faster-whisper", "hyperframes", "openai", "elevenlabs"])
    ap.add_argument("--model", default="small", help="faster-whisper / hyperframes model (small, medium, large-v3; *.en for English only)")
    ap.add_argument("--language", help="ISO code, e.g. en. Omit to auto-detect.")
    ap.add_argument("--script", help="scenes.json (uses scenes[].vo_text by file stem) or a .txt to copy spellings from")
    ap.add_argument("--format", default="herk", choices=["herk", "hyperframes"])
    ap.add_argument("--out", help="Output file (single input only). Default: <input>.words.json")
    a = ap.parse_args()

    p = Path(a.input)
    files = sorted(f for f in p.iterdir() if f.suffix.lower() in AUDIO_EXT) if p.is_dir() else [p]
    if not files:
        die(f"No audio/video files in {p}")
    script_by_id: dict[str, str] = {}
    script_all = None
    if a.script:
        if a.script.endswith(".json"):
            for s in read_json(a.script).get("scenes", []):
                if s.get("vo_text"):
                    script_by_id[s["id"]] = s["vo_text"]
        else:
            script_all = Path(a.script).read_text(encoding="utf-8")
    for f in files:
        res = transcribe_one(str(f), a, script_by_id.get(f.stem) or script_all or (" ".join(script_by_id.values()) if script_by_id else None))
        out = Path(a.out) if (a.out and len(files) == 1) else f.with_suffix(".words.json")
        write_json(out, res["words"] if a.format == "hyperframes" else res)
        print(f"WORDS: {out}  ({len(res['words'])} words, {res['duration']:.2f}s)")


if __name__ == "__main__":
    main()
