# Interop: moving work between the tools

## File contracts

| Artifact | Shape | Producers → consumers |
|---|---|---|
| Word transcript | `{"text","duration","audio_duration_secs","words":[{"text","start","end"}]}` (seconds) | `transcribe_words.py`, herk Scribe, VoiceStudio verbose_json (normalised) → herk cutters, `timeline_from_vo.py`, `captions_convert.py` |
| HyperFrames transcript | `[{"text","start","end"}]` | `captions_convert.py --to hyperframes`, `hyperframes transcribe` → HF caption blocks, `hf_build.py` |
| Remotion captions | `Caption[]` `{text:" word", startMs, endMs, timestampMs, confidence, pageBreakAfter?}` | `timeline_from_vo.py`, `captions_convert.py --to remotion` → `@remotion/captions` |
| Scene list | `scenes.json` | you / `shots_to_scenes.py` (Direct module (AI Director)) → `voice.py`, `timeline_from_vo.py` |
| Master clock | `timeline.master.json` | `timeline_from_vo.py` → `audio.py mix`, `qa_check.py --strips`, `hf_build.py`, Remotion `src/timeline.json` |
| EDL | herk `*.silence-edl.json` / `*.mistakes-edl.json` (`keep_ranges`, `delete_ranges`, `source_duration`, `edited_duration`) | herk → review page, timing maps |
| Asset provenance | `assets/ledger.json` | `ledger.py` ← OpenMontage `asset_manifest`, herk `footage-ledger.json` |
| Brand | `brand.json` → tokens | `brand_tokens.py` → every engine |

Times are seconds everywhere except Remotion (frames = `Math.round(t * fps)`) and Remotion captions (ms).

## Compositing one engine's output over another's

Render overlays with alpha, composite with FFmpeg (or place as a clip in the other engine):
```bash
# HyperFrames overlay → WebM VP9 alpha (root, html, body backgrounds transparent)
npx hyperframes render --format webm -o overlay.webm
# Remotion overlay → ProRes 4444 or VP9 alpha
npx remotion render Overlay overlay.mov --image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444
# composite (decode VP9 with libvpx-vp9 to keep alpha)
ffmpeg -i base.mp4 -c:v libvpx-vp9 -i overlay.webm -filter_complex "[0:v][1:v]overlay=0:0:format=auto" -map 0:a? -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a copy out.mp4
```
Keep one render clock: same fps, same duration, same start. Composite in a single pass; don't concatenate separately encoded segments (lip-sync drifts ~1 frame).

## Remotion ↔ HyperFrames

- Remotion → HF: HeyGen's `/remotion-to-hyperframes` skill (lint the source first; blockers: `useState`, `useReducer`, `useEffect` with deps, async `calculateMetadata`, third-party UI). Mapping in `references/remotion.md`.
- HF → Remotion: no tool; rebuild scenes as components from the same `timeline.json` (that's why both starters read the same data).
- Using both in one project: pick one as the **master timeline** (where VO, captions and the end card live); the other renders alpha overlays or self-contained inserts.

## herk → Remotion

Take `edit/clean.mp4` + `*.mistakes-transcript.json`. Put the clean video in `remotion/public/media/`, a `footage` scene spanning the film, overlay scenes anchored at `Math.round(wordStart * fps) - lead` (beats 0.15–0.6 s before the anchor phrase). Captions from the retimed transcript (`captions_convert.py --to remotion`).

## OpenMontage ↔ this pipeline

- In: register this pipeline's VO in OpenMontage's `asset_manifest` (or install `templates/openmontage/local_voice_tts.py`); copy the brand playbook to `styles/`.
- Out: final render + `asset_manifest` → `ledger.py add`; re-mix with `audio.py` if loudness targets differ; `render_matrix.py` with `"engine": "file", "src": "<path>"` rows for QA and manifest.

## Direct module (AI Director) ↔ this pipeline

- `shots_to_scenes.py <shots.json> --out scenes.json --media-dir assets/video` (fixed shot durations; AI plates as `footage` scenes; text layer notes kept).
- The Direct module (AI Director)'s own Remotion starter (`../direct/templates/remotion-starter`, Remotion 4.0.350) can stay the edit if it's already built; add this pipeline's captions/mix/QA around it. Upgrade both projects to one Remotion version before sharing components (`npx remotion upgrade`).

## Pireel

Import any render or WAV as a clip (`import_media` + `scripts/import-media.mjs`); HyperFrames-style blocks (`data-start`, `window.__timelines`, scoped GSAP) port as BYO components through `compose_component`.

## Converting captions for platforms

YouTube/LinkedIn/Vimeo: SRT or VTT sidecar from `captions_convert.py`. Burned-in: engine captions or `ffmpeg -vf ass=…`. HF can also convert: `npx hyperframes transcribe transcript.json --to srt`.
