#!/usr/bin/env python3
"""Scaffold a brand video project folder.

  python scripts/new_project.py "D:/AI Production/Homely - Spring Rates" --title "Spring Rates" \
        --brand "D:/AI Production/_brands/homely" --engine both

  --brand    a brand folder (containing brand.json, fonts/, logo/) or a brand.json file; copied into <project>/brand/.
             Omit to start from templates/brand.example.json (fill it in before anything else).
  --engine   remotion | hyperframes | both | none   (which composition starters to copy)

Creates:
  <project>/00_START_HERE.md BRIEF.md SCRIPT.md DECISIONS.md VERIFY.md scenes.json variants.json
  brand/ refs/ raw/ vo/ assets/{images,video,music,sfx}/ edit/ audio/ captions/ renders/drafts/ delivery/ prompts/
  remotion/   (Remotion brand-film starter, run `npm install` inside)
  hyperframes/ (brand.css + timeline feed; build index.html with hf_build.py or author by hand)
Then runs brand_tokens.py so every engine starts on-brand.
"""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import SKILL_DIR, die, read_json, write_json  # noqa: E402

TPL = SKILL_DIR / "templates"
DIRS = ["brand", "refs", "raw", "vo", "assets/images", "assets/video", "assets/music", "assets/sfx", "edit", "audio",
        "captions", "renders/drafts", "delivery", "prompts", "music_library"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dest")
    ap.add_argument("--title", default=None)
    ap.add_argument("--brand")
    ap.add_argument("--engine", default="both", choices=["remotion", "hyperframes", "both", "none"])
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()

    P = Path(a.dest)
    if P.exists() and any(P.iterdir()):
        die(f"{P} exists and is not empty. Pick a new folder (never scaffold over existing work).")
    P.mkdir(parents=True, exist_ok=True)
    for d in DIRS:
        (P / d).mkdir(parents=True, exist_ok=True)
    title = a.title or P.name
    today = dt.date.today().isoformat()
    for f in (TPL / "project").iterdir():
        if f.is_file():
            txt = f.read_text(encoding="utf-8").replace("{{TITLE}}", title).replace("{{DATE}}", today)
            (P / f.name).write_text(txt, encoding="utf-8")
    sfx = P / "sfx.example.json"
    if sfx.exists():
        sfx.replace(P / "audio" / "sfx.json")

    if a.brand:
        b = Path(a.brand)
        if b.is_dir():
            if not (b / "brand.json").exists():
                die(f"{b} has no brand.json")
            shutil.copytree(b, P / "brand", dirs_exist_ok=True)
        else:
            shutil.copy2(b, P / "brand" / "brand.json")
            for sub in ("fonts", "logo"):
                if (b.parent / sub).is_dir():
                    shutil.copytree(b.parent / sub, P / "brand" / sub, dirs_exist_ok=True)
    else:
        shutil.copy2(TPL / "brand.example.json", P / "brand" / "brand.json")
        print("NOTE: brand/brand.json is the EXAMPLE brand. Replace it with the real brand kit before making anything client-facing.")

    S = read_json(P / "scenes.json")
    S["title"] = title
    S["fps"] = a.fps
    write_json(P / "scenes.json", S)

    if a.engine in ("remotion", "both"):
        shutil.copytree(TPL / "remotion-brand", P / "remotion", ignore=shutil.ignore_patterns("node_modules", "renders", "out"))
    if a.engine in ("hyperframes", "both"):
        shutil.copytree(TPL / "hyperframes-brand", P / "hyperframes")

    subprocess.run([sys.executable, str(SKILL_DIR / "scripts" / "brand_tokens.py"), str(P / "brand" / "brand.json"), "--project", str(P)])
    print(f"\nPROJECT: {P}")
    print("Next: fill BRIEF.md -> SCRIPT.md -> scenes.json; then voice.py generate, transcribe_words.py, timeline_from_vo.py.")
    if a.engine in ("remotion", "both"):
        print(f"Remotion: cd \"{P / 'remotion'}\" && npm install && npx remotion studio")
    if a.engine in ("hyperframes", "both"):
        print(f"HyperFrames: python scripts/hf_build.py \"{P / 'hyperframes'}\" then cd there && npx hyperframes preview")


if __name__ == "__main__":
    main()
