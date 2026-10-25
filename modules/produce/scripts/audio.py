#!/usr/bin/env python3
"""Measure, mix, master and mux the soundtrack. FFmpeg only, no plugins.

  python scripts/audio.py measure renders/final.mp4                    # integrated LUFS, true peak, LRA
  python scripts/audio.py mix --timeline timeline.master.json --music audio/bed.wav --sfx audio/sfx.json \
                              --out audio/master.wav --lufs -14 --tp -1 --under-db 12
  python scripts/audio.py mix --voice edit/clean.wav --music audio/bed.wav --out audio/master.wav
  python scripts/audio.py normalize in.wav --out out.wav --lufs -16 --tp -1.5
  python scripts/audio.py mux renders/draft.mp4 audio/master.wav --out renders/final.mp4

mix: VO lines are placed at scene start + voDelay from timeline.master.json (or one --voice track),
the music bed sits `under-db` below the voice and is sidechain-ducked a further `duck-db` while
speech plays, SFX land at their times (events: [{"t": 3.2, "file": "audio/sfx/whoosh.wav", "gain_db": -6}]),
then a two-pass loudnorm hits the delivery target. Output: 48 kHz 24-bit stereo WAV.
Always re-measure the final encoded file, not the WAV: AAC encoding and mono/stereo change readings.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import FFMPEG_HINT, die, eprint, media_duration, need, read_json, run  # noqa: E402


def loudnorm_measure(inputs: list[str], graph: str | None, label: str | None, lufs: float, tp: float) -> dict:
    """Run a graph (or a single file) through loudnorm analysis and return its JSON."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    for i in inputs:
        cmd += ["-i", i]
    if graph:
        cmd += ["-filter_complex", f"{graph};[{label}]loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json[o]", "-map", "[o]"]
    else:
        cmd += ["-af", f"loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json"]
    cmd += ["-f", "null", "-"]
    r = run(cmd, capture=True, check=False)
    m = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr or "", re.S)
    if not m:
        die(f"loudnorm analysis failed:\n{(r.stderr or '')[-1500:]}")
    return json.loads(m[-1])


def cmd_measure(a) -> None:
    need("ffmpeg", FFMPEG_HINT)
    d = loudnorm_measure([a.file], None, None, -14, -1)
    out = {"file": a.file, "integrated_lufs": float(d["input_i"]), "true_peak_dbtp": float(d["input_tp"]),
           "lra": float(d["input_lra"]), "threshold": float(d["input_thresh"])}
    print(json.dumps(out, indent=2))


def build_graph(a, total: float) -> tuple[list[str], str, str]:
    inputs: list[str] = []
    parts: list[str] = []
    vo_labels: list[str] = []
    fmt = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"

    if a.timeline:
        T = read_json(a.timeline)
        for s in T["scenes"]:
            if not s.get("voFile"):
                continue
            idx = len(inputs)
            inputs.append(s["voFile"])
            delay = int(round((s["start"] + s.get("voDelay", 0)) * 1000))
            gain = s.get("voVolume", 1)
            parts.append(f"[{idx}:a]{fmt},volume={gain},adelay={delay}:all=1[v{idx}]")
            vo_labels.append(f"[v{idx}]")
    if a.voice:
        idx = len(inputs)
        inputs.append(a.voice)
        parts.append(f"[{idx}:a]{fmt}[v{idx}]")
        vo_labels.append(f"[v{idx}]")
    if not vo_labels and not a.music:
        die("Nothing to mix: give --timeline (with VO), --voice and/or --music")

    has_vo = bool(vo_labels)
    if has_vo:
        parts.append(f"{''.join(vo_labels)}amix=inputs={len(vo_labels)}:normalize=0:dropout_transition=0,apad=whole_dur={total:.3f},"
                     f"atrim=0:{total:.3f},asplit=2[vo][vosc]")
    mix_in = ["[vo]"] if has_vo else []

    if a.music:
        idx = len(inputs)
        inputs.append(a.music)
        # Static bed level: measured music loudness pushed to (voice loudness - under_db + duck_db): the sidechain then
        # pulls it down another duck_db while someone is talking, so the bed sits ~under_db below speech.
        bed_gain = 0.0
        if has_vo:
            vo_l = float(loudnorm_measure(inputs[:idx], ";".join(parts[:-1] + [parts[-1].replace(",asplit=2[vo][vosc]", "[vmeas]")]), "vmeas", -14, -1)["input_i"])
            mu_l = float(loudnorm_measure([a.music], None, None, -14, -1)["input_i"])
            if vo_l > -70 and mu_l > -70:
                bed_gain = (vo_l - a.under_db + a.duck_db) - mu_l
                eprint(f"voice {vo_l:.1f} LUFS, music {mu_l:.1f} LUFS -> bed gain {bed_gain:+.1f} dB")
        loop = "aloop=loop=-1:size=2147483647," if a.loop_music else ""
        fade_out_start = max(0.0, total - a.music_fade_out)
        parts.append(f"[{idx}:a]{fmt},{loop}atrim=0:{total:.3f},volume={bed_gain:.2f}dB,"
                     f"afade=t=in:d={a.music_fade_in},afade=t=out:st={fade_out_start:.3f}:d={a.music_fade_out}[mus]")
        if has_vo:
            # Approximate duck: speech sits far above the threshold, so ratio 4 pulls the bed down ~5-8 dB while talking.
            parts.append(f"[mus][vosc]sidechaincompress=threshold=0.015:ratio={a.duck_ratio}:attack=15:release=350:makeup=1[bed]")
            mix_in.append("[bed]")
        else:
            mix_in.append("[mus]")
    elif has_vo:
        parts.append("[vosc]anullsink")

    if a.sfx:
        events = read_json(a.sfx)
        base = Path(a.sfx).parent
        for e in events:
            f = Path(e["file"])
            f = f if f.is_absolute() or f.exists() else base / f
            idx = len(inputs)
            inputs.append(str(f))
            parts.append(f"[{idx}:a]{fmt},volume={e.get('gain_db', -6)}dB,adelay={int(round(e['t'] * 1000))}:all=1[s{idx}]")
            mix_in.append(f"[s{idx}]")

    parts.append(f"{''.join(mix_in)}amix=inputs={len(mix_in)}:normalize=0:dropout_transition=0,atrim=0:{total:.3f}[mix]")
    return inputs, ";".join(parts), "mix"


def cmd_mix(a) -> None:
    need("ffmpeg", FFMPEG_HINT)
    total = a.length
    if not total and a.timeline:
        total = float(read_json(a.timeline)["total"])
    if not total and a.voice:
        total = media_duration(a.voice)
    if not total:
        die("Give --length when there is no timeline or voice")
    inputs, graph, label = build_graph(a, total)
    eprint("pass 1: measuring the mix")
    m = loudnorm_measure(inputs, graph, label, a.lufs, a.tp)
    ln = (f"loudnorm=I={a.lufs}:TP={a.tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for i in inputs:
        cmd += ["-i", i]
    cmd += ["-filter_complex", f"{graph};[{label}]{ln},aresample=48000,alimiter=limit={10 ** (a.tp / 20):.4f}:level=disabled[o]",
            "-map", "[o]", "-ar", "48000", "-c:a", "pcm_s24le", a.out]
    eprint("pass 2: rendering master")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    run(cmd)
    d = loudnorm_measure([a.out], None, None, a.lufs, a.tp)
    print(json.dumps({"out": a.out, "duration": round(total, 3), "integrated_lufs": float(d["input_i"]),
                      "true_peak_dbtp": float(d["input_tp"]), "target": {"lufs": a.lufs, "tp": a.tp}}, indent=2))


def cmd_normalize(a) -> None:
    need("ffmpeg", FFMPEG_HINT)
    m = loudnorm_measure([a.file], None, None, a.lufs, a.tp)
    ln = (f"loudnorm=I={a.lufs}:TP={a.tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", a.file, "-af", f"{ln},aresample=48000", "-ar", "48000",
         "-c:a", "pcm_s24le", a.out])
    d = loudnorm_measure([a.out], None, None, a.lufs, a.tp)
    print(json.dumps({"out": a.out, "integrated_lufs": float(d["input_i"]), "true_peak_dbtp": float(d["input_tp"])}, indent=2))


def cmd_mux(a) -> None:
    need("ffmpeg", FFMPEG_HINT)
    out = a.out or str(Path(a.video).with_name(Path(a.video).stem + "-mixed.mp4"))
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", a.video, "-i", a.audio, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", a.bitrate, "-ar", "48000", "-shortest", "-movflags", "+faststart", out])
    d = loudnorm_measure([out], None, None, -14, -1)
    print(json.dumps({"out": out, "integrated_lufs": float(d["input_i"]), "true_peak_dbtp": float(d["input_tp"]),
                      "video_duration": round(media_duration(a.video), 3), "out_duration": round(media_duration(out), 3)}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("measure")
    p.add_argument("file")
    p.set_defaults(fn=cmd_measure)
    p = sub.add_parser("mix")
    p.add_argument("--timeline", help="timeline.master.json from timeline_from_vo.py")
    p.add_argument("--voice", help="A single, already-placed voice track (e.g. a cut talking head)")
    p.add_argument("--music")
    p.add_argument("--loop-music", action="store_true", help="Loop the bed if shorter than the film (prefer a long-enough edit)")
    p.add_argument("--sfx", help="events JSON: [{t, file, gain_db}]")
    p.add_argument("--out", required=True)
    p.add_argument("--length", type=float)
    p.add_argument("--lufs", type=float, default=-14.0)
    p.add_argument("--tp", type=float, default=-1.0)
    p.add_argument("--under-db", type=float, default=12.0, help="How far the bed sits under the voice while speaking")
    p.add_argument("--duck-db", type=float, default=5.0, help="Bed is set this much louder between lines; the sidechain takes it back down under speech")
    p.add_argument("--duck-ratio", type=float, default=4.0, help="Sidechain ratio (higher = deeper duck)")
    p.add_argument("--music-fade-in", type=float, default=1.5)
    p.add_argument("--music-fade-out", type=float, default=2.5)
    p.set_defaults(fn=cmd_mix)
    p = sub.add_parser("normalize")
    p.add_argument("file")
    p.add_argument("--out", required=True)
    p.add_argument("--lufs", type=float, default=-14.0)
    p.add_argument("--tp", type=float, default=-1.0)
    p.set_defaults(fn=cmd_normalize)
    p = sub.add_parser("mux")
    p.add_argument("video")
    p.add_argument("audio")
    p.add_argument("--out")
    p.add_argument("--bitrate", default="256k")
    p.set_defaults(fn=cmd_mux)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
