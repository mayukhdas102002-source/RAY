# HyperFrames: HTML + GSAP compositions rendered to video

HeyGen's framework: plain HTML/CSS plus a seekable animation timeline, captured by headless Chrome and encoded by FFmpeg. No build step. Apache-2.0. Version used here: **0.8.178** (pre-1.0; trust `npx hyperframes <cmd> --help` over this file when they differ). Node 22+, system FFmpeg.

## Two modes

- **Templated:** `timeline_from_vo.py --hyperframes hyperframes/` then `hf_build.py hyperframes/ --size 1920x1080`, and for other aspects `hf_build.py hyperframes/ --size 1080x1920 --into hyperframes-9x16/` (HyperFrames allows exactly **one root `index.html` per project**, so each aspect is its own project folder). Generates `index.html` (root, audio, hosts) + `compositions/scene-*.html` + `compositions/captions.html`, vendors GSAP to `assets/vendor/`. Passes `npx hyperframes lint` with 0 errors. Good for fast, on-brand baselines and many aspects.
- **Atelier:** hand-author for hero/launch work. Read `frame.md` + `brand.css`, plan a storyboard, search the catalog, write each scene as a sub-composition. Keep the generated file only as a timing reference.

## Composition contract

Standalone `index.html` (no `<template>`):
```html
<div id="root" data-composition-id="main" data-start="0" data-width="1920" data-height="1080" data-duration="24.6">
  <div id="scene-S01" data-composition-id="scene-S01" data-composition-src="compositions/scene-S01.html"
       data-start="0" data-duration="4.9" data-width="1920" data-height="1080" data-track-index="1"></div>
  <audio id="vo-S01" src="assets/vo/S01.wav" data-start="0.25" data-duration="4.15" data-track-index="30"></audio>
</div>
<script src="assets/vendor/gsap.min.js"></script>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.to({}, { duration: 24.6 }, 0);
  window.__timelines["main"] = tl;   // key == data-composition-id
</script>
```
Sub-composition file: **everything inside `<template>`**; host id = inner root id = `__timelines` key; prefix ids with the composition id; style the root by `#id`; child timelines nest automatically; a sub-composition cannot animate host elements.

Attributes:
- Root: `data-composition-id`, `data-width`, `data-height` required; `data-duration` in **seconds**, read once at compile (variables can't change it); `data-fps` optional.
- Clips: `data-start` (seconds) makes an element timed; `data-duration` required on divs and hosts (img defaults 3 s, media = source length); `data-track-index` is a Studio lane only (stacking = CSS `z-index`); clips on one track must not overlap.
- Visible timed divs get `class="clip"`; **never** on `<video>`/`<audio>`. Every `<audio>` needs an `id` (else silent render). Timed `<video>` is `muted playsinline` (or `data-has-audio="true"`), never inside a timed plain element; animate a wrapper.
- Media extras: `data-media-start`, `data-volume` (0–3.98), `data-playback-rate`, `data-automation` (volume/rate lanes for fades and ducking).
- Visibility window is `[start, start+duration)`: finish animations slightly early.
- Captions host: add `data-track-kind="captions"`.

Variables (batch/personalisation): declare on `<html data-composition-variables='[{"id":"headline","type":"string","label":"Headline","default":"…"}]'>`; bind with `data-var-text="headline"`, `data-var-src`, or `var(--headline)`; supply with `--variables '{"headline":"…"}'`, `--variables-file`, or `--batch rows.json --output "renders/{index}-{city}.mp4"`.

## Animation rules

- GSAP for 95% of work: exactly **one paused timeline per composition**, built and registered synchronously (building inside `document.fonts.ready` is fine; register after building). Lottie → `window.__hfLottie`; Three.js → `hf-seek` event + set root `data-duration`; also CSS keyframes, WAAPI, Anime.js, custom `FrameAdapter`.
- Every scene has an entrance (`gsap.fromTo`, not `from`). **No exit animations except the final scene**: the transition is the exit. Before writing a transition read the catalog; shader transitions come from `@hyperframes/shader-transitions` / registry blocks.
- Never tween `visibility`/`display`/`autoAlpha` on a `.clip`; animate a child. Don't set a CSS `transform` and tween the same property (use `xPercent`/`yPercent` for centring). Spatial motion with x/y/scale/rotation only; precompute positions.
- `repeat:-1` only with a finite root duration; otherwise `Math.max(0, Math.floor(dur/cycle) - 1)`.
- Deterministic: no `Date.now`, `performance.now`, unseeded random, render-time fetch, hover/scroll state.
- Fonts: a named family needs `@font-face` (brand.css provides it) unless it's in HF's auto-resolved list (Inter, Poppins, Montserrat, Outfit, Roboto, Open Sans, Lato, Oswald, Bebas Neue, Playfair Display, IBM Plex Mono, JetBrains Mono, Space Mono, EB Garamond, Segoe UI, Arial, Helvetica, Georgia…).
- No `<br>` in body text; transformed elements block-level and sized; no `crossorigin` on media.
- Lint errors switch off layout/contrast audits: "0 samples" from `check` is not a pass.

## CLI (most commands take `--json`)

| Command | Use |
|---|---|
| `init <dir> [--example blank\|kinetic-type\|product-promo\|…] [--resolution landscape\|portrait\|square\|*-4k] [--video f.mp4\|--audio f.mp3] [--tailwind] [--non-interactive]` | New project (don't use inside OpenMontage pipelines) |
| `catalog --query "<effect>" [--type block\|component] --json` | Search ~400 registry items; **search before hand-writing any named effect** |
| `add <name>` | Install a block (→ `compositions/<name>.html`) or component (→ `compositions/components/`, merge by hand, scope its CSS) |
| `capture <url> -o captures/<name>` | Website → screenshots, assets, text, tokens. Blocked capture = stop. |
| `lint [--verbose]` → `check [--snapshots] [--strict]` | Iteration lint; `check` is the final gate (lint + runtime + layout + motion + WCAG contrast) |
| `snapshot --at 1.5,7,12` / `--composition <id> --frames N` | Stills to look at |
| `timeline --json`, `compositions`, `info`, `keyframes`, `beats`, `audio`, `normalize-audio` | Inspection and audio helpers |
| `preview [--background] [--port 3002]` | Studio at `http://localhost:3002/#project/<name>`; give the user the link, wait for approval |
| `render -o out.mp4 [--quality draft\|looks\|delivery] [--format mp4\|webm\|mov\|gif\|png-sequence\|hls] [--fps N] [--workers N] [--variables…] [--batch rows.json] [--strict] [--docker] [--gpu]` | Render. Draft while iterating, delivery for finals. `webm`/`mov` keep alpha (mov = ProRes 4444). |
| `transcribe <media\|.srt\|.vtt\|.json> [--model small.en\|medium.en\|large-v3] [--language xx] [--to srt\|vtt] [--dir d]` | Word-level `transcript.json` (whisper.cpp/Parakeet); `.en` models only for English |
| `tts "text"\|script.txt --voice af_heart\|bf_emma… --speed 1 -o vo.wav` / `tts --list` | Local Kokoro-82M (54 voices); fallback when no brand clone |
| `remove-background <in>` | u2net, transparent output |
| `figma asset\|tokens\|component` | Needs `FIGMA_TOKEN` |
| `doctor`, `browser ensure`, `benchmark`, `clean`, `upgrade --check` | Tooling |
| `lambda deploy\|sites create\|render\|render-batch\|progress\|destroy`, `cloudrun …`, `cloud render` (HeyGen-hosted) | Scale-out |

Long renders from an agent shell: `bash -c 'set -m; HYPERFRAMES_RENDER_DETACHED=1 npx hyperframes render -o out.mp4 </dev/null >render.log 2>&1 &'`. Use `--workers 1` when compositions contain `<video>` (parallel workers can paint video black) or more than ~5 background videos. Point at an existing Chrome with `HYPERFRAMES_BROWSER_PATH`.

## HeyGen's workflow skills (install with `npx hyperframes skills update <name>`)

Router `/hyperframes` resolves project state then routes to one of: `/remotion-to-hyperframes`, `/slideshow`, `/embedded-captions` (35 styles; captions composited behind the subject), `/talking-head-recut`, `/music-to-video`, `/motion-graphics` (unnarrated, <~10 s), `/pr-to-video`, `/product-launch-video` (any URL), `/faceless-explainer`, `/general-video`. Domain skills: `hyperframes-core`, `-animation`, `-keyframes`, `-creative` (frame.md, palettes, typography, storyboard), `media-use` (BGM/SFX/images/icons/voice sourcing with a ledger), `hyperframes-audio` (effect chains, `<hf-audio-group>` buses), `-cli`, `-registry`. Narrative workflows are best at 30–90 s, up to ~3 min.

Their dev loop matches this skill's gates: init/capture → media → catalog → author (use `timeline --json`) → lint → `check` → snapshots → preview + **wait for approval** → draft → looks → delivery → verify (`test -s`, ffprobe duration = `data-duration`, frames). Never render merely because checks pass.

## Media hygiene (from OpenMontage's HyperFrames notes)

- Free stock is often 640×360: pre-scale to cover (`scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,unsharp=3:3:0.6`).
- Re-encode footage with dense keyframes before use: `-c:v libx264 -r 30 -g 30 -keyint_min 30 -sc_threshold 0 -movflags +faststart` (avoids parallel timeouts and frozen frames).
- HEVC/ProRes sources get browser proxies for preview automatically; the original renders.
- HyperFrames re-encodes audio slightly quieter: mux the measured master afterwards (`audio.py mux`).
