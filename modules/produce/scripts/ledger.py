#!/usr/bin/env python3
"""Asset ledger: provenance, licence and cost for every file that ends up in a video.

  python scripts/ledger.py add assets/video/S04_kling.mp4 --source generated --provider higgsfield --model "Kling 3.0" \
        --prompt-file prompts/S04.txt --seed 123 --scene S04 --cost 0.42 --use 0.4-3.1
  python scripts/ledger.py add assets/music/bed.wav --source music --provider "Artlist" --license "Artlist Pro, licence #..." --url https://...
  python scripts/ledger.py check          # missing files, changed hashes, duplicate scene use, unlicensed items, total cost
  python scripts/ledger.py list

Writes assets/ledger.json in the project (or --ledger PATH). Why: clients ask "where did this shot come from
and can we use it?", platforms ask about AI content, and herk's rule is one use of each B-roll scene per reel.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import die, media_duration, read_json, write_json  # noqa: E402

SOURCES = ["footage", "generated", "stock", "official", "music", "sfx", "vo", "screen", "render", "other"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["add", "check", "list"])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--ledger", default="assets/ledger.json")
    ap.add_argument("--source", choices=SOURCES)
    ap.add_argument("--provider")
    ap.add_argument("--model")
    ap.add_argument("--prompt")
    ap.add_argument("--prompt-file")
    ap.add_argument("--seed")
    ap.add_argument("--task-id")
    ap.add_argument("--license")
    ap.add_argument("--url")
    ap.add_argument("--scene")
    ap.add_argument("--use", help="Used interval in source seconds, e.g. 0.4-3.1")
    ap.add_argument("--cost", type=float)
    ap.add_argument("--ai", action="store_true", help="AI-generated (for platform disclosure); implied by --source generated")
    ap.add_argument("--notes")
    a = ap.parse_args()
    lp = Path(a.ledger)
    L = read_json(lp) if lp.exists() else {"assets": []}

    if a.cmd == "add":
        if not a.file:
            die("add needs a file")
        p = Path(a.file)
        if not p.exists():
            die(f"{p} not found")
        entry = {
            "id": f"A{len(L['assets']) + 1:03d}", "file": str(p).replace("\\", "/"), "sha256": sha(p), "bytes": p.stat().st_size,
            "source": a.source or "other", "provider": a.provider, "model": a.model,
            "prompt": Path(a.prompt_file).read_text(encoding="utf-8") if a.prompt_file else a.prompt,
            "seed": a.seed, "task_id": a.task_id, "license": a.license, "original_url": a.url, "scene": a.scene,
            "used_interval": [float(x) for x in a.use.split("-")] if a.use else None,
            "cost_usd": a.cost, "ai_generated": bool(a.ai or a.source == "generated"), "notes": a.notes,
            "added": dt.datetime.now().isoformat(timespec="seconds"),
        }
        if p.suffix.lower() in {".mp4", ".mov", ".webm", ".wav", ".mp3", ".m4a", ".mkv"}:
            try:
                entry["duration"] = round(media_duration(str(p)), 3)
            except SystemExit:
                pass
        L["assets"].append({k: v for k, v in entry.items() if v is not None})
        write_json(lp, L)
        print(f"ADDED {entry['id']}: {entry['file']}")
        return

    if a.cmd == "list":
        for e in L["assets"]:
            print(f"{e['id']}  {e.get('scene', '-'):<5} {e.get('source', ''):<9} {e.get('provider', '') or '':<12} {e['file']}")
        return

    problems, seen = [], {}
    total = 0.0
    for e in L["assets"]:
        p = Path(e["file"])
        if not p.exists():
            problems.append(f"{e['id']} missing file {p}")
        elif sha(p) != e["sha256"]:
            problems.append(f"{e['id']} {p} changed since it was logged (re-log or restore)")
        if e.get("source") in ("stock", "music", "sfx", "official") and not e.get("license"):
            problems.append(f"{e['id']} {p.name}: {e.get('source')} asset without a licence note")
        if e.get("source") in ("footage", "generated", "stock") and e.get("scene"):
            key = e["sha256"]
            if key in seen and seen[key] != e["scene"]:
                problems.append(f"{e['id']} {p.name}: same clip used in scenes {seen[key]} and {e['scene']} (one use per reel)")
            seen[key] = e["scene"]
        total += float(e.get("cost_usd") or 0)
    ai = sum(1 for e in L["assets"] if e.get("ai_generated"))
    print(f"{len(L['assets'])} assets · {ai} AI-generated · spend ${total:.2f}")
    for pr in problems:
        print(f"FIX {pr}")
    if ai:
        print("Remember: turn on the platform's AI-generated content label for this video.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
