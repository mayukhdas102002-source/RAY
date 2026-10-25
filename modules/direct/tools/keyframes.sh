#!/usr/bin/env bash
# Grab specific frames (e.g. open, product moment, wow, end card) as JPGs.
# Usage: ./keyframes.sh <video> <t1> [t2 ...]   → <video>_<t>.jpg
f="$1"; shift; [ -f "$f" ] || { echo "usage: $0 <video> t1 [t2 ...]"; exit 1; }
for t in "$@"; do o="${f%.*}_${t}s.jpg"; ffmpeg -v error -y -ss "$t" -i "$f" -frames:v 1 -vf scale=640:-2 -q:v 4 "$o"; echo "$o"; done
