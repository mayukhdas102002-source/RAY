# Tools

Small ffmpeg helpers used for reference teardowns and boards. Requires `ffmpeg`/`ffprobe` and `python3`.

| Script | Does |
|---|---|
| `probe.sh <video>` | Duration, resolution, fps, audio streams |
| `cut_log.sh <video> [0.25]` | Scene cuts → shot count, average shot length, cut times |
| `contact_sheet.sh <video> [30] [out.jpg]` | Dense timestamped grid of frames (landscape 6 cols, portrait 8) |
| `keyframes.sh <video> t1 t2 …` | Save specific frames as JPGs for write-ups |
| `boards_from_edit.py <animatic> <shots.json> <out>` | One board image per shot from a rendered edit |

Windows: run inside WSL or Git Bash, or use the equivalent ffmpeg commands directly.
