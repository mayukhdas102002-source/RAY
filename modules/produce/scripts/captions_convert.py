#!/usr/bin/env python3
"""Turn a word transcript into captions for any engine or platform.

  python scripts/captions_convert.py captions/words.master.json --to srt --out delivery/film.en.srt
  python scripts/captions_convert.py captions/words.master.json --to vtt --words 7
  python scripts/captions_convert.py captions/words.master.json --to remotion --out remotion/src/captions.json
  python scripts/captions_convert.py captions/words.master.json --to hyperframes --out hyperframes/transcript.json
  python scripts/captions_convert.py captions/words.master.json --to ass --brand brand/brand.json --vertical --out captions/film.ass
  python scripts/captions_convert.py captions/words.master.json --to groups   # JSON cue groups for hand-built HTML captions

Input: any transcript shape this skill reads (see _common.load_words).
Grouping rules (herk / OpenMontage house rules): vertical 1-3 words per cue, horizontal 6-8; break on
punctuation and on pauses > --gap; a cue ends ~0.2 s after its last word or when the next cue starts.
Burn an .ass file with: ffmpeg -i in.mp4 -vf "ass=film.ass" -c:a copy out.mp4
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import die, load_words, read_json, ts_srt, ts_vtt, write_json, write_text  # noqa: E402


def group(words: list[dict], max_words: int, max_chars: int, gap: float, max_dur: float, hold: float) -> list[dict]:
    cues, cur = [], []

    def flush() -> None:
        if cur:
            cues.append({"start": cur[0]["start"], "end": cur[-1]["end"], "words": list(cur),
                         "text": " ".join(w["text"] for w in cur)})
            cur.clear()

    for i, w in enumerate(words):
        if cur:
            prev = cur[-1]
            text_len = len(" ".join(x["text"] for x in cur + [w]))
            if (len(cur) >= max_words or text_len > max_chars or w["start"] - prev["end"] > gap
                    or w["end"] - cur[0]["start"] > max_dur or re.search(r"[.!?;:]$", prev["text"])):
                flush()
        cur.append(w)
        if re.search(r"[,—–]$", w["text"]) and len(cur) >= max(1, max_words // 2):
            flush()
    flush()
    for i, c in enumerate(cues):
        nxt = cues[i + 1]["start"] if i + 1 < len(cues) else None
        end = c["end"] + hold
        c["end"] = min(end, nxt) if nxt is not None else end
    return cues


def ass_color(hex_color: str, alpha: int = 0) -> str:
    h = hex_color.lstrip("#")[:6]
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def to_ass(cues: list[dict], brand: dict, vertical: bool, upper: bool) -> str:
    colors = brand.get("colors", {})
    font = brand.get("typography", {}).get("heading", {}).get("family", "Arial")
    W, H = (1080, 1920) if vertical else (1920, 1080)
    size = 64 if vertical else 54
    margin_v = 340 if vertical else 90
    cap = brand.get("captions", {})
    hl_role = cap.get("highlight", "accent")
    fg = ass_color(cap.get("text_color", "#FFFFFF"))
    hl = ass_color(colors.get(hl_role, hl_role if str(hl_role).startswith("#") else "#FFD400"))
    box = ass_color(colors.get("bg", "#000000"), alpha=0x30)  # ~80% opaque backing box
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,{font},{size},{hl},{fg},{box},{box},-1,0,0,0,100,100,0,0,3,14,0,2,90,90,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def t(x: float) -> str:
        cs = int(round(x * 100))
        h, cs = divmod(cs, 360000)
        m, cs = divmod(cs, 6000)
        s, cs = divmod(cs, 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    lines = []
    for c in cues:
        # \k karaoke: each word switches from SecondaryColour (text colour) to PrimaryColour (brand highlight) as it is spoken
        parts = []
        for i, w in enumerate(c["words"]):
            nxt = c["words"][i + 1]["start"] if i + 1 < len(c["words"]) else c["end"]
            k = max(1, int(round((nxt - w["start"]) * 100)))
            txt = w["text"].upper() if upper else w["text"]
            parts.append(f"{{\\k{k}}}{txt}")
        lines.append(f"Dialogue: 0,{t(max(0, c['start'] - 0.066))},{t(c['end'])},Brand,,0,0,0,,{' '.join(parts)}")
    return head + "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript")
    ap.add_argument("--to", required=True, choices=["srt", "vtt", "remotion", "hyperframes", "ass", "groups"])
    ap.add_argument("--out")
    ap.add_argument("--vertical", action="store_true", help="9:16 grouping (1-3 words)")
    ap.add_argument("--words", type=int, help="Max words per cue (default 3 vertical / 7 horizontal)")
    ap.add_argument("--chars", type=int, default=42, help="Max characters per cue")
    ap.add_argument("--gap", type=float, default=0.6, help="Pause that forces a new cue (s)")
    ap.add_argument("--max-dur", type=float, default=3.5)
    ap.add_argument("--hold", type=float, default=0.2, help="Seconds a cue stays after its last word")
    ap.add_argument("--offset", type=float, default=0.0, help="Shift everything by N seconds")
    ap.add_argument("--upper", action="store_true")
    ap.add_argument("--brand", help="brand.json (ASS colours/font)")
    a = ap.parse_args()

    T = load_words(a.transcript)
    words = [{"text": w["text"], "start": w["start"] + a.offset, "end": w["end"] + a.offset} for w in T["words"]]
    if not words:
        die("Transcript has no words")
    max_words = a.words or (3 if a.vertical else 7)
    cues = group(words, max_words, a.chars if not a.vertical else min(a.chars, 24), a.gap, a.max_dur, a.hold)
    stem = Path(a.transcript).with_suffix("")
    if a.to == "srt":
        body = "\n".join(f"{i}\n{ts_srt(c['start'])} --> {ts_srt(c['end'])}\n{c['text'].upper() if a.upper else c['text']}\n"
                         for i, c in enumerate(cues, 1))
        out = Path(a.out or f"{stem}.srt")
        write_text(out, body)
    elif a.to == "vtt":
        body = "WEBVTT\n\n" + "\n".join(f"{ts_vtt(c['start'])} --> {ts_vtt(c['end'])}\n{c['text'].upper() if a.upper else c['text']}\n" for c in cues)
        out = Path(a.out or f"{stem}.vtt")
        write_text(out, body)
    elif a.to == "remotion":
        caps = [{"text": " " + w["text"], "startMs": int(round(w["start"] * 1000)), "endMs": int(round(w["end"] * 1000)),
                 "timestampMs": int(round((w["start"] + w["end"]) * 500)), "confidence": None} for w in words]
        out = Path(a.out or f"{stem}.remotion.json")
        write_json(out, caps)
    elif a.to == "hyperframes":
        out = Path(a.out or f"{stem}.hyperframes.json")
        write_json(out, [{"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in words])
    elif a.to == "groups":
        out = Path(a.out or f"{stem}.groups.json")
        write_json(out, [{"id": f"cg{i}", "start": round(c["start"], 3), "end": round(c["end"], 3), "text": c["text"],
                          "words": c["words"]} for i, c in enumerate(cues)])
    else:
        brand = read_json(a.brand) if a.brand else {}
        out = Path(a.out or f"{stem}.ass")
        write_text(out, to_ass(cues, brand, a.vertical, a.upper or brand.get("captions", {}).get("upper", False)))
    print(f"CAPTIONS: {out}  ({len(cues)} cues from {len(words)} words)")


if __name__ == "__main__":
    main()
