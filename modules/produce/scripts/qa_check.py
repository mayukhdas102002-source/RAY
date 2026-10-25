#!/usr/bin/env python3
"""Technical QA on a rendered file. Measures; never assumes.

  python scripts/qa_check.py renders/final-9x16.mp4 --size 1080x1920 --fps 30 --duration 28 --lufs -14 --tp -1
  python scripts/qa_check.py renders/final.mp4 --timeline timeline.master.json --strips --sheet 12 --verify VERIFY.md

Checks: container/codecs, size, fps, duration (±1 frame), pixel format (yuv420p for social), +faststart,
audio present/48 kHz/stereo, integrated loudness and true peak, black frames, frozen video, long silences.
Visuals: --sheet N writes a contact sheet; --strips writes a 10-frame strip across every scene cut;
--at 1.5,7,12 writes single frames. Paths print as FRAME: <path> - open each with the Read tool and look.
Exit code 1 if any hard check fails.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import FFMPEG_HINT, ffprobe_json, need, read_json, run  # noqa: E402


def detect(path: str, vf: str | None, af: str | None, pattern: str) -> list[tuple[float, float]]:
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", path]
    if vf:
        cmd += ["-vf", vf, "-an"]
    if af:
        cmd += ["-af", af, "-vn"]
    cmd += ["-f", "null", "-"]
    r = run(cmd, capture=True, check=False)
    err = r.stderr or ""
    out = []
    if pattern == "black":
        for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", err):
            out.append((float(m.group(1)), float(m.group(2))))
    elif pattern == "freeze":
        starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", err)]
        ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", err)]
        out = list(zip(starts, ends + [float("nan")] * (len(starts) - len(ends))))
    elif pattern == "silence":
        starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
        ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
        out = list(zip(starts, ends + [float("nan")] * (len(starts) - len(ends))))
    elif pattern == "loud":
        m = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
        if m:
            d = json.loads(m[-1])
            return [(float(d["input_i"]), float(d["input_tp"]))]
    return out


def faststart(path: str) -> bool | None:
    try:
        with open(path, "rb") as f:
            head = f.read(1 << 20)
        moov, mdat = head.find(b"moov"), head.find(b"mdat")
        if moov == -1:
            return False
        return mdat == -1 or moov < mdat
    except OSError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--size", help="WxH expected")
    ap.add_argument("--fps", type=float)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--timeline", help="timeline.master.json: expected duration + cut points for --strips")
    ap.add_argument("--lufs", type=float, help="Target integrated LUFS (±1 LU tolerance)")
    ap.add_argument("--tp", type=float, help="Max true peak dBTP")
    ap.add_argument("--no-audio-ok", action="store_true")
    ap.add_argument("--sheet", type=int, default=0, help="Contact sheet with N frames")
    ap.add_argument("--strips", action="store_true", help="Frame strips across every scene cut (needs --timeline)")
    ap.add_argument("--at", help="Comma list of seconds to grab as single frames")
    ap.add_argument("--out-dir", help="Where to write frames (default: <video dir>/qa)")
    ap.add_argument("--verify", help="Append a section to this VERIFY.md")
    a = ap.parse_args()
    need("ffmpeg", FFMPEG_HINT)

    info = ffprobe_json(a.video)
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    au = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
    dur = float(info.get("format", {}).get("duration", 0))
    res: dict = {"file": a.video, "duration": round(dur, 3), "size_mb": round(int(info.get("format", {}).get("size", 0)) / 1e6, 2),
                 "checks": [], "warnings": []}

    def check(name: str, ok: bool, detail: str, hard: bool = True) -> None:
        res["checks"].append({"check": name, "ok": ok, "detail": detail, "hard": hard})

    if not v:
        check("video stream", False, "no video stream")
    else:
        fr = v.get("avg_frame_rate", "0/1")
        n, d = (fr.split("/") + ["1"])[:2]
        fps = float(n) / float(d) if float(d) else 0
        res.update({"codec": v.get("codec_name"), "width": v.get("width"), "height": v.get("height"), "fps": round(fps, 3),
                    "pix_fmt": v.get("pix_fmt")})
        if a.size:
            w, h = map(int, a.size.lower().split("x"))
            check("size", (v.get("width"), v.get("height")) == (w, h), f"{v.get('width')}x{v.get('height')} (want {a.size})")
        if a.fps:
            check("fps", abs(fps - a.fps) < 0.01, f"{fps:.3f} (want {a.fps})")
        check("pixel format", v.get("pix_fmt") in ("yuv420p", "yuvj420p", "yuva444p10le", "yuva420p", "yuv420p10le"),
              f"{v.get('pix_fmt')} (social platforms want yuv420p)", hard=False)
    want = a.duration
    if want is None and a.timeline:
        want = float(read_json(a.timeline)["total"])
    if want is not None:
        tol = 1.0 / (res.get("fps") or 30) + 0.05
        check("duration", abs(dur - want) <= tol, f"{dur:.3f}s (want {want:.3f}s ±{tol:.3f})")
    fs = faststart(a.video)
    if a.video.lower().endswith((".mp4", ".mov", ".m4v")):
        check("faststart (moov first)", bool(fs), "moov atom before mdat" if fs else "re-mux with -movflags +faststart", hard=False)

    if not au:
        check("audio stream", a.no_audio_ok, "no audio stream", hard=not a.no_audio_ok)
    else:
        res.update({"audio_codec": au.get("codec_name"), "sample_rate": au.get("sample_rate"), "channels": au.get("channels")})
        check("audio 48 kHz", au.get("sample_rate") == "48000", f"{au.get('sample_rate')} Hz", hard=False)
        check("audio stereo", au.get("channels") == 2, f"{au.get('channels')} ch (mono measures ~3 dB quieter)", hard=False)
        loud = detect(a.video, None, "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "loud")
        if loud:
            i, tp = loud[0]
            res.update({"integrated_lufs": i, "true_peak_dbtp": tp})
            if a.lufs is not None:
                check("loudness", abs(i - a.lufs) <= 1.0, f"{i:.1f} LUFS (want {a.lufs} ±1)")
            if a.tp is not None:
                check("true peak", tp <= a.tp + 0.1, f"{tp:.1f} dBTP (max {a.tp})")
        sil = [(s, e) for s, e in detect(a.video, None, "silencedetect=n=-50dB:d=1.5", "silence")]
        res["silences"] = sil
        if sil:
            res["warnings"].append(f"{len(sil)} silence(s) ≥1.5 s: " + ", ".join(f"{s:.1f}-{e:.1f}" for s, e in sil[:8]))

    if v:
        blacks = detect(a.video, "blackdetect=d=0.2:pix_th=0.04", None, "black")
        res["black"] = blacks
        bad_black = [(s, e) for s, e in blacks if not (e >= dur - 0.6)]  # a fade-to-black ending is fine; pix_th 0.04 so dark brand grounds don't count as black
        check("no black frames", not bad_black, ", ".join(f"{s:.2f}-{e:.2f}" for s, e in bad_black) or "none", hard=False)
        frz = detect(a.video, "freezedetect=n=0.002:d=1.5", None, "freeze")
        res["frozen"] = frz
        if frz:
            res["warnings"].append("frozen video ≥1.5 s at " + ", ".join(f"{s:.1f}s" for s, _ in frz[:8]) + " (fine for held cards; a bug on footage)")

    out_dir = Path(a.out_dir or Path(a.video).parent / "qa")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(a.video).stem
    frames = []
    if a.sheet and dur:
        n = a.sheet
        cols = 4 if (res.get("height", 1) or 1) <= (res.get("width", 1) or 1) else 6
        rows = (n + cols - 1) // cols
        sheet = out_dir / f"{stem}.sheet.jpg"  # frames read left-to-right, evenly spaced every dur/N seconds
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.video, "-vf",
             f"fps={n / dur:.6f},scale=480:-2,tile={cols}x{rows}",
             "-frames:v", "1", "-update", "1", str(sheet)], check=False)
        if sheet.exists():
            frames.append(str(sheet))
    if a.strips and a.timeline and dur:
        T = read_json(a.timeline)
        fps = res.get("fps") or T.get("fps", 30)
        for s in T["scenes"][1:]:
            cut = float(s["start"])
            n0 = max(0, int(round(cut * fps)) - 5)
            strip = out_dir / f"{stem}.cut-{s['id']}.jpg"
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.video, "-vf",
                 f"select='between(n\\,{n0}\\,{n0 + 9})',scale=320:-2,tile=10x1", "-frames:v", "1", "-update", "1", str(strip)], check=False)
            if strip.exists():
                frames.append(str(strip))
    if a.at:
        for t in [float(x) for x in a.at.split(",")]:
            f = out_dir / f"{stem}.t{t:06.2f}.png"
            run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", a.video, "-frames:v", "1", "-update", "1", str(f)], check=False)
            if f.exists():
                frames.append(str(f))
    res["frames"] = frames

    hard_fail = [c for c in res["checks"] if c["hard"] and not c["ok"]]
    res["verdict"] = "FAIL" if hard_fail else "PASS"
    (out_dir / f"{stem}.qa.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    for c in res["checks"]:
        print(f"[{'OK ' if c['ok'] else ('XX ' if c['hard'] else '!! ')}] {c['check']}: {c['detail']}")
    for w in res["warnings"]:
        print(f"[!! ] {w}")
    for f in frames:
        print(f"FRAME: {f}")
    print(f"VERDICT: {res['verdict']}  (details: {out_dir / (stem + '.qa.json')})")
    if a.verify:
        with open(a.verify, "a", encoding="utf-8") as fh:
            fh.write(f"\n## QA · {Path(a.video).name} · {res['verdict']}\n\n")
            for c in res["checks"]:
                fh.write(f"- {'✅' if c['ok'] else ('❌' if c['hard'] else '⚠️')} {c['check']}: {c['detail']}\n")
            for w in res["warnings"]:
                fh.write(f"- ⚠️ {w}\n")
            fh.write("- Visual review: frames listed in the qa folder were opened and checked: ☐ (tick after looking)\n")
    sys.exit(1 if hard_fail else 0)


if __name__ == "__main__":
    main()
