> **RAY module.** This folder is part of RAY (`../../SKILL.md`). Its `SKILL.md` is renamed `MODULE.md` so it doesn't register as a separate skill; install RAY, not this folder. Standalone install notes below are kept for reference.

# claude vidreader

A Claude skill that lets Claude **read, watch and transcribe video** — local
files or online links — by converting media into things a language model can
actually consume: frames it can see, transcripts it can read, metadata and
comments.

It merges two projects:

- [MaximRomanMd/video-reader](https://github.com/MaximRomanMd/video-reader) — the
  local-file skill: ffmpeg frame extraction, whisper transcription, ffprobe
  metadata, audio spectrograms.
- [s8zvp68zyn-ctrl/claude-video-reader](https://github.com/s8zvp68zyn-ctrl/claude-video-reader)
  — the online side: yt-dlp metadata and comments, platform captions before
  speech-to-text, cookie handling for login-walled sites, frames straight off a
  stream.

Both are MIT-licensed; this skill reuses and adapts their approach.

## Install

Copy the `claude vidreader` folder into your skills directory:

- Claude Code / Cowork (per-project): `.claude/skills/claude-vidreader/`
- Claude Code (personal): `~/.claude/skills/claude-vidreader/`

The folder must contain `SKILL.md` at its top level. Rename the folder to
`claude-vidreader` (no space) if your setup prefers slug-style names.

## Requirements

| Tool | Needed for | Install |
|---|---|---|
| Python 3.9+ | everything | — |
| ffmpeg / ffprobe | frames, metadata, audio, transcription | `winget install Gyan.FFmpeg` · `brew install ffmpeg` · `sudo apt install ffmpeg` |
| yt-dlp | any URL | `pip install -U yt-dlp` |
| faster-whisper *(optional)* | transcription when no captions exist | `pip install faster-whisper` |

## Scripts

| Script | Input | Does |
|---|---|---|
| `info.py` | URL | Title, uploader, views/likes, date, description, hashtags, captions available, top comments |
| `captions.py` | URL | Platform's own subtitles (manual or auto) as timestamped text — instant, no download |
| `fetch.py` | URL | Downloads the video or audio via yt-dlp |
| `probe.py` | file | Duration, codecs, resolution, bitrate, streams |
| `frames.py` | file or URL | Still frames (evenly spaced or on scene cuts), downscaled |
| `transcribe.py` | file or URL | Timestamped speech-to-text via faster-whisper / openai-whisper; writes `.txt` + `.srt` |
| `audiomap.py` | file | Spectrogram, waveform and loudest moments — for music and sound effects |

Everything writes to `<temp>/claude-vidreader/<name>/`.

## Cookies (Facebook, Instagram, Douyin)

YouTube and TikTok work with no setup. For the login-walled sites, export your
browser session once:

```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt \
    --skip-download "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

Then set one of:

| Variable | Purpose |
|---|---|
| `VIDREADER_COOKIES_FILE` | Path to `cookies.txt` (most reliable) |
| `VIDREADER_COOKIES_BROWSER` | Browser name to read cookies live, e.g. `chrome` |

Cookies are applied only to Facebook/Instagram/Douyin and never to
YouTube/TikTok, which break when they receive them. `cookies.txt` is a live
login session — keep it out of git and don't share it.

## Notes

- A platform that suddenly stops working is usually a stale yt-dlp: `pip install -U yt-dlp`.
- Frames cost model context — keep `--max` small (6–12) and let them stay downscaled.
- Only access content you're authorized to view; respect copyright and platform terms.
