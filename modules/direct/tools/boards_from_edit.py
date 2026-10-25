#!/usr/bin/env python3
"""Pull one board frame per shot from a rendered animatic, using shots.json timings.
Usage: python3 boards_from_edit.py <animatic.mp4> <shots.json> <out_dir> [position=0.7]"""
import json, subprocess, sys, os
vid, shots, out = sys.argv[1:4]; pos = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
os.makedirs(out, exist_ok=True)
for s in json.load(open(shots))["shots"]:
    t = s["t"][0] + (s["t"][1] - s["t"][0]) * pos
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", vid, "-frames:v", "1", "-q:v", "3", f"{out}/{s['id']}.jpg"], check=True)
    print(f"{out}/{s['id']}.jpg")
