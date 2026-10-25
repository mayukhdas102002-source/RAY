# The master clock, captions, and the mix

## Lock the clock

Everything time-based derives from one source:
- **VO-led films:** measured VO lengths. `timeline_from_vo.py scenes.json` → scene start = previous end; duration = max(`min_duration`, `lead` + VO + `tail`) (defaults lead 0.25 s, tail 0.45 s), snapped to frames; fixed `duration` wins for music-cut or picture-led scenes.
- **Footage-led films:** the locked cut (`edit/clean.mp4`) and its retimed transcript (herk chain).
- **Music-led pieces:** the beat grid (herk `music-grid.mjs` / `beatgrid.mjs`, or HF `npx hyperframes beats`).

Outputs: `timeline.master.json` (scenes with `start`, `duration`, `voFile`, `voDelay`, `voDuration`), `timeline.md` (review table), `captions/words.master.json` (all words on the master clock), plus the engine feeds. Any VO pickup → re-run; never hand-edit times downstream.

## Captions

**Sources of word timing, best first:** VoiceStudio WhisperX (`transcribe_words.py --backend voicestudio`) → faster-whisper → HyperFrames whisper.cpp/Parakeet → OpenAI whisper-1 → ElevenLabs Scribe. Use `--script` to restore brand spellings (ASR timing kept, script text copied where tokens align). If >20% junk tokens, retry with a larger model.

**Style rules (merged from herk, OpenMontage, Remotion):**
- Vertical 1–3 words per cue; landscape 6–8. Break on sentence punctuation, on pauses > 0.6 s and at every scene cut.
- Appear ~2 frames before the first word; hard swap (no pop); a cue ends ~0.2 s after its last word or at the next cue.
- Active word highlighted in the brand accent; whole-chunk colour only for meaning (wrong way / concept / payoff) and sparingly.
- One dark box with a thin light edge, always: measure what's behind it. Never over a mouth, chin or face; in a split layout sit on the seam.
- Brand case (all caps for punchy social; sentence case for long-form/LinkedIn).

**Outputs:**
```bash
python scripts/captions_convert.py captions/words.master.json --to srt --out delivery/film.en.srt          # sidecar (YouTube, LinkedIn)
python scripts/captions_convert.py captions/words.master.json --to vtt --out delivery/film.en.vtt
python scripts/captions_convert.py captions/words.master.json --to ass --vertical --brand brand/brand.json --out captions/film.ass
ffmpeg -i clean-master.mp4 -vf "ass=captions/film.ass" -c:a copy burned.mp4                                # burn-in without an engine
python scripts/captions_convert.py captions/words.master.json --to remotion --out remotion/src/captions.json
python scripts/captions_convert.py captions/words.master.json --to hyperframes --out hyperframes/transcript.json
```
Engines: Remotion starter `Captions.tsx` (word-highlight pages); HyperFrames `hf_build.py` captions sub-composition, or registry components (`npx hyperframes catalog --query captions`: caption-pill-karaoke, caption-kinetic-slam…), or the `/embedded-captions` workflow (35 styles, captions composited behind the subject). OpenMontage: `subtitle_gen` + `remotion_caption_burn`. Pireel: `set_captions` presets (`em-*`, `ln-*`).

Deliver a clean (no burned captions) master plus SRT for platforms with native captions; burned-in for sound-off social.

## The mix

Order of operations: **voice first** (clean, levelled, de-essed if needed), then the bed under it, then SFX, then the master limiter/loudness.

```bash
python scripts/audio.py mix --timeline timeline.master.json --music assets/music/bed.wav --sfx audio/sfx.json \
       --out audio/master.wav --lufs -14 --tp -1 --under-db 12 --duck-db 5
python scripts/audio.py measure audio/master.wav
python scripts/audio.py mux renders/film.raw.mp4 audio/master.wav --out delivery/film.mp4      # render_matrix does this per variant
```
What `mix` does: places each scene WAV at `start + voDelay`; measures voice and music loudness and sets the bed `under-db` below the voice (+`duck-db` between lines), then sidechain-compresses the bed under speech; fades the bed in/out; places SFX (`[{t, file, gain_db}]`); two-pass `loudnorm` to target, then a true-peak limiter; 48 kHz 24-bit stereo.

Targets (from brand.json; defaults):

| Destination | Integrated | True peak |
|---|---|---|
| Social (Reels, TikTok, Shorts) / YouTube / web | −14 LUFS | ≤ −1 dBTP |
| Talking-head reels (herk short-form-edit) | −16 to −14 LUFS | ≤ −1 dBTP |
| Broadcast (check the station spec) | e.g. −23 LUFS (EBU R128) / −24 LKFS (ATSC A/85) | ≤ −1 / −2 dBTP |

Rules:
- Music bed 9–14 dB under the voice while speaking; if the user says music is too loud, lower the bed **relative to the voice**, not the master.
- Music starts on the first frame or with a 1–2 s fade; ends on the last visual frame with a 1.5–3 s fade; never fade the last word.
- B-roll audio under speech at −20 to −30 dB or muted.
- SFX only on visible actions, aligned to the audible peak (not the file start); vary files for repeated items; leave some cuts dry. No lasers, plops, risers on every cut.
- Never time-stretch the voice to fit; lengthen the scene.
- Mono measures ~3 dB quieter than stereo: always measure the **final stereo encode** (`qa_check.py --lufs`).
- For anything that sounds wrong (harshness, muddy low end, masking, a reference to match), hand off to **Audio module**: measure → diagnose → exact EQ/compression values → re-measure.

Music sourcing order (OpenMontage's rule): user's `music_library/` → licensed search → generated (Suno/ElevenLabs/Lyria via OpenMontage or herk `kie.mjs`) → bring your own → none. Log the licence in the ledger.
