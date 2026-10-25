#!/usr/bin/env python3
"""Reframe a finished video to another aspect ratio (fallback only).

  python scripts/reframe.py renders/film-16x9.mp4 --to 9x16 --mode blur --out renders/film-9x16-reframed.mp4
  python scripts/reframe.py footage/interview.mp4 --to 9x16 --mode crop --x 0.62 --out edit/interview-9x16.mp4
  python scripts/reframe.py renders/film-16x9.mp4 --to 1x1 --mode pad --color "#0A1216"

Prefer rendering each aspect natively from Remotion/HyperFrames (text and safe areas reflow).
Use this for footage plates, or when a composition can't be re-rendered. A centre crop of a
graphic film is not a vertical edit; check every frame for cut-off text.

Modes: crop (fill, choose focus with --x/--y 0..1), blur (fit + blurred cover background),
pad (fit + solid brand colour bars).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import FFMPEG_HINT, need, run  # noqa: E402

SIZES = {"16x9": (1920, 1080), "9x16": (1080, 1920), "1x1": (1080, 1080), "4x5": (1080, 1350), "4k": (3840, 2160)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--to", required=True, choices=list(SIZES))
    ap.add_argument("--mode", default="blur", choices=["crop", "blur", "pad"])
    ap.add_argument("--x", type=float, default=0.5, help="crop focus 0..1 (0 = left)")
    ap.add_argument("--y", type=float, default=0.5, help="crop focus 0..1 (0 = top)")
    ap.add_argument("--color", default="#000000", help="pad colour")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--out")
    a = ap.parse_args()
    need("ffmpeg", FFMPEG_HINT)
    W, H = SIZES[a.to]
    out = a.out or str(Path(a.video).with_name(f"{Path(a.video).stem}-{a.to}.mp4"))
    if a.mode == "crop":
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H}:(in_w-{W})*{a.x}:(in_h-{H})*{a.y},setsar=1")
        fc = None
    elif a.mode == "pad":
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={a.color.replace('#', '0x')},setsar=1")
        fc = None
    else:
        vf = None
        fc = (f"[0:v]split=2[bg][fg];"
              f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,eq=brightness=-0.08[b];"
              f"[fg]scale={W}:{H}:force_original_aspect_ratio=decrease[f];"
              f"[b][f]overlay=(W-w)/2:(H-h)/2,setsar=1[v]")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", a.video]
    if fc:
        cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "0:a?"]
    else:
        cmd += ["-vf", vf, "-map", "0:v:0", "-map", "0:a?"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", out]
    run(cmd)
    print(f"REFRAMED: {out} ({W}x{H}, {a.mode})")


if __name__ == "__main__":
    main()
