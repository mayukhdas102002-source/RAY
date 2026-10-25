#!/usr/bin/env bash
# Scene-cut timestamps → shot count and average shot length.
# Usage: ./cut_log.sh <video> [threshold=0.25]   (lower = more sensitive)
f="$1"; th="${2:-0.25}"; [ -f "$f" ] || { echo "usage: $0 <video> [threshold]"; exit 1; }
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
cuts=$(ffmpeg -hide_banner -i "$f" -vf "select='gt(scene,$th)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*" | cut -d: -f2)
n=$(echo "$cuts" | grep -c .)
echo "duration: ${dur}s"; echo "cuts: $n  → shots: $((n+1))"
python3 -c "print(f'avg shot: {float($dur)/($n+1):.2f}s')"
echo "cut times: $(echo $cuts | tr '\n' ' ')"
