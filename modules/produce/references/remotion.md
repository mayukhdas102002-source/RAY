# Remotion: React compositions rendered frame by frame

Remotion renders React components in headless Chrome, one frame at a time, in parallel tabs, then encodes with a bundled FFmpeg. Version used here: **4.0.537**. Docs as Markdown: append `.md` to any remotion.dev/docs URL. Implement from current docs, not memory.

## The brand starter (`templates/remotion-brand`)

```
src/index.ts          registerRoot
src/Root.tsx          BrandFilm-16x9 / -9x16 / -1x1 / -4x5 + EndCard-* + Thumbnail-* stills
src/BrandFilm.tsx     scenes → <Sequence>, per-scene VO (voDelay), music bed with ducking, captions
src/scenes/Scenes.tsx title · statement · stat · list · quote · footage · image · lowerThird · endCard
src/scenes/EndCard.tsx official logo (or wordmark), tagline, CTA, legal line
src/Captions.tsx      phrase pages (break on punctuation, pauses, scene ends, 3/6 words), active word highlight
src/layout.ts         safe areas + type scale from frame size; frame-pure entrance/exit helpers
src/brand.ts          reads brand.json, loads font files
src/brand.json        ← brand_tokens.py
src/timeline.json     ← timeline_from_vo.py (seconds)
src/captions.json     ← timeline_from_vo.py / captions_convert.py --to remotion (Caption[], ms)
public/vo, public/audio, public/media, public/brand   ← copied by the scripts
scripts/render-all.mjs  every aspect (+ --draft, --no-captions)
```

Duration is never hardcoded: `calculateMetadata` sums the timeline. Passing `--props='{"timeline": {...}}'` renders a different cut from the same code (batch/personalised). `--props='{"showCaptions": false}'` gives a clean master for SRT delivery.

Change the look by editing scene components; change content by editing `scenes.json` and re-running the scripts. New scene kinds: add to `SceneKind`, render in `SceneView`, pass fields through `timeline_from_vo.py` (`PASS_THROUGH`).

## CLI

| Command | Use |
|---|---|
| `npx remotion studio [--port N] [--no-open]` | Studio at `http://localhost:3000/<CompId>`. Open it as soon as the project runs and keep it open. |
| `npx remotion compositions` | List ids, sizes, durations |
| `npx remotion render <CompId> <out.mp4> [--props=file.json] [--frames=0-90] [--scale=0.5] [--crf=N] [--codec=h264\|h265\|vp9\|prores\|gif\|aac\|wav] [--muted] [--concurrency=N] [--browser-executable=…]` | Render |
| `npx remotion render <CompId> out/frames --frames=0,45,90 --image-format=png --sequence` | Grab specific frames to look at |
| `npx remotion still <StillId> out.png [--frame=N]` | Stills (end card, thumbnail) |
| `npx remotion benchmark` | Find the best `--concurrency` |
| `npx remotion add <pkg>` / `upgrade` / `versions` | Keep every `@remotion/*` on one exact version |
| `npx remotion ffmpeg … / ffprobe …` | Bundled binaries (H.264/H.265/VP8/VP9/ProRes only) |
| `npx remotion gpu` | Chrome GPU info; `--gl=angle` for WebGL/three.js/effects |

Transparent overlays: `--image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444 out.mov`, or `--image-format=png --pixel-format=yuva420p --codec=vp9 out.webm`.

## Authoring rules (from Remotion's own agent skills)

- **Pure function of the frame.** Every render tab is independent. No state that depends on frame order, no `Math.random()` (use `random('seed')`), no CSS transitions/animations, no Tailwind `animate-*`/`transition-*`.
- Animate with `interpolate(frame, [a,b], [x,y], {extrapolateLeft:'clamp', extrapolateRight:'clamp'})` and `spring({frame, fps, config:{damping:200}})`. Write timing as `n * fps` from `useVideoConfig()`. Prefer CSS `translate`/`scale`/`rotate` properties.
- Keep `useCurrentFrame()` in the smallest component that needs it. Inside a `<Sequence>`, frames and `durationInFrames` are local.
- Layout: one focal point; safe area 80 px sides / 100 px top-bottom at 1080 wide; headline ≥ 84 px, support ≥ 44 px at 1080; no redundant elements.
- Media: `@remotion/media` `<Video>`/`<Audio>` (frame-accurate, `trimBefore`, `volume` as number or `(f)=>number`); `<Img>`; assets in `public/` via `staticFile()`. Cut with `trimBefore` rather than re-encoding; if FFmpeg trims, re-encode (`-c:v libx264`).
- Async work (fetch, fonts, Lottie JSON) goes through `delayRender`/`continueRender` or built-in loaders (`@remotion/fonts`, `@remotion/google-fonts/<Family>`).
- Sequencing: `<Sequence from durationInFrames>`, `<Series>`, `<TransitionSeries>` (`@remotion/transitions`: `fade()`, `slide()`, `wipe()`, `flip()`, `clockWipe()`; `linearTiming`/`springTiming`). **Transitions shorten the total**; overlays don't. Keep a shot's video and its captions under the same timing parent.
- Captions: `Caption = {text, startMs, endMs, timestampMs, confidence}` with a leading space in `text`. `parseSrt`/`serializeSrt` in `@remotion/captions`. Transcribe each source separately with timestamps relative to it.
- Voiceover: one file per scene in `public/vo/`; `calculateMetadata` sums durations. Never shorten sounds to fit; lengthen the scene.
- Parameters: optional zod `schema` (top level `z.object`, `zColor()` from `@remotion/zod-types`) makes props editable in Studio. `defaultProps` must be JSON-serialisable.
- 3D: `@remotion/three` `<ThreeCanvas>`, never R3F `useFrame()`; any `<Sequence>` inside needs `layout="none"`.
- Useful packages: `@remotion/transitions`, `@remotion/captions`, `@remotion/media-utils` (`visualizeAudio`, `getAudioDurationInSeconds`), `@remotion/lottie`, `@remotion/gif`, `@remotion/shapes`, `@remotion/paths`, `@remotion/noise`, `@remotion/motion-blur`, `@remotion/light-leaks`, `@remotion/layout-utils` (`fitText`, `measureText`), `@remotion/effects` (blur, glow, vignette, LUT, halftone…), `@remotion/gsap` (`useGsapTimeline`), `@remotion/player` (embed previews in a web page).
- **Don't render unless asked.** Studio first; render on "render/export/give me the MP4" or after draft approval.

## Rendering at scale

- Local: `render_matrix.py` (one row per variant) or `scripts/render-all.mjs`.
- Node API: `bundle()` → `selectComposition({serveUrl, id, inputProps})` → `renderMedia({composition, serveUrl, codec, outputLocation, inputProps})`.
- **Lambda** (fastest, hundreds of versions): `npx remotion add @remotion/lambda` → `lambda policies role/user/validate` → keys in `.env` (`REMOTION_AWS_ACCESS_KEY_ID/SECRET`) → `lambda functions deploy` → `lambda sites create src/index.ts --site-name=<brand>-film` → `lambda render <site> BrandFilm-9x16 --props=row.json`. Redeploy functions after upgrades, sites after code changes. Never paste secrets into chat.
- Cloud Run is alpha and not actively developed; Vercel Sandbox and `@remotion/web-renderer` (client-side) exist.
- **Licence:** Remotion 5 will require `licenseKey` on render APIs for automators; companies of 4+ need a Company License now.

## Porting to HyperFrames

HyperFrames' `/remotion-to-hyperframes` skill maps `<Composition>` → root `data-*` (duration = frames / fps), `<Sequence from>` → sub-composition host `data-start = from / fps`, `interpolate` → `gsap.fromTo(..., {ease:"none"})`, `spring` → `back.out(N)`, `Easing.bezier` → `CustomEase`. Blockers: `useState`/`useReducer`/`useEffect` with deps, async `calculateMetadata`, third-party UI libraries.
