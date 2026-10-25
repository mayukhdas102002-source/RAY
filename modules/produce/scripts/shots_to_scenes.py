#!/usr/bin/env python3
"""Bridge from the AI Director skill: convert its shots.json into this pipeline's scenes.json.

  python scripts/shots_to_scenes.py "../Artisan Escape - The Deep Breath/shots.json" --out scenes.json [--media-dir assets/video]

AI Director owns concept, shot list, keyframe + motion prompts and Higgsfield model allocation.
This pipeline then owns voice, captions, Remotion/HyperFrames text layer, mix, QA and versions.

Mapping per shot -> scene:
  id            -> id                  t[start,end] -> fixed duration (picture-led films keep the director's timing)
  maker "AI*"   -> kind footage, media = <media-dir>/<id>.mp4 if that plate exists (else a placeholder you swap later)
  maker Remotion-> kind statement/endCard (copy from `remotion` / `name`)
  sound         -> lines in "QUOTES" or after NAME: become vo_text candidates (review them)
  frame/name/model/note are kept in `notes` for reference.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import read_json, write_json  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shots")
    ap.add_argument("--out", required=True)
    ap.add_argument("--media-dir", default="assets/video")
    ap.add_argument("--fps", type=int, default=24)
    a = ap.parse_args()
    S = read_json(a.shots)
    out_dir = Path(a.out).parent
    scenes = []
    for sh in S.get("shots", []):
        t0, t1 = sh.get("t", [0, 0])
        maker = (sh.get("maker") or "").lower()
        vo = " ".join(re.findall(r"[“\"]([^”\"]+)[”\"]", sh.get("sound", "")))
        sc = {"id": sh["id"], "duration": round(float(t1) - float(t0), 3), "vo_text": vo,
              "notes": {k: sh.get(k) for k in ("name", "frame", "model", "maker", "remotion", "note", "sound") if sh.get(k)}}
        if maker.startswith("ai") or "effect" in maker:
            sc["kind"] = "footage"
            plate = Path(a.media_dir) / f"{sh['id']}.mp4"
            sc["media"] = str(plate).replace("\\", "/")
            if not (out_dir / plate).exists():
                sc["notes"]["todo"] = f"Generate/drop the plate at {plate}"
            if sh.get("remotion"):
                sc["notes"]["text_layer"] = sh["remotion"]
        else:
            last = sh is S["shots"][-1]
            sc["kind"] = "endCard" if last else "statement"
            sc["headline"] = sh.get("name", "")
        scenes.append(sc)
    write_json(a.out, {"title": S.get("title", ""), "fps": a.fps, "pad": {"lead": 0.0, "tail": 0.0},
                       "source": str(a.shots), "music": None, "scenes": scenes})
    print(f"SCENES: {a.out} ({len(scenes)} scenes, {sum(s['duration'] for s in scenes):.2f}s). Review vo_text and kinds before voicing.")


if __name__ == "__main__":
    main()
