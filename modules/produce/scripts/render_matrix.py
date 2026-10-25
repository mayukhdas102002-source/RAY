#!/usr/bin/env python3
"""Render every deliverable from one variants file: aspects, languages, hooks, personalised rows.

  python scripts/render_matrix.py variants.json            # finals
  python scripts/render_matrix.py variants.json --draft    # fast, low-res drafts of every variant
  python scripts/render_matrix.py variants.json --only reels-en,yt-16x9

variants.json (see templates/project/variants.json):
{
  "defaults": {"engine": "remotion", "project": "remotion", "fps": 30, "muted": true,
               "mux_audio": "audio/master.wav", "qa": {"lufs": -14, "tp": -1}},
  "variants": [
    {"id": "yt-16x9",  "composition": "BrandFilm-16x9", "size": "1920x1080"},
    {"id": "reels-en", "composition": "BrandFilm-9x16", "size": "1080x1920", "props": {"showCaptions": true}},
    {"id": "hf-promo", "engine": "hyperframes", "project": "hyperframes", "size": "1920x1080",
     "variables": {"headline": "Spring rates"}, "quality": "delivery", "format": "mp4"}
  ]
}
Writes delivery/<id>.mp4 (or "out"), runs qa_check on each, and writes delivery/manifest.json with hashes.
Rendering is the step the user approves: run drafts first, show them, and run finals only on a clear go-ahead.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import die, eprint, media_duration, read_json, run, write_json  # noqa: E402

HERE = Path(__file__).resolve().parent


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("variants")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--out-dir", default=None, help="Default: delivery/ (finals) or renders/drafts/ (drafts)")
    ap.add_argument("--no-qa", action="store_true")
    ap.add_argument("--browser-executable", help="Remotion: use an existing Chrome/Chromium instead of downloading one")
    a = ap.parse_args()

    vp = Path(a.variants).resolve()
    proj = vp.parent
    V = read_json(vp)
    D = V.get("defaults", {})
    only = set(a.only.split(",")) if a.only else None
    out_dir = Path(a.out_dir) if a.out_dir else proj / ("renders/drafts" if a.draft else "delivery")
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"variants": []}

    for v in V["variants"]:
        if only and v["id"] not in only:
            continue
        c = {**D, **v}
        engine = c.get("engine", "remotion")
        pdir = (proj / c.get("project", engine)).resolve()
        out = (proj / c["out"]).resolve() if c.get("out") else (out_dir / f"{v['id']}.mp4").resolve()
        raw = (proj / "renders" / f"{out.stem}.raw.mp4").resolve() if c.get("mux_audio") else out
        raw.parent.mkdir(parents=True, exist_ok=True)
        eprint(f"\n=== {v['id']} ({engine}) -> {out}")
        if engine == "remotion":
            cmd = ["npx", "remotion", "render", c["composition"], str(raw)]
            props = dict(c.get("props", {}))
            if c.get("props_file"):
                props = {**read_json(proj / c["props_file"]), **props}
            if props:
                pf = pdir / f".bvp-props-{v['id']}.json"
                pf.write_text(json.dumps(props), encoding="utf-8")
                cmd.append(f"--props={pf}")
            if c.get("muted") and c.get("mux_audio"):
                cmd.append("--muted")
            if a.draft:
                cmd += ["--scale=0.5", "--crf=28"]
            elif c.get("crf"):
                cmd.append(f"--crf={c['crf']}")
            if c.get("codec"):
                cmd.append(f"--codec={c['codec']}")
            if a.browser_executable:
                cmd.append(f"--browser-executable={a.browser_executable}")
            run(cmd, cwd=str(pdir))
        elif engine == "hyperframes":
            cmd = ["npx", "hyperframes", "render", "-o", str(raw), "--format", c.get("format", "mp4"),
                   "--quality", "draft" if a.draft else c.get("quality", "delivery")]
            if c.get("fps"):
                cmd += ["--fps", str(c["fps"])]
            if c.get("variables"):
                vf = pdir / f".bvp-vars-{v['id']}.json"
                vf.write_text(json.dumps(c["variables"]), encoding="utf-8")
                cmd += ["--variables-file", str(vf)]
            if c.get("composition"):
                cmd += ["-c", c["composition"]]
            if c.get("workers"):
                cmd += ["--workers", str(c["workers"])]
            run(cmd, cwd=str(pdir))
        elif engine == "file":
            src = (proj / c["src"]).resolve()
            if not src.exists():
                die(f"{src} missing")
            raw = src
        else:
            die(f"Unknown engine {engine}")

        if c.get("mux_audio"):
            run([sys.executable, str(HERE / "audio.py"), "mux", str(raw), str(proj / c["mux_audio"]), "--out", str(out)])
        elif raw != out:
            out.write_bytes(Path(raw).read_bytes())
        if c.get("reframe"):
            tmp = out.with_name(out.stem + ".reframe.mp4")
            run([sys.executable, str(HERE / "reframe.py"), str(out), "--to", c["reframe"], "--mode", c.get("reframe_mode", "blur"), "--out", str(tmp)])
            tmp.replace(out)

        verdict = "skipped"
        if not a.no_qa:
            q = [sys.executable, str(HERE / "qa_check.py"), str(out), "--sheet", "12"]
            if c.get("size") and not a.draft:
                q += ["--size", c["size"]]
            if c.get("fps"):
                q += ["--fps", str(c["fps"])]
            qa = c.get("qa", {})
            if qa.get("lufs") is not None and not a.draft:
                q += ["--lufs", str(qa["lufs"])]
            if qa.get("tp") is not None and not a.draft:
                q += ["--tp", str(qa["tp"])]
            if (proj / "timeline.master.json").exists():
                q += ["--timeline", str(proj / "timeline.master.json")]
            r = subprocess.run(q)
            verdict = "PASS" if r.returncode == 0 else "FAIL"
        manifest["variants"].append({"id": v["id"], "file": str(out), "engine": engine, "sha256": sha(out),
                                     "duration": round(media_duration(str(out)), 3), "qa": verdict, "draft": a.draft})
        write_json(out_dir / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
