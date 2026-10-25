#!/usr/bin/env bash
# Duration, resolution, fps and audio presence of a video.
# Usage: ./probe.sh <video>
f="$1"; [ -f "$f" ] || { echo "usage: $0 <video>"; exit 1; }
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of default=nw=1 "$f"
