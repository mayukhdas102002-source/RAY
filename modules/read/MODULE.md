---
name: claude-vidreader
description: Read, watch, transcribe or summarize a video or audio — a local file (.mp4/.mov/.mkv/.webm/.avi/.mp3/.wav) or an online link (YouTube, TikTok, Instagram, Facebook, Douyin, Vimeo, X). Turns media Claude cannot open natively into things it can read - still frames it can see, a timestamped transcript, platform captions and comments, and technical metadata. Use whenever the user shares a video/clip/recording/screencast/podcast or a video URL and asks what's in it, what's said, what it looks like, or its format/duration/resolution.
---

# claude-vidreader

> Part of RAY (module: read). Paths below are relative to `modules/read/`. RAY's `SKILL.md` decides when this module runs.


Claude has no native video input. This skill bridges that gap by shelling out to
`ffmpeg`/`ffprobe`/`yt-dlp` (and optionally a whisper backend) to convert video
into artifacts Claude *can* read: **frames** (images), a **transcript** (text),
**captions and comments** (text), and **metadata** (text).

All scripts live in `scripts/` next to this file. Run them with `python`
(3.9+). They are stdlib-only; transcription is the one thing that needs a pip
package, and only when platform captions don't exist.

## Step 1 — Local file or URL?

That single fork decides everything. Never download a video you don't need.

| Input | Metadata | Speech | Visuals |
|---|---|---|---|
| **URL** | `info.py` (+`--comments N`) | `captions.py` → fall back to `transcribe.py` | `frames.py` (streams, no download) |
| **Local file** | `probe.py` | `transcribe.py` | `frames.py` |

Then map the request to the least work that answers it:

| The user wants… | Use | Needs |
|---|---|---|
| "what's this video / who posted it / how popular" | `info.py` | yt-dlp |
| "what do they say / transcribe / summarize the talk" | `captions.py`, else `transcribe.py` | yt-dlp; whisper only for fallback |
| "what does it look like / show me / find the part where…" | `frames.py` | ffmpeg |
| "how long / what resolution / what codec / is it corrupt" | `probe.py` | ffprobe |
| "what does it *sound* like / music / sfx" | `audiomap.py` | ffmpeg |
| "save it to my machine" | `fetch.py` | yt-dlp |

If the intent is vague ("tell me about this video"), start cheap: `info.py` for a
URL or `probe.py` for a file. Then decide — talking-head/lecture/podcast wants a
transcript; a silent or visual clip wants frames.

## Step 2 — Online videos

```bash
python scripts/info.py "<URL>"                  # title, uploader, views, description, hashtags
python scripts/info.py "<URL>" --comments 20    # + top comments (slower)
python scripts/captions.py "<URL>"              # platform captions - instant, free
python scripts/captions.py "<URL>" --lang any   # any language that exists
python scripts/frames.py "<URL>" --max 8        # frames straight off the stream
python scripts/fetch.py "<URL>" --audio-only    # only when captions.py found nothing
```

**Always try `captions.py` before transcribing.** YouTube and most platforms
already have manual or auto captions; speech-to-text on a 40-minute video when a
free transcript exists is pure waste. `captions.py` exits with code 2 when there
are none — that is the signal to fall back:

```bash
python scripts/fetch.py "<URL>" --audio-only    # prints FILE: <path>
python scripts/transcribe.py "<FILE>"
```
(`transcribe.py` also accepts a URL directly and will fetch the audio itself.)

## Step 3 — Local files

```bash
python scripts/probe.py "<input>"                        # duration, codecs, resolution
python scripts/frames.py "<input>"                       # ~12 evenly-spaced, 768px wide
python scripts/frames.py "<input>" --mode scene          # only on scene changes
python scripts/frames.py "<input>" --start 30 --end 90   # just a time window
python scripts/frames.py "<input>" --max 6 --width 512   # even cheaper
python scripts/transcribe.py "<input>" --model small     # more accurate, slower
python scripts/transcribe.py "<input>" --start 120 --end 300
python scripts/audiomap.py "<input>"                     # spectrogram + waveform + loud moments
```

`frames.py` prints one `FRAME: <path>` line per image and `audiomap.py` prints
`IMAGE: <path>`. **Read those paths with the Read tool** to actually see them,
then describe or answer. `transcribe.py` prints the transcript and saves
`.txt`/`.srt`.

## Step 4 — Locating a moment (visual + audio together)

To find "the part where X happens": get the transcript or captions first (the
timestamps point you at roughly-when), then pull frames from that window with
`--start/--end` to confirm visually. Far cheaper and more precise than scanning
the whole video frame by frame. For a non-speech event (a crash, a sting, a beat
drop), `audiomap.py` gives you the loud moments to aim at instead.

## Step 5 — Login-walled sites (Facebook, Instagram, Douyin)

YouTube and TikTok need no setup. The other three need the user's browser
session as a Netscape `cookies.txt`. The scripts stop with these instructions
when cookies are missing — relay them, don't improvise:

```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt \
    --skip-download "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```
Then set `VIDREADER_COOKIES_FILE=/absolute/path/to/cookies.txt` (or
`VIDREADER_COOKIES_BROWSER=chrome`). Cookies expire in days-to-weeks; when a
site suddenly stops working, re-export. Cookies are deliberately **never** sent
to YouTube/TikTok — YouTube rejects requests that carry them.

`cookies.txt` is a live login session: never print it, copy it, or commit it.

## Step 6 — Missing dependencies

If a script exits saying a binary is missing, it already printed the exact
install command for this OS. Relay that and stop — don't work around it.

- **ffmpeg/ffprobe** (frames, audio, transcription): `winget install Gyan.FFmpeg`
  (Windows), `brew install ffmpeg` (macOS), `sudo apt install ffmpeg` (Linux).
- **yt-dlp** (anything with a URL): `pip install -U yt-dlp`. A platform that
  "stopped working" is usually a stale yt-dlp — upgrade first.
- **transcription backend** (only when captions don't exist):
  `pip install faster-whisper` (recommended, no torch) or `pip install openai-whisper`.

## Guardrails

- **Protect your context.** Never extract dozens of frames "to be safe". Start
  with 6–12, Read them, and only pull more (or a specific window) if needed.
- **Prefer captions over transcription, and `--audio-only` over full download.**
- Long videos: transcription time scales with length. Warn before running a big
  model on something very long; suggest `--model base` or a trimmed window.
- Outputs land in a temp dir (`<tmp>/claude-vidreader/<name>/`). Mention where
  files landed if the user may want the `.srt` or the frames; no need to clean up.
- Only access content the user is authorized to view; respect copyright and
  platform terms. Scraping login-walled sites is against their ToS and fragile.
