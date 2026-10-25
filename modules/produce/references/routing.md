# Routing: intake, references, story, and a recipe per deliverable

## Intake (one message; skip what's known)

1. What is it for, who sees it, where (platforms/placements), and what should they do after?
2. The one promise, and up to two proofs. Which claims are approved, with sources?
3. Lengths and aspects (16:9, 9:16, 4:5, 1:1); sound-off viewing likely?
4. What exists: brand kit, logo files, fonts, footage, screen recordings, photos, reference videos, a voice (consented) or a narrator.
5. Voice: none / brand clone / real VO / talking head. Music: user library / licensed / generated / none.
6. Budget for paid generation and the per-call approval threshold. Deadline.

Write answers into `BRIEF.md`, propose a route from the table below, and stop for Gate 1.

## References

| Input | Tool | Output |
|---|---|---|
| Video URL (YouTube, TikTok, IG…) | Read module (vidreader): `info.py`, `captions.py`, `frames.py --mode scene` | transcript, frames, metadata |
| Local reference file | vidreader `frames.py`, `audiomap.py`; herk `analyze-reference.mjs <video> <out> --fps 6 --bpm <bpm>` (cuts, luminance, onsets vs beat) | cut log, rhythm, contact sheets |
| "Make something like this" (agentic) | OpenMontage `skills/meta/video-reference-analyst.md` (`video_analyzer`, `scene_detect`, `frame_sampler`) → 2–3 differentiated concepts | concepts grounded in the reference |
| A website / product page | `npx hyperframes capture <url> -o captures/<name>` (screenshots, assets, text, design tokens) | material for site-to-video; a blocked capture is a hard stop |
| Ad teardown for AI films | Direct module `../direct/director/02-reference-teardown.md` | shot log, the one wow, lessons |

Write `refs/REFERENCE-ANALYSIS.md`: timestamped observations, inferred principles, what we borrow (mechanisms, pacing, structure) and what we never copy (branded copy, characters, music, logos). Don't claim to have heard audio you only saw as a waveform.

## Story

- **Concepts:** pitch 3 (title, one-line logline, the image, how the product lands, why it wins). Recommend one.
- **Hook in 3 s:** the first gate for social is "in the first 3 seconds, is someone convinced to watch to the end?" Draft three openings from the same true material (problem-first, result-glimpse, recognition-first); compare them sound-off.
- **Shape:** hook → open loop → escalation/proof → payoff → CTA. Close the loop before the CTA. One main loop, at most one secondary.
- **Tempo:** brand VO reads at ~2.4–2.8 words/s (≈70 words per 30 s). Scenes 2.5–4 s; hero moments 4–8 s; charts ≥4 s; nothing shorter than 1 s except deliberate flurries.
- **On-screen words:** ~20 per section; a card must read in under a second. If nobody says it, consider not drawing it.
- **Every scene gets a job:** orientation, comprehension, belief, recall, feeling or action. Reject: card soup, wallpaper B-roll, timer editing, subtitle soup, unsupported proof, the speaker disappearing, theme drift.

## Recipes

Each recipe assumes Stage 0–2 are done (doctor green for its tools, brief approved, brand tokens generated).

### A. Narrated brand film / promo (the default)
1. `SCRIPT.md` → `scenes.json` (kinds: title, statement, stat, list, quote, footage, image, lowerThird, endCard).
2. `voice.py clone` (once per brand) → sample one line → `voice.py generate --scenes scenes.json --brand brand/brand.json`.
3. `transcribe_words.py vo/ --script scenes.json`.
4. Music into `assets/music/`, SFX into `assets/sfx/` + `audio/sfx.json`; `ledger.py add` each.
5. `timeline_from_vo.py scenes.json --remotion remotion --hyperframes hyperframes`.
6. Remotion: `npm install && npx remotion studio`, adapt `src/scenes/` for the look; or HyperFrames: `hf_build.py hyperframes --size …` then refine. Preview → Gate 5.
7. `audio.py mix …` → `render_matrix.py variants.json --draft` → Gate 6 → finals → `VERIFY.md`.

### B. Site-to-video / product launch
1. `npx hyperframes capture <url> -o captures/site` (respect `BLOCKED.md`).
2. Install HF workflow skill: `npx hyperframes skills update product-launch-video` (or herk's `website-to-hyperframes`: capture → DESIGN.md → SCRIPT.md → STORYBOARD.md → VO → build → validate).
3. Replace the captured design with this brand's `frame.md`/`brand.css` where they differ (brand.json wins).
4. VO from Voicebox/VoiceStudio instead of Kokoro for brand voice; transcribe; set each beat from first-word start to last-word end + 0.3–0.5 s.
5. `npx hyperframes lint` → `check` → `preview` → approval → `render --quality draft` → `delivery`.

### C. Explainer (faceless, data, teacher)
- **OpenMontage** (`references/openmontage.md`): pipeline `animated-explainer`, style playbook = brand YAML, TTS = your local VO (register WAVs in `asset_manifest` or add a Voicebox `BaseTool`). Follow its stage directors and gates.
- **Lighter:** HF `/faceless-explainer` workflow, or Remotion starter with stat/list scenes + charts (`@remotion/*` or HF `data-chart` block).

### D. Talking head (founder, testimonial, internal comms)
1. `raw/` holds the untouched take. herk chain (`references/herk-edit-kit.md`): transcribe → `cut-silences` → `find-cut-candidates` → **user reviews** → `apply-cuts` → `edit/clean.mp4` + `*.mistakes-transcript.json` (copy to `<hf project>/assets/transcript.json`).
2. Plan beats on the clean transcript (`video-storytelling`, `hyperframes-video-beats`): lower-thirds and full-screen takeovers anchored to phrases; validator `validate-beat-sync.mjs`.
3. Overlays: HyperFrames cards (native in herk) or Remotion (frames = round(t × fps)).
4. Captions from the retimed transcript; mix voice normalised + bed 9–14 dB under; master.
5. Never speed up the voice; cut between phrases, never inside one; consent for any testimonial.

### E. Short-form (Reels/Shorts/TikTok) from long footage
- herk `short-form-edit` (1080×1920; phone-safe text x 90–930, y 200–1600; 3 opening drafts; open loops; asset shortlist; footage ledger; validators `validate:short-form`, `validate:footage`), **or** OpenMontage `clip-factory` / `podcast-repurpose` for many clips.
- Captions 1–3 words per chunk, hard swap 2 frames before the word, dark box, never over the mouth. Master −14 LUFS / ≤ −1 dBTP on the final stereo encode.

### F. AI ad film / hyper-real brand story
1. Direct module (AI Director) stages 0–9 (concept, treatment, look lock, keyframes, motion prompts, model allocation, realism audit). Generation on Higgsfield is the user's step unless a connected tool can run it.
2. Bring plates into `assets/video/<shot>.mp4`, log them (`ledger.py add --source generated`).
3. `shots_to_scenes.py <shots.json> --out scenes.json` → all text/UI/end card through Remotion (Direct module (AI Director)'s starter or this template) → VO/mix/captions/versions here.

### G. Motion piece: logo sting, showreel, title sequence (no VO, ≤30 s)
- Cut to music: herk `motion-showreel` (`music-grid.mjs` for BPM/phase from the kick band, `splice-music.mjs`, `beatgrid.mjs` chapters, `mix.mjs`), cuts within 2 frames of the beat.
- Or HF `/motion-graphics` + `npx hyperframes catalog --query "logo reveal"` → `add logo-sting`.
- `scenes.json` with fixed `duration` per scene (no VO), `timeline_from_vo.py` still locks the clock.

### H. Batch / personalised / data-driven
- Remotion: one composition, `--props` per row (`render_matrix.py` rows with `props`), or Lambda (`references/remotion.md`). Duration from `calculateMetadata`.
- HyperFrames: declare `data-composition-variables`, bind with `data-var-text`/`var(--id)`; `npx hyperframes render --batch rows.json --output "renders/{index}-{city}.mp4"`; Lambda `render-batch` (JSONL).
- Never let a row change copy length past the layout: test the longest row first.

### I. Localisation
- VoiceStudio dubbing (`/dub/upload` → transcribe → translate → generate → QC → SRT/VTT/ASS + stems) or OpenMontage `localization-dub`.
- Or re-voice the translated script with `voice.py generate --language <code>` (cross-language cloning: keep the reference transcript in its own language), re-run `transcribe_words.py`, `timeline_from_vo.py`, re-render. Native-speaker check before delivery.

### J. Screen demo
- OpenMontage `screen-demo` (`real_capture` or `synthetic_terminal`). Real recordings beat mocks; zoom in, keep the cursor visible; label any mock as an example.

### K. Avatar / spokesperson
- OpenMontage `avatar-spokesperson` (HeyGen, Kling avatar, SadTalker/MuseTalk, Wav2Lip). Written consent from the person whose likeness/voice is used; disclose.

### L. Podcast / audiogram
- OpenMontage `podcast-repurpose`; or Remotion with `@remotion/media-utils` `visualizeAudio` + captions; brand frame around the waveform.

### M. Finishing existing footage by hand
- Pireel local editor, or hosted Pireel through its MCP for agent-driven trims, captions, variants (`references/pireel.md`).
