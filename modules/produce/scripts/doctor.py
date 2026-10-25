#!/usr/bin/env python3
"""Check every tool the brand video pipeline can use and say which routes are ready.

Usage:
  python scripts/doctor.py                       # quick check
  python scripts/doctor.py --deep                # also runs `npx hyperframes doctor --json`
  python scripts/doctor.py --tools-dir "D:/AI Production/_toolchain" --json

Never prints secret values: API keys are reported as present/absent only.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VOICEBOX_URLS, VOICESTUDIO_URLS, first_live, http, run, which  # noqa: E402

INSTALL = {
    "node": "Node 22+: Windows `winget install OpenJS.NodeJS.LTS`, macOS `brew install node@22`, Linux via nodesource or nvm.",
    "ffmpeg": "FFmpeg 7+ with ffprobe: Windows `winget install Gyan.FFmpeg`, macOS `brew install ffmpeg`, Linux `sudo apt install ffmpeg` (Ubuntu 22.04 ships 4.4; use a static build for 7+).",
    "git": "Git: Windows `winget install Git.Git`, macOS `xcode-select --install`, Linux `sudo apt install git`.",
    "python": "Python 3.10+ (3.12 recommended): https://www.python.org/downloads/ or `winget install Python.Python.3.12`.",
    "uv": "Optional, used by OpenMontage/VoiceStudio/HyperFrames captions: `pip install uv` or https://docs.astral.sh/uv/.",
    "pnpm": "Only for Pireel OSS: `corepack enable` (ships with Node).",
    "voicebox": "Voicebox desktop app: https://voicebox.sh (Windows NSIS/MSI). NVIDIA: Settings → GPU → Install CUDA backend. API on 127.0.0.1:17493.",
    "voicestudio": "VoiceStudio: Windows PowerShell `irm https://voicestudio.sh/install | iex` or the release .exe. API on 127.0.0.1:3900.",
    "openmontage": "git clone https://github.com/calesthio/OpenMontage.git && cd OpenMontage && make setup (or the manual venv steps in references/openmontage.md).",
    "herk": "git clone https://github.com/nateherkai/herk-edit-kit.git && cd herk-edit-kit && npm ci && npm run setup.",
    "pireel": "git clone https://github.com/pireel/pireel.git && cd pireel && corepack enable && pnpm install && pnpm dev. Agent control is hosted: claude plugin marketplace add pireel/pireel-agent.",
}

KEY_GROUPS = {
    "TTS / STT (cloud)": ["ELEVENLABS_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY", "AZURE_SPEECH_KEY", "FISH_AUDIO_API_KEY", "CARTESIA_API_KEY", "GROQ_API_KEY"],
    "Image / video generation": ["FAL_KEY", "REPLICATE_API_TOKEN", "KLING_API_KEY", "RUNWAY_API_KEY", "HIGGSFIELD_API_KEY", "XAI_API_KEY", "IDEOGRAM_API_KEY", "MINIMAX_API_KEY", "KIE_API_KEY", "HEYGEN_API_KEY", "LTX_API_KEY", "ARK_API_KEY"],
    "Music / SFX": ["SUNO_API_KEY", "FREESOUND_API_KEY"],
    "Stock": ["PEXELS_API_KEY", "PIXABAY_API_KEY", "UNSPLASH_ACCESS_KEY"],
    "Render cloud": ["REMOTION_AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID", "FIGMA_TOKEN"],
}


def version_of(cmd: list[str]) -> str | None:
    if not which(cmd[0]):
        return None
    try:
        r = run(cmd, check=False, capture=True, timeout=60)
        out = (r.stdout or "") + (r.stderr or "")
        return out.strip().splitlines()[0] if out.strip() else "present"
    except Exception:
        return "present"


def major(v: str | None) -> int:
    if not v:
        return 0
    m = re.search(r"(\d+)\.(\d+)", v)
    return int(m.group(1)) if m else 0


def env_keys(tools_dir: Path | None) -> dict[str, bool]:
    present = {k: bool(os.environ.get(k)) for g in KEY_GROUPS.values() for k in g}
    candidates = [Path.cwd() / ".env"]
    if tools_dir:
        candidates += [tools_dir / "OpenMontage" / ".env", tools_dir / "herk-edit-kit" / ".env"]
    for f in candidates:
        if f.is_file():
            for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                m = re.match(r"\s*([A-Z0-9_]+)\s*=\s*(\S+)", line)
                if m and m.group(1) in present and not m.group(2).startswith("#"):
                    present[m.group(1)] = True
    return present


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tools-dir", default=os.environ.get("BVP_TOOLS", ""), help="Folder holding OpenMontage/, herk-edit-kit/, pireel/ clones (env BVP_TOOLS)")
    ap.add_argument("--deep", action="store_true", help="Also run `npx hyperframes doctor --json` (slow on first run)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    tools = Path(a.tools_dir) if a.tools_dir else None

    r: dict = {"os": f"{platform.system()} {platform.release()} ({platform.machine()})", "checks": {}, "warnings": []}
    c = r["checks"]

    node = version_of(["node", "-v"])
    c["node"] = {"version": node, "ok": major(node.lstrip("v") if node else None) >= 22}
    c["npx"] = {"ok": bool(which("npx"))}
    ff = version_of(["ffmpeg", "-version"])
    ffm = major(ff.split("version")[-1] if ff else None)
    c["ffmpeg"] = {"version": ff, "ok": bool(ff) and bool(which("ffprobe"))}
    if ff and ffm and ffm < 7:
        r["warnings"].append(f"FFmpeg {ffm}.x found. herk-edit-kit cutters need FFmpeg 7+ (`-/filter_complex`); HyperFrames and this skill work with older builds.")
    c["git"] = {"version": version_of(["git", "--version"]), "ok": bool(which("git"))}
    py = sys.version.split()[0]
    c["python"] = {"version": py, "ok": sys.version_info >= (3, 10)}
    c["uv"] = {"version": version_of(["uv", "--version"]), "ok": bool(which("uv")), "optional": True}
    c["pnpm"] = {"version": version_of(["pnpm", "-v"]), "ok": bool(which("pnpm")), "optional": True}
    c["docker"] = {"version": version_of(["docker", "--version"]), "ok": bool(which("docker")), "optional": True}

    vb = first_live(VOICEBOX_URLS)
    c["voicebox"] = {"url": vb, "ok": bool(vb), "optional": True}
    if vb:
        code, _, body = http("GET", vb + "/health", timeout=5)
        try:
            h = json.loads(body)
            c["voicebox"].update({"gpu": h.get("gpu_type") or h.get("gpu_available"), "backend": h.get("backend_type")})
        except Exception:
            pass
        code, _, body = http("GET", vb + "/profiles", timeout=5)
        if code == 200:
            c["voicebox"]["profiles"] = [p.get("name") for p in json.loads(body)][:20]
    vs = first_live(VOICESTUDIO_URLS)
    c["voicestudio"] = {"url": vs, "ok": bool(vs), "optional": True}
    if vs:
        code, _, body = http("GET", vs + "/profiles", timeout=5)
        if code == 200:
            try:
                c["voicestudio"]["profiles"] = [p.get("name") for p in json.loads(body)][:20]
            except Exception:
                pass

    if tools:
        c["openmontage"] = {"path": str(tools / "OpenMontage"), "ok": (tools / "OpenMontage" / "AGENT_GUIDE.md").is_file(), "optional": True}
        c["herk"] = {"path": str(tools / "herk-edit-kit"), "ok": (tools / "herk-edit-kit" / "package.json").is_file(), "optional": True}
        c["pireel"] = {"path": str(tools / "pireel"), "ok": (tools / "pireel" / "package.json").is_file(), "optional": True}
    else:
        r["warnings"].append("No --tools-dir / BVP_TOOLS set, so OpenMontage, herk-edit-kit and Pireel clones were not checked.")

    if a.deep and which("npx"):
        try:
            out = run(["npx", "--yes", "hyperframes", "doctor", "--json"], check=False, capture=True, timeout=300)
            hf = json.loads(out.stdout or "{}")
            c["hyperframes_doctor"] = {"ok": bool(hf.get("ok")), "summary": {k: v for k, v in hf.items() if k in ("ok", "checks")}}
        except Exception as e:  # noqa: BLE001
            c["hyperframes_doctor"] = {"ok": False, "error": str(e)}

    keys = env_keys(tools)
    r["api_keys_present"] = {g: [k for k in ks if keys.get(k)] for g, ks in KEY_GROUPS.items()}

    core = c["node"]["ok"] and c["npx"]["ok"] and c["ffmpeg"]["ok"] and c["python"]["ok"]
    r["routes"] = {
        "remotion": core,
        "hyperframes": core,
        "local_voice": c["voicebox"]["ok"] or c["voicestudio"]["ok"],
        "word_timestamps_local": c["voicestudio"]["ok"],
        "openmontage": core and c.get("openmontage", {}).get("ok", False),
        "herk_talking_head": core and c.get("herk", {}).get("ok", False),
        "pireel_local_editor": c.get("pireel", {}).get("ok", False) and c["pnpm"]["ok"],
    }

    if a.json:
        print(json.dumps(r, indent=2))
        return
    print(f"OS: {r['os']}\n")
    for name, v in c.items():
        mark = "OK " if v.get("ok") else ("-- " if v.get("optional") else "XX ")
        detail = v.get("version") or v.get("url") or v.get("path") or ""
        print(f"[{mark}] {name:<18} {detail}")
        if not v.get("ok") and name in INSTALL:
            print(f"       install: {INSTALL[name]}")
        if v.get("profiles"):
            print(f"       voice profiles: {', '.join(p for p in v['profiles'] if p)}")
    print("\nAPI keys present (values never shown):")
    for g, ks in r["api_keys_present"].items():
        print(f"  {g}: {', '.join(ks) if ks else 'none'}")
    print("\nRoutes ready:")
    for k, v in r["routes"].items():
        print(f"  {'yes' if v else 'no ':<4} {k}")
    for w in r["warnings"]:
        print(f"\nWARNING: {w}")


if __name__ == "__main__":
    main()
