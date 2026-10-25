#!/usr/bin/env python3
"""Lock the master clock: scene timing from measured VO, then feed Remotion and/or HyperFrames.

  python scripts/timeline_from_vo.py scenes.json --vo vo/ --remotion remotion/ --hyperframes hyperframes/

Reads   scenes.json (scene order, copy, kind, min/fixed durations, music)
        vo/manifest.json (written by voice.py) and vo/<id>.words.json (written by transcribe_words.py), both optional
Writes  timeline.master.json        master clock: every scene's start/duration and VO start, in seconds
        captions/words.master.json  all VO words shifted onto the master clock (herk shape)
        timeline.md                 human-readable table for review
        remotion/src/timeline.json + remotion/src/captions.json, VO/music copied into remotion/public/   (--remotion)
        hyperframes/timeline.json + hyperframes/transcript.json, VO/music copied into hyperframes/assets/ (--hyperframes)

Scene duration = fixed `duration` if set, else max(min_duration, lead + VO + tail), snapped to whole frames.
Re-run after every VO change. Never hand-edit start times downstream; change the inputs and re-run.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import die, eprint, load_words, media_duration, read_json, write_json, write_text  # noqa: E402

PASS_THROUGH = ("kind", "kicker", "headline", "body", "stat", "items", "name", "role", "media", "mediaStart", "voVolume")


def snap(t: float, fps: int) -> float:
    return round(round(t * fps) / fps, 6)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes")
    ap.add_argument("--vo", help="VO folder with manifest.json (default: <scenes dir>/vo)")
    ap.add_argument("--lead", type=float, default=None, help="Seconds before VO starts in each scene (default scenes.pad.lead or 0.25)")
    ap.add_argument("--tail", type=float, default=None, help="Seconds after VO ends (default scenes.pad.tail or 0.45)")
    ap.add_argument("--min", type=float, default=2.5, help="Default minimum scene length")
    ap.add_argument("--remotion", help="Remotion project dir to feed")
    ap.add_argument("--hyperframes", help="HyperFrames project dir to feed")
    a = ap.parse_args()

    sp = Path(a.scenes)
    proj = sp.parent
    S = read_json(sp)
    fps = int(S.get("fps", 30))
    pad = S.get("pad", {})
    lead = a.lead if a.lead is not None else float(pad.get("lead", 0.25))
    tail = a.tail if a.tail is not None else float(pad.get("tail", 0.45))
    vo_dir = Path(a.vo) if a.vo else proj / "vo"
    manifest = read_json(vo_dir / "manifest.json") if (vo_dir / "manifest.json").exists() else {"scenes": {}}

    cursor = 0.0
    out_scenes, master_words, rows = [], [], []
    for s in S.get("scenes", []):
        sid = s["id"]
        m = manifest.get("scenes", {}).get(sid)
        vo_file = vo_dir / m["file"] if m else None
        if vo_file is not None and not vo_file.exists():
            die(f"{sid}: manifest lists {vo_file} but the file is missing")
        vo_len = float(m["duration"]) if m else 0.0
        if vo_file is not None and not m.get("duration"):
            vo_len = media_duration(str(vo_file))
        s_lead = float(s.get("lead", lead)) if vo_len else 0.0
        if s.get("duration"):
            dur = float(s["duration"])
            if vo_len and s_lead + vo_len > dur:
                eprint(f"WARNING {sid}: fixed duration {dur}s is shorter than lead+VO {s_lead + vo_len:.2f}s; VO will be cut. Raise duration or trim copy.")
        else:
            dur = max(float(s.get("min_duration", a.min)), s_lead + vo_len + float(s.get("tail", tail)) if vo_len else float(s.get("min_duration", a.min)))
        start = snap(cursor, fps)
        dur = snap(dur, fps)
        cursor = start + dur
        sc = {"id": sid, "start": start, "duration": dur}
        for k in PASS_THROUGH:
            if k in s:
                sc[k] = s[k]
        sc.setdefault("kind", "statement")
        if vo_file is not None:
            sc["voFile"] = str(vo_file)
            sc["voDelay"] = s_lead
            sc["voDuration"] = round(vo_len, 3)
            wf = vo_file.with_suffix(".words.json")
            if wf.exists():
                for w in load_words(str(wf))["words"]:
                    master_words.append({"text": w["text"], "start": round(start + s_lead + w["start"], 3),
                                         "end": round(start + s_lead + w["end"], 3), "scene": sid})
            else:
                eprint(f"note {sid}: no {wf.name}; run transcribe_words.py on the VO for word-timed captions")
        out_scenes.append(sc)
        rows.append(f"| {sid} | {sc['kind']} | {start:6.2f} | {dur:5.2f} | {vo_len:5.2f} | {(s.get('vo_text') or s.get('headline') or '')[:60]} |")

    total = snap(cursor, fps)
    music = S.get("music")
    master = {"title": S.get("title", ""), "fps": fps, "total": total, "lead": lead, "tail": tail,
              "scenes": [{k: v for k, v in sc.items()} for sc in out_scenes], "music": music}
    write_json(proj / "timeline.master.json", master)
    write_json(proj / "captions" / "words.master.json",
               {"text": " ".join(w["text"] for w in master_words), "duration": total, "audio_duration_secs": total, "words": master_words})
    write_text(proj / "timeline.md", "\n".join([
        f"# Timeline: {S.get('title', '')}", "", f"{len(out_scenes)} scenes · {total:.2f}s · {fps} fps · lead {lead}s / tail {tail}s", "",
        "| Scene | Kind | Start | Dur | VO | Copy |", "|---|---|---|---|---|---|", *rows, ""]))

    def feed(dest: Path, media_root: Path, rel_prefix: str) -> list[dict]:
        scenes = []
        for sc in out_scenes:
            d = {k: v for k, v in sc.items() if k != "voFile"}
            if sc.get("voFile"):
                src = Path(sc["voFile"])
                tgt = media_root / "vo" / src.name
                tgt.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, tgt)
                d["vo"] = f"{rel_prefix}vo/{src.name}"
            else:
                d["vo"] = None
            if sc.get("media"):
                msrc = (proj / sc["media"]) if not Path(sc["media"]).is_absolute() else Path(sc["media"])
                if msrc.exists():
                    mt = media_root / "media" / msrc.name
                    mt.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(msrc, mt)
                    d["media"] = f"{rel_prefix}media/{msrc.name}"
            scenes.append(d)
        mus = None
        if music and music.get("src"):
            msrc = proj / music["src"]
            if msrc.exists():
                mt = media_root / "audio" / msrc.name
                mt.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(msrc, mt)
                mus = {**music, "src": f"{rel_prefix}audio/{msrc.name}"}
            else:
                eprint(f"WARNING: music {msrc} not found; skipped")
        return scenes, mus  # type: ignore[return-value]

    if a.remotion:
        r = Path(a.remotion)
        if not (r / "src").is_dir():
            die(f"{r} is not a Remotion project (no src/)")
        scenes, mus = feed(r, r / "public", "")
        write_json(r / "src" / "timeline.json", {"title": S.get("title", ""), "fps": fps, "music": mus, "scenes": scenes})
        caps = []
        for i, w in enumerate(master_words):
            c = {"text": " " + w["text"], "startMs": int(round(w["start"] * 1000)), "endMs": int(round(w["end"] * 1000)),
                 "timestampMs": int(round((w["start"] + w["end"]) * 500)), "confidence": None}
            if i + 1 == len(master_words) or master_words[i + 1]["scene"] != w["scene"]:
                c["pageBreakAfter"] = True  # never let a caption page straddle a scene cut
            caps.append(c)
        write_json(r / "src" / "captions.json", caps)
        print(f"REMOTION: {r / 'src' / 'timeline.json'} ({len(scenes)} scenes, {total:.2f}s) + captions.json ({len(caps)} words)")

    if a.hyperframes:
        h = Path(a.hyperframes)
        h.mkdir(parents=True, exist_ok=True)
        scenes, mus = feed(h, h / "assets", "assets/")
        write_json(h / "timeline.json", {"title": S.get("title", ""), "fps": fps, "total": total, "music": mus, "scenes": scenes})
        write_json(h / "transcript.json", [{"text": w["text"], "start": w["start"], "end": w["end"]} for w in master_words])
        print(f"HYPERFRAMES: {h / 'timeline.json'} + transcript.json. Set root data-duration=\"{total}\" and each scene host's "
              f"data-start/data-duration from timeline.json (seconds); <audio id=...> per VO with data-start = scene start + voDelay.")

    print(f"MASTER: {proj / 'timeline.master.json'} · {total:.2f}s · see timeline.md")


if __name__ == "__main__":
    main()
