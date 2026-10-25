# RAY: an AI audio-video production pipeline

**One Claude skill that takes a brief to finished, QA-checked video and audio.** RAY acts as producer, writer, director, editor, sound designer and finishing house: it reads reference media, writes the concept and script, directs AI shots on Higgsfield, clones a brand voice locally, builds motion graphics in Remotion or HyperFrames, mixes and masters audio, captions, renders every aspect ratio and checks the result before delivery.

Built by [Mayukh Das](https://www.linkedin.com/in/mayukhdas02) while running growth and content for Homely NZ and Artisan Escape (New Zealand).

## Why I built it

Every AI ad used to mean juggling separate tools and prompts for scripting, shot direction, image and video generation, voice, captions, editing and audio mastering, then re-cutting each aspect ratio by hand. A one-minute AI social video or ad took **several days, sometimes weeks**.

I refined the workflow over **2 to 3 months of real client projects**, then spent **2 to 3 days** packaging it as RAY: one customisable tool anyone can use.

## Results

| | Before | With RAY |
| --- | --- | --- |
| One ~1-minute AI ad or social video | Several days to weeks | As little as **one day** |
| Aspect ratios | Re-cut by hand | 16:9, 9:16, 1:1 and 4:5 from one variants file |
| Quality checks | Eyeballed | Measured: loudness, resolution, frame rate, captions vs script |

## Used in production

- **Artisan Escape, "Fern Reveal" 30s ad**: delivered in 16:9 and 9:16
- **Artisan Escape, "The Deep Breath" and "Steamboat to Steam Bath"**: prompt packs, shot lists, storyboards, animatics, finals
- **Artisan Escape, "NZ Unfiltered" series**: keyframe-to-video workflows
- **Homely NZ, "The Asset"** fintech ad, plus a cinematic rework and a future reel

## How it works

**Understand → Plan → Make → Prove → Deliver.** RAY asks only what's missing, picks one of 13 playbooks and a mode (Quick, Standard, Full production or Advisory), makes the work through approval gates, measures it before claiming it's done, and hands over a delivery folder with a manifest.

| Layer | What it does |
| --- | --- |
| `core/` | Intake, production OS (project folders and gates), craft, quality bar, rights and safety |
| `playbooks/` | 13 content families: ads, brand films, social, explainers, product, people on camera, podcast and audio, events and organisations, motion, localisation, personalised at scale, narrative, industry notes |
| `modules/read` | Frames, transcripts, platform captions, comments, metadata and audio maps from any file or link |
| `modules/direct` | Concept, treatment, shot list, look lock, Higgsfield prompts and model choice, realism audit |
| `modules/produce` | Brand tokens, cloned voice, master clock from measured VO, Remotion/HyperFrames, captions, render matrix, QA |
| `modules/audio` | Measure, diagnose, mix and master to loudness targets; sound design; speech clean-up |
| `connectors/` | Higgsfield and other MCP tools, with fallbacks when they aren't connected |
| `scripts/ray.py` | One command line for 25 tools across the modules |

**Stack:** Claude Code (skill), Python 3.10+ (stdlib CLI), FFmpeg, Remotion, HyperFrames, faster-whisper, yt-dlp, Voicebox / VoiceStudio (local voice), Higgsfield via MCP.

---

## Using RAY

RAY is a Claude skill that runs audio and video production end to end for any person, brand or organisation. Ask for an ad, a reel series, a podcast edit, an explainer, a launch film, a training module, a fundraising appeal, a music video or a voiceover, and Ray takes it from the brief to finished, checked files.

It brings four production skills together under one brain:

| Module | Was | Does |
|---|---|---|
| `modules/read` | claude vidreader | Reads any video or link: frames, transcripts, captions, comments, metadata, audio maps |
| `modules/direct` | AI Video Buddy / AI Director | Directs films and AI shots: concepts, treatments, shot lists, Higgsfield prompts and model choice, realism checks |
| `modules/produce` | master-brand-video-pipeline | Makes everything: brand tokens, cloned voice, captions, Remotion/HyperFrames, OpenMontage, herk talking-head edits, Pireel, mix, renders, QA |
| `modules/audio` | master-ai-audio-director | Measures, diagnoses, mixes and masters audio; sound design; speech clean-up and transcription |

On top: `core/` (intake, production OS, craft, quality bar, rights and safety), `playbooks/` (13 content families with full workflows), `connectors/` (Higgsfield and other MCPs), `scripts/ray.py` (one command line for everything) and `templates/` (person and organisation brand kits, connector sheet).

## Folder map

```
RAY/
├── SKILL.md                 ← Ray's brain: how it works, modes, playbooks, tools, hard rules
├── core/                    intake · production-os · craft · quality-bar · rights-and-safety
├── playbooks/               INDEX + 01 ads … 12 narrative, 13 industry notes
├── connectors/              README (any MCP) · higgsfield · catalog (local MCP servers)
├── modules/
│   ├── read/                MODULE.md + scripts (info, captions, frames, transcribe, probe, audiomap, fetch)
│   ├── direct/              MODULE.md + director/ 01–11 + library/ (Higgsfield, visual skills) + templates + tools
│   ├── produce/             MODULE.md + references/ + scripts/ (14 tools) + templates (Remotion, HyperFrames, project)
│   └── audio/               MODULE.md + references/
├── scripts/ray.py           doctor · playbooks · tools · new · tool <name>
└── templates/               brand.person / brand.org examples · CONNECTORS.md
```

## Install

- **Cowork / claude.ai:** zip the `RAY` folder (with `SKILL.md` at the top level of the zip) and add it in Settings → Capabilities → Skills.
- **Claude Code:** copy the folder to `~/.claude/skills/ray/`.
- Then ask: "Ray, check my setup" (runs `python scripts/ray.py doctor`).

Optional tools (install what your content needs; `references/setup.md` in the Produce module has every step): Node 22+, FFmpeg 7+, Python 3.10+, yt-dlp, faster-whisper, Voicebox or VoiceStudio (local brand voice), OpenMontage / herk-edit-kit / Pireel (clones in `_toolchain/`). Connect MCPs such as Higgsfield in Settings → Connectors when you want Ray to generate on your accounts.

## Try

- "Ray, make three 30-second reels from this podcast episode for Instagram and TikTok."
- "Ray, we're a nonprofit: build a 90-second fundraising video from these interview clips."
- "Ray, write and direct a 30-second AI ad for our app and generate the shots on Higgsfield."
- "Ray, turn our website into a product launch video in 16:9 and 9:16."
- "Ray, clean up this voice note and master it for a podcast."
- "Ray, make 200 personalised welcome videos from this spreadsheet."

## Command line

```bash
python scripts/ray.py doctor --tools-dir "<workspace>/_toolchain"
python scripts/ray.py playbooks
python scripts/ray.py tools
python scripts/ray.py new "<workspace>/Acme - Spring Launch" --kind brand --playbook product --brand "<workspace>/_brands/acme"
python scripts/ray.py tool frames https://youtu.be/... --max 8
python scripts/ray.py tool render_matrix variants.json --draft
```

See `CREDITS.md` for the open-source projects and libraries Ray builds on.
