#!/usr/bin/env python3
"""RAY command line: one entry point for every module.

  python scripts/ray.py doctor [--tools-dir <toolchain>] [--json]
  python scripts/ray.py playbooks
  python scripts/ray.py tools
  python scripts/ray.py new "<project folder>" --kind person|brand|org --playbook <id> [--brand <kit dir or brand.json>]
                            [--engine remotion|hyperframes|both|none] [--title "Title"] [--film]
  python scripts/ray.py tool <name> [args...]        e.g.  tool frames clip.mp4 --max 8
                                                           tool voice generate --scenes scenes.json
                                                           tool read/probe file.mp4   (module/name when names clash)

Stdlib only (Python 3.10+). Module scripts keep their own --help.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAY = Path(__file__).resolve().parent.parent
MODULES = RAY / "modules"
TOOL_DIRS = [("read", MODULES / "read" / "scripts"), ("produce", MODULES / "produce" / "scripts"),
             ("direct", MODULES / "direct" / "tools")]
HIDDEN = {"_common", "common", "__init__"}
PLAYBOOKS = {
    "ads": "01-ads-and-commercials.md", "brand-film": "02-brand-films-and-stories.md", "social": "03-social-short-form.md",
    "explainer": "04-explainers-and-education.md", "product": "05-product-and-tech.md", "people": "06-people-on-camera.md",
    "audio": "07-podcast-and-audio.md", "org": "08-events-and-organisations.md", "motion": "09-motion-and-design.md",
    "localise": "10-localisation-and-accessibility.md", "batch": "11-personalised-and-batch.md",
    "narrative": "12-narrative-and-entertainment.md",
}
FILM_PLAYBOOKS = {"ads", "brand-film", "narrative"}


def all_tools() -> dict[str, list[tuple[str, Path]]]:
    found: dict[str, list[tuple[str, Path]]] = {}
    for mod, d in TOOL_DIRS:
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix in (".py", ".sh") and f.stem not in HIDDEN:
                found.setdefault(f.stem, []).append((mod, f))
    return found


def first_doc_line(f: Path) -> str:
    try:
        txt = f.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    m = re.search(r'"""(.*?)(?:\n|""")', txt, re.S) if f.suffix == ".py" else re.search(r"^#(?!!)\s*(.+)$", txt, re.M)
    return (m.group(1).strip() if m else "")[:100]


def run_tool(name: str, args: list[str]) -> int:
    tools = all_tools()
    if "/" in name:
        mod, stem = name.split("/", 1)
        cands = [(m, f) for m, f in tools.get(stem, []) if m == mod]
    else:
        cands = tools.get(name, [])
    if not cands:
        sys.exit(f"No tool '{name}'. Run: python scripts/ray.py tools")
    if len(cands) > 1:
        sys.exit(f"'{name}' exists in several modules: {', '.join(m + '/' + name for m, _ in cands)}. Use module/name.")
    mod, f = cands[0]
    if f.suffix == ".py":
        cmd = [sys.executable, str(f), *args]
    else:
        bash = shutil.which("bash")
        if not bash:
            sys.exit(f"{f.name} is a bash script. On Windows run it in Git Bash or WSL, or use the ffmpeg commands in modules/direct/tools/README.md.")
        cmd = [bash, str(f), *args]
    return subprocess.call(cmd)


def cmd_tools(_a) -> None:
    for stem, entries in sorted(all_tools().items()):
        for mod, f in entries:
            print(f"{mod + '/' + stem:<28} {first_doc_line(f)}")


def cmd_playbooks(_a) -> None:
    for pid, fname in PLAYBOOKS.items():
        title = ""
        p = RAY / "playbooks" / fname
        if p.exists():
            title = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
        print(f"{pid:<11} {title:<40} playbooks/{fname}")
    print(f"{'(add-on)':<11} {'13 · Industry notes':<40} playbooks/13-industry-notes.md")


def version(cmd: list[str]) -> str | None:
    exe = shutil.which(cmd[0])
    if not exe:
        return None
    try:
        r = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, timeout=30)
        out = (r.stdout or r.stderr or "").strip().splitlines()
        return out[0][:80] if out else "present"
    except Exception:  # noqa: BLE001
        return "present"


def cmd_doctor(a) -> None:
    doc = MODULES / "produce" / "scripts" / "doctor.py"
    args = [sys.executable, str(doc)]
    if a.tools_dir:
        args += ["--tools-dir", a.tools_dir]
    if a.json:
        args.append("--json")
    if a.deep:
        args.append("--deep")
    subprocess.call(args)
    extra = {
        "yt-dlp (Read: links)": version(["yt-dlp", "--version"]),
        "higgsfield CLI": version(["higgsfield", "--version"]) or version(["higgs", "--version"]),
        "audio-analyzer CLI/MCP": (shutil.which("audio-analyzer-mcp") or shutil.which("audio-analyzer")),
        "bash (Direct tools)": shutil.which("bash"),
    }
    for mod in ("faster_whisper", "whisper", "librosa", "pyloudnorm"):
        try:
            __import__(mod)
            extra[f"python: {mod}"] = "installed"
        except Exception:  # noqa: BLE001
            extra[f"python: {mod}"] = None
    hints = {
        "yt-dlp (Read: links)": "pip install -U yt-dlp",
        "higgsfield CLI": "optional: https://github.com/higgsfield-ai/cli (or connect the Higgsfield MCP: connectors/higgsfield.md)",
        "audio-analyzer CLI/MCP": "optional: modules/audio/references/setup.md",
        "bash (Direct tools)": "optional on Windows: Git Bash or WSL",
        "python: faster_whisper": "pip install faster-whisper   (local transcription)",
        "python: whisper": "optional alternative: pip install openai-whisper",
        "python: librosa": "optional (audio analysis fallback): pip install librosa",
        "python: pyloudnorm": "optional: pip install pyloudnorm",
    }
    if a.json:
        print(json.dumps({"ray_extra": extra}, indent=2))
        return
    print("\nRAY extras (Read / Direct / Audio modules):")
    for k, v in extra.items():
        print(f"[{'OK ' if v else '-- '}] {k:<26} {v or ''}")
        if not v:
            print(f"       {hints.get(k, '')}")
    print("\nMCP connectors can't be seen from a script: check the session's tool list (connectors/README.md).")


def cmd_new(a) -> None:
    np = MODULES / "produce" / "scripts" / "new_project.py"
    dest = Path(a.dest)
    args = [sys.executable, str(np), str(dest), "--engine", a.engine]
    if a.title:
        args += ["--title", a.title]
    if a.brand:
        args += ["--brand", a.brand]
    r = subprocess.call(args)
    if r != 0:
        sys.exit(r)
    if not a.brand and a.kind in ("person", "org"):
        src = RAY / "templates" / f"brand.{a.kind}.example.json"
        shutil.copy2(src, dest / "brand" / "brand.json")
        subprocess.call([sys.executable, str(MODULES / "produce" / "scripts" / "brand_tokens.py"), str(dest / "brand" / "brand.json"),
                         "--project", str(dest)], stdout=subprocess.DEVNULL)
        print(f"NOTE: brand/brand.json starts from the {a.kind} example. Fill it with the real kit before anything client-facing.")
    conn = dest / "brand" / "CONNECTORS.md"
    if not conn.exists():
        shutil.copy2(RAY / "templates" / "CONNECTORS.md", conn)
    film = a.film or a.playbook in FILM_PLAYBOOKS
    if film:
        d = dest / "direction"
        d.mkdir(exist_ok=True)
        for t in ("treatment.md", "shot-card.md", "prompt-pack.md", "client-shot-by-shot.md", "logline-sheet.md", "shots.example.json"):
            s = MODULES / "direct" / "templates" / t
            if s.exists():
                shutil.copy2(s, d / ("shots.json" if t == "shots.example.json" else t))
    pb = PLAYBOOKS.get(a.playbook)
    start = dest / "00_START_HERE.md"
    lines = ["", "## RAY plan", "",
             f"- **Kind:** {a.kind} · **Playbook:** {a.playbook} (`RAY/playbooks/{pb}`)" if pb else f"- **Kind:** {a.kind}",
             "- **Mode:** Quick / Standard / Full production / Advisory (circle one in BRIEF.md)",
             "- **Film direction files:** `direction/` (Direct module templates)" if film else "- Film direction files: not needed (add with `--film`)",
             "- **Connectors in use:** see `brand/CONNECTORS.md`", "",
             "### Spine checklist", ""]
    for step in ["Understand: brief + references (G)", "Kit: brand_tokens", "Story: concepts → script (G)",
                 "Plan the making: scenes/shots + engine (G)", "Voice & assets: samples → batch (G)", "Lock the clock: timeline_from_vo",
                 "Compose: preview link (G)", "Captions, mix, master", "Drafts → QA → finals (G)", "Deliver: manifest, sidecars, VERIFY.md"]:
        lines.append(f"- [ ] {step}")
    with open(start, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"RAY: project ready at {dest} (playbook: {a.playbook}{', film direction files added' if film else ''})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("doctor")
    p.add_argument("--tools-dir", default=os.environ.get("BVP_TOOLS", ""))
    p.add_argument("--json", action="store_true")
    p.add_argument("--deep", action="store_true")
    p.set_defaults(fn=cmd_doctor)
    sub.add_parser("playbooks").set_defaults(fn=cmd_playbooks)
    sub.add_parser("tools").set_defaults(fn=cmd_tools)
    p = sub.add_parser("new")
    p.add_argument("dest")
    p.add_argument("--kind", choices=["person", "brand", "org"], default="brand")
    p.add_argument("--playbook", choices=list(PLAYBOOKS), default="social")
    p.add_argument("--brand")
    p.add_argument("--engine", choices=["remotion", "hyperframes", "both", "none"], default="both")
    p.add_argument("--title")
    p.add_argument("--film", action="store_true")
    p.set_defaults(fn=cmd_new)
    p = sub.add_parser("tool")
    p.add_argument("name")
    p.add_argument("args", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    if a.cmd == "tool":
        sys.exit(run_tool(a.name, a.args))
    a.fn(a)


if __name__ == "__main__":
    main()
