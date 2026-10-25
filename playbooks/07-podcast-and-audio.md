# 07 · Podcast and audio

Everything where sound is the product or the backbone: podcasts and video podcasts, audiograms, voiceovers, audiobooks, radio/audio ads, sonic logos and jingles, music beds, sound design, and fixing bad audio.

The Audio module (`modules/audio/MODULE.md`) runs the judgement: **measure first, decide with exact values, verify after**. The Produce module's `audio.py` runs the deterministic mixing; local voice apps make speech.

## Formats

| Format | Length | Deliverables |
|---|---|---|
| Podcast episode (audio) | 15–90 min | WAV master + MP3 (128–192 kbps), chapters, show notes, transcript |
| Video podcast | 15–90 min | Multi-cam edit 16:9, clips 9:16, captions |
| Audiogram | 30–90 s | 1:1 / 9:16 waveform + captions + cover art |
| Voiceover / narration | any | 48 kHz 24-bit WAV per line/scene + script |
| Audiobook | chapters | per-chapter files, consistent loudness, M4B with chapters |
| Audio ad (radio/streaming) | 15 / 30 / 60 s | Broadcast-spec WAV + streaming MP3, legal read |
| Sonic logo / jingle | 1–5 s / 15–30 s | Stems + mixes, short/long variants |
| Music bed | per video | Edited to the cut, stems if available, licence |
| Sound design pack | per project | SFX library for the brand (UI, transitions, stingers) |

## Intake extras

Recording setup (mics, rooms, remote tool), number of speakers, target platforms (Spotify/Apple/YouTube), loudness target, intro/outro assets, sponsor reads, show-notes style, voice direction for VO.

## Workflows

### A. Podcast episode
1. **Ingest** each track to `raw/`; `ray tool probe`; sync multitrack by clap or waveform.
2. **Analyse** (Audio module Workflow A): loudness, noise floor, spectral balance per track; findings with exact fixes.
3. **Clean:** noise reduction (DeepFilterNet/Auphonic/ElevenLabs per Audio `transcription-pipeline.md`; ask before cloud upload), high-pass 70–90 Hz, de-ess 5–8 kHz, compression 2–4:1, levelling.
4. **Transcribe** (`ray tool transcribe_words` per track or VoiceStudio diarization) → edit by transcript: remove false starts, long pauses, crosstalk; keep personality. Present major cuts → **G**.
5. **Structure:** cold open (best 20–40 s), intro, segments, ads, outro; chapters from the transcript.
6. **Mix & master:** `ray tool audio mix --voice edit/episode.wav --music assets/music/theme.wav --out audio/master.wav --lufs -16 --tp -1` (podcast −16 LUFS stereo / −19 mono is common; YouTube −14). Verify: `ray tool audio measure`.
7. **Deliver:** WAV + MP3, chapters, transcript (`captions_convert --to srt/vtt`), show notes in `delivery/SHOWNOTES.md`.

### B. Video podcast + clips
Multi-cam: sync cameras to the master audio, switch to the active speaker (by transcript speaker turns), wide shot every 30–60 s; then clip mining via `playbooks/03-social-short-form.md`. Audiograms: Remotion with `@remotion/media-utils` `visualizeAudio` + captions + brand frame, or OpenMontage `podcast-repurpose`.

### C. Voiceover / narration / audiobook
1. Script prep: pronunciations (brand lexicon), pauses as punctuation, numbers spelled as spoken.
2. Voice: human casting brief **or** cloned brand voice (consent) via `ray tool voice clone/generate` (Voicebox Qwen3-TTS for commercial English and 9 more languages; VoiceStudio VoxCPM2/CosyVoice for many languages; long-form TADA/Voicebox Stories).
3. Sample line → **G** → batch per scene/chapter, seeds pinned.
4. QC: fresh transcript vs script (missing/mangled words), consistent loudness per file (audiobooks ≈ −18 to −23 LUFS RMS-style specs per retailer; check the target platform), room tone between paragraphs.

### D. Sonic logo / jingle / music bed
- Brief: 3–5 brand adjectives → musical translation (tempo, key/mode, instrumentation, motif length 3–5 notes).
- Create: commission, licensed library, or generative music (Suno/ElevenLabs/Lyria via OpenMontage or a music MCP) with commercial terms; log licence.
- Edit beds to the cut with beat-accurate splices (herk `music-grid.mjs` + `splice-music.mjs`).
- Sound design: Audio module `sound-design-dsp.md` for synth recipes and exact parameters; ElevenLabs SFX generation (herk `sfx.mjs`) for one-shots.

### E. Fix bad audio
Measure → diagnose (Audio Workflow A) → fixes with exact settings (noise, reverb, clipping, levels, hum at 50/60 Hz + harmonics) → re-measure → A/B report. Be honest about what can't be recovered.

## Loudness targets (defaults; confirm per platform)

| Destination | Integrated | True peak |
|---|---|---|
| Podcasts (stereo) | −16 LUFS | ≤ −1 dBTP |
| YouTube / social video | −14 LUFS | ≤ −1 dBTP |
| Broadcast | −23 LUFS (EBU R128) / −24 LKFS (ATSC A/85) | −1 / −2 dBTP |
| Music streaming | ≈ −14 LUFS (platform-normalised) | ≤ −1 dBTP |

## Accelerators

audio-analyzer MCP (`modules/audio/references/setup.md`), Voicebox/VoiceStudio MCPs, ElevenLabs or other voice/music MCPs if connected (announce paid calls), Pireel for video-podcast trims.
