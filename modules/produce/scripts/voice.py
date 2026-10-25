#!/usr/bin/env python3
"""Brand voiceover through local Voicebox or VoiceStudio (both run on the user's machine).

  python scripts/voice.py health
  python scripts/voice.py list     --provider voicebox
  python scripts/voice.py clone    --provider voicebox    --name "Brand VO" --audio ref.wav --ref-text "exact words spoken" [--language en]
  python scripts/voice.py clone    --provider voicestudio --name "Brand VO" --audio ref.wav --ref-text "exact words spoken"
  python scripts/voice.py generate --scenes scenes.json --out vo/ [--brand brand/brand.json] [--provider ...] [--profile NAME|ID]
  python scripts/voice.py generate --text "One line" --out vo/line.wav --profile "Brand VO"

generate writes one WAV per scene (vo/<scene-id>.wav) and vo/manifest.json with measured durations,
seed, engine and the exact spoken text. Defaults come from brand.json -> voice {...}; flags override.

Licences: VoiceStudio's default OmniVoice weights are CC-BY-NC (non-commercial). For client or paid work
use Voicebox `qwen` (Apache-2.0 weights) or VoiceStudio `voxcpm2` / `cosyvoice` (Apache-2.0). Only clone a
voice you have written consent to clone.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (VOICEBOX_URLS, VOICESTUDIO_URLS, die, eprint, first_live, http, media_duration,  # noqa: E402
                     multipart, read_json, write_json)

NONCOMMERCIAL_ENGINES = {"omnivoice", "omnivoice-subprocess", "omnivoice-gguf"}


def base_url(provider: str, explicit: str | None) -> str:
    if explicit:
        return explicit.rstrip("/")
    urls = VOICEBOX_URLS if provider == "voicebox" else VOICESTUDIO_URLS
    b = first_live(urls)
    if not b:
        die(f"{provider} is not reachable on {', '.join(u for u in urls if u)}. Start the app (see references/voice.md) "
            f"or pass --url. Docker Voicebox listens on 127.0.0.1:17600.")
    return b  # type: ignore[return-value]


def detect_provider(explicit: str | None) -> str:
    if explicit:
        return explicit
    if first_live(VOICEBOX_URLS):
        return "voicebox"
    if first_live(VOICESTUDIO_URLS):
        return "voicestudio"
    die("Neither Voicebox (17493/17600) nor VoiceStudio (3900) is running. Start one, or pass --provider and --url.")
    return ""


def list_profiles(provider: str, url: str) -> list[dict]:
    code, _, body = http("GET", f"{url}/profiles", timeout=30)
    if code != 200:
        die(f"GET /profiles -> {code}: {body[:300]!r}")
    return json.loads(body)


def resolve_profile(provider: str, url: str, ref: str) -> str:
    profiles = list_profiles(provider, url)
    for p in profiles:
        if p.get("id") == ref:
            return ref
    matches = [p for p in profiles if str(p.get("name", "")).lower() == ref.lower()]
    if len(matches) == 1:
        return matches[0]["id"]
    if len(matches) > 1:
        die(f"Several profiles are named '{ref}': {[m['id'] for m in matches]}. Pass the id.")
    die(f"No {provider} profile '{ref}'. Existing: {[p.get('name') for p in profiles]}")
    return ""


def apply_lexicon(text: str, lexicon: dict[str, str]) -> str:
    """Respell brand words for TTS (e.g. {"Homely": "Home-lee"}). Captions keep the real spelling."""
    for word, say in (lexicon or {}).items():
        text = re.sub(rf"\b{re.escape(word)}\b", say, text)
    return text


# ------------------------------------------------------------------ Voicebox

def vb_generate(url: str, profile_id: str, text: str, out: Path, opts: dict) -> dict:
    body = {
        "profile_id": profile_id,
        "text": text,
        "language": opts.get("language", "en"),
        "normalize": opts.get("normalize", True),
    }
    for k in ("seed", "model_size", "instruct", "engine"):
        if opts.get(k) is not None:
            body[k] = opts[k]
    code, headers, data = http("POST", f"{url}/generate/stream", json_body=body, timeout=1800)
    if code == 200 and data[:4] == b"RIFF":
        out.write_bytes(data)
        return {"route": "generate/stream"}
    if code == 400 and b"not downloaded" in data:
        eprint("Model not cached yet; using async /generate (this triggers the download, first run can take minutes).")
    elif code != 200:
        eprint(f"/generate/stream -> {code}: {data[:300]!r}; retrying via async /generate")
    code, _, data = http("POST", f"{url}/generate", json_body=body, timeout=120)
    if code != 200:
        die(f"POST /generate -> {code}: {data[:400]!r}")
    gen = json.loads(data)
    gid = gen["id"]
    t0 = time.time()
    while True:
        code, _, data = http("GET", f"{url}/history/{gid}", timeout=30)
        if code == 200:
            h = json.loads(data)
            if h.get("status") == "completed":
                break
            if h.get("status") == "failed":
                die(f"Voicebox generation {gid} failed: {h.get('error')}")
        if time.time() - t0 > 3600:
            die(f"Voicebox generation {gid} timed out")
        time.sleep(3)
    code, _, data = http("GET", f"{url}/audio/{gid}", timeout=120)
    if code != 200:
        die(f"GET /audio/{gid} -> {code}")
    out.write_bytes(data)
    return {"route": "generate+poll", "generation_id": gid}


def vb_clone(url: str, name: str, audio: str, ref_text: str, language: str, engine: str) -> dict:
    code, _, data = http("POST", f"{url}/profiles", json_body={
        "name": name, "language": language, "voice_type": "cloned", "default_engine": engine,
        "description": "Brand voice created by master-brand-video-pipeline"}, timeout=60)
    if code not in (200, 201):
        die(f"POST /profiles -> {code}: {data[:400]!r}")
    prof = json.loads(data)
    body, ctype = multipart({"reference_text": ref_text}, {"file": audio})
    code, _, data = http("POST", f"{url}/profiles/{prof['id']}/samples", data=body, headers={"Content-Type": ctype}, timeout=300)
    if code not in (200, 201):
        die(f"POST /profiles/{prof['id']}/samples -> {code}: {data[:400]!r}  (clip must be 2-30 s, clean, and ref text must match exactly)")
    return {"id": prof["id"], "name": name}


# ------------------------------------------------------------------ VoiceStudio

def vs_generate(url: str, profile_id: str, text: str, out: Path, opts: dict) -> dict:
    engine = opts.get("engine")
    if engine in NONCOMMERCIAL_ENGINES and not opts.get("allow_noncommercial"):
        die(f"Engine '{engine}' has non-commercial (CC-BY-NC) weights. Use voxcpm2 or cosyvoice, or pass --allow-noncommercial for internal tests.")
    fields = {
        "text": text,
        "profile_id": profile_id,
        "language": opts.get("language"),
        "seed": opts.get("seed"),
        "engine": engine,
        "effect_preset": opts.get("effect_preset", "raw"),
        "wav_bits": str(opts.get("wav_bits", 24)),
        "duration": opts.get("target_duration"),
        "instruct": opts.get("instruct") if opts.get("vs_instruct") else None,
    }
    body, ctype = multipart(fields)
    for attempt in range(4):
        code, headers, data = http("POST", f"{url}/generate", data=body, headers={"Content-Type": ctype}, timeout=1800)
        if code == 503 and attempt < 3:
            eprint("VoiceStudio busy (503); retrying in 30 s")
            time.sleep(30)
            continue
        break
    if code == 403:
        die("VoiceStudio refused: the model licence has not been accepted in Model Catalogue (or the engine is blocked). Accept it in the app, or choose voxcpm2/cosyvoice.")
    if code != 200:
        die(f"POST /generate -> {code}: {data[:400]!r}")
    out.write_bytes(data)
    h = {k.lower(): v for k, v in headers.items()}
    if h.get("x-omnivoice-dropped-chunks"):
        eprint(f"WARNING: VoiceStudio dropped text chunks for {out.name}: {h['x-omnivoice-dropped-chunks']}")
    return {"route": "generate", "audio_id": h.get("x-audio-id"), "seed": h.get("x-seed")}


def vs_clone(url: str, name: str, audio: str, ref_text: str, language: str) -> dict:
    body, ctype = multipart({"name": name, "kind": "clone", "ref_text": ref_text, "language": language or "Auto"}, {"ref_audio": audio})
    code, _, data = http("POST", f"{url}/profiles", data=body, headers={"Content-Type": ctype}, timeout=600)
    if code not in (200, 201):
        die(f"POST /profiles -> {code}: {data[:400]!r}  (OmniVoice: 3-10 s is ideal; a transcript with a clip > 20 s is rejected)")
    p = json.loads(data)
    return {"id": p.get("id"), "name": name}


# ------------------------------------------------------------------ main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["health", "list", "clone", "generate"])
    ap.add_argument("--provider", choices=["voicebox", "voicestudio"])
    ap.add_argument("--url", help="Override base URL")
    ap.add_argument("--brand", help="brand.json (voice defaults + lexicon)")
    ap.add_argument("--profile", help="Profile name or id")
    ap.add_argument("--name", help="clone: new profile name")
    ap.add_argument("--audio", help="clone: reference clip")
    ap.add_argument("--ref-text", help="clone: exact transcript of the reference clip")
    ap.add_argument("--language")
    ap.add_argument("--engine", help="Voicebox: qwen|luxtts|chatterbox|chatterbox_turbo|tada|kokoro... VoiceStudio: voxcpm2|cosyvoice|indextts2|omnivoice...")
    ap.add_argument("--model-size", help="Voicebox: 1.7B|0.6B|1B|3B")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--instruct", help="Voicebox qwen delivery note, e.g. 'warm, confident, medium pace'")
    ap.add_argument("--scenes", help="scenes.json with scenes[].vo_text")
    ap.add_argument("--only", help="Comma list of scene ids to (re)generate")
    ap.add_argument("--text", help="Single line to speak")
    ap.add_argument("--out", required=False, help="Output folder (scenes) or .wav (single)")
    ap.add_argument("--effect-preset", default="raw", help="VoiceStudio: raw (default here) | broadcast | podcast | warm ...")
    ap.add_argument("--fit-duration", action="store_true", help="VoiceStudio: pass scenes[].target_vo_seconds as `duration`")
    ap.add_argument("--allow-noncommercial", action="store_true")
    a = ap.parse_args()

    brand_voice: dict = {}
    if a.brand:
        brand_voice = read_json(a.brand).get("voice", {}) or {}
    provider = a.provider or brand_voice.get("provider")
    if a.cmd == "health":
        print(json.dumps({"voicebox": first_live(VOICEBOX_URLS), "voicestudio": first_live(VOICESTUDIO_URLS)}, indent=2))
        return
    provider = detect_provider(provider)
    url = base_url(provider, a.url)

    if a.cmd == "list":
        for p in list_profiles(provider, url):
            print(f"{p.get('id')}\t{p.get('name')}\t{p.get('language', '')}\t{p.get('voice_type', p.get('kind', ''))}")
        return

    if a.cmd == "clone":
        if not (a.name and a.audio and a.ref_text):
            die("clone needs --name, --audio and --ref-text (the exact words in the clip)")
        dur = media_duration(a.audio)
        if provider == "voicebox" and not (2 <= dur <= 30):
            die(f"Reference is {dur:.1f}s. Voicebox needs 2-30 s (10-30 s clean speech recommended). Trim it.")
        if provider == "voicestudio" and dur > 20:
            die(f"Reference is {dur:.1f}s. VoiceStudio rejects >20 s with a transcript; trim clip and text to the same 3-10 s passage.")
        if provider == "voicebox":
            res = vb_clone(url, a.name, a.audio, a.ref_text, a.language or "en", a.engine or "qwen")
        else:
            res = vs_clone(url, a.name, a.audio, a.ref_text, a.language or "Auto")
        print(json.dumps({"provider": provider, **res}, indent=2))
        eprint("Store the profile id in brand.json -> voice.profile. Keep written consent from the voice owner on file.")
        return

    # generate
    profile_ref = a.profile or brand_voice.get("profile")
    if not profile_ref:
        die("Pass --profile or set voice.profile in brand.json")
    profile_id = resolve_profile(provider, url, profile_ref)
    opts = {
        "language": a.language or brand_voice.get("language", "en"),
        "seed": a.seed if a.seed is not None else brand_voice.get("seed"),
        "engine": a.engine or brand_voice.get("engine"),
        "model_size": a.model_size or brand_voice.get("model_size"),
        "instruct": a.instruct or brand_voice.get("instruct"),
        "effect_preset": a.effect_preset,
        "allow_noncommercial": a.allow_noncommercial,
    }
    if provider == "voicestudio" and not a.language:
        opts["language"] = None  # VoiceStudio: the profile's stored language drives generation unless pinned
    lexicon = brand_voice.get("lexicon", {})
    gen = vb_generate if provider == "voicebox" else vs_generate

    if a.text:
        out = Path(a.out or "vo/line.wav")
        out.parent.mkdir(parents=True, exist_ok=True)
        meta = gen(url, profile_id, apply_lexicon(a.text, lexicon), out, opts)
        print(json.dumps({"file": str(out), "duration": round(media_duration(str(out)), 3), **meta}, indent=2))
        return

    if not a.scenes:
        die("generate needs --scenes scenes.json or --text")
    scenes = read_json(a.scenes)
    out_dir = Path(a.out or Path(a.scenes).parent / "vo")
    out_dir.mkdir(parents=True, exist_ok=True)
    man_path = out_dir / "manifest.json"
    manifest = read_json(man_path) if man_path.exists() else {"scenes": {}}
    manifest.update({"provider": provider, "url": url, "profile_id": profile_id, "profile": profile_ref,
                     "engine": opts["engine"], "model_size": opts["model_size"], "seed": opts["seed"],
                     "instruct": opts["instruct"], "language": opts["language"]})
    only = set(a.only.split(",")) if a.only else None
    for s in scenes.get("scenes", []):
        sid, text = s["id"], (s.get("vo_text") or "").strip()
        if not text or (only and sid not in only):
            continue
        o = dict(opts)
        if a.fit_duration and s.get("target_vo_seconds"):
            o["target_duration"] = s["target_vo_seconds"]
        spoken = apply_lexicon(text, lexicon)
        wav = out_dir / f"{sid}.wav"
        eprint(f"[{sid}] {spoken[:70]}{'...' if len(spoken) > 70 else ''}")
        meta = gen(url, profile_id, spoken, wav, o)
        manifest["scenes"][sid] = {"file": wav.name, "duration": round(media_duration(str(wav)), 3),
                                   "text": text, "spoken_text": spoken, **meta}
        write_json(man_path, manifest)
    print(json.dumps(manifest, indent=2))
    eprint(f"Wrote {man_path}. Next: transcribe_words.py for word timings, then timeline_from_vo.py.")


if __name__ == "__main__":
    main()
