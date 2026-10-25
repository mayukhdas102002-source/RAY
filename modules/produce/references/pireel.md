# Pireel: finishing and variants editor

Pireel Studio (`pireel/pireel`, AGPL-3.0) is a browser multi-track editor built for humans and AI agents: timeline, canvas, captions, motion-graphic components, multiple outputs per project, in-browser export (WebCodecs; MP4/WebM/MOV up to 4K). It edits; it doesn't plan or generate (generation exists only on the hosted service, paid in credits).

## Two ways to use it

| | Local OSS editor | Hosted pireel.com (agent-driven) |
|---|---|---|
| Install | `git clone https://github.com/pireel/pireel.git && cd pireel && corepack enable && pnpm install && pnpm dev` | `claude plugin marketplace add pireel/pireel-agent && claude plugin install pireel@pireel-marketplace` then `claude mcp login plugin:pireel:pireel` (or `claude mcp add --transport http pireel https://pireel.com/api/studio/mcp`) |
| Who drives | The user, by hand | The agent via MCP tools; the editor tab must be open |
| Media | Local `.local-assets/` (100 MB cap per upload) | Uploaded to Pireel cloud (2 GB video/audio, 50 MB images) |
| Cost | Free | Free plan 20 credits/day; Pro/Max plans; commercial licence needs Pro+ (check current pricing) |
| Limits | No MCP server in the OSS repo; transcription/generation providers absent | Transcription, analysis, generation charge credits |

Use it for: talking-head clean-up by transcript, caption styling with presets, B-roll placement, per-platform outputs (`manage_project duplicate/switch_output`), last-mile human touch-ups. Import finished Remotion/HyperFrames renders and local VO as clips.

## Agent workflow (hosted)

1. `get_state` once; then update your model of the project from each mutation's delta. Never invent ids; clip/track ids are per output.
2. Two clocks: timeline **frames** vs source **seconds**; never multiply by fps yourself.
3. Open the editor for the user with `create_browser_handoff` in the in-app browser (single-use ticket ~60 s; don't print the URL).
4. Import local media: `import_media` → token + base_url → `node scripts/import-media.mjs --base <base_url> --token <token> /path/file.mp4` (uploads, transcribes, registers).
5. Edit with `add_clips` (roles primary/broll/narration/music/sfx), `split_clips`, `ripple_delete_ranges`, `remove_silence` (before transcript cuts), `remove_words`, `set_clip_properties` (volumeDb, fades, speed 0.5–2, source in/out), `set_clip_framing` (punch-in, split, corner), `add_transition` (one family per video), `set_captions` (presets `em-*`, `ln-*`), `compose_component` (free: your own HTML+JS block) / `apply_component`.
6. Prefer bring-your-own (free) over charged tools (`[…CHARGES…]` in descriptions: transcript, semantic inspection, generation, speech, lip-sync).
7. Export: `export {action:"start"}` then poll `status` every ~15 s; headless: `node scripts/export-sink.mjs --out <dir> &` and pass `sink_url`. One output at a time. Don't re-encode the export as the deliverable.
8. Errors: `studio_not_open` (409) → offline mode; `tab_timeout` → don't retry, foreground the tab, `get_state`, read `lateReceipts`; `401` → re-login; `402` → offer the bring-your-own route.

Mixing rules from its audio skill match this pipeline: no auto-ducking or looping; music −18 to −12 dB under speech with manual ducks (split + per-segment `volumeDb`); fade in 1–2 s, out 1.5–3 s; B-roll audio −20 to −30 dB under speech; cut by default.

## Brand in Pireel

`brand_tokens.py` writes `brand/tokens/pireel-frame.md` (a Studio **Frame**: palette front matter + directing prose). In a self-built shell, add it under `packages/studio-frames/content/<brand>/frame.md` and merge with `mergeFrameRegistries(..., {onConflict:'replace'})`. Studio Kit components (metric, kpi, chart, steps, callout, lowerThird, title, code) take theme tokens `--sk-fg`, `--sk-accent`, `--sk-panel`, `--sk-font-head`…: map them from `brand.css`.
