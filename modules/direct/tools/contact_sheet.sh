#!/usr/bin/env bash
# Dense, timestamped contact sheet (default 30 frames) — enough to see every cut.
# Usage: ./contact_sheet.sh <video> [frames=30] [out.jpg]
f="$1"; n="${2:-30}"; out="${3:-${f%.*}_sheet.jpg}"; [ -f "$f" ] || { echo "usage: $0 <video> [frames] [out]"; exit 1; }
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$f"); H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$f")
if [ "$W" -gt "$H" ]; then cols=6; sw=320; else cols=8; sw=200; fi
rows=$(( (n + cols - 1) / cols ))
fps=$(python3 -c "print($n/$dur)")
ffmpeg -v error -y -i "$f" -vf "fps=$fps,scale=$sw:-2,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6,tile=${cols}x${rows}" -frames:v 1 "$out"
echo "$out"
