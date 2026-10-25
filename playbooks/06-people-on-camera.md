# 06 · People on camera

Videos built around a real person speaking: founder and creator videos, thought leadership, interviews, testimonials, personal-brand intros, vlogs, CEO messages, webinar highlights.

## Formats

| Format | Length | Aspect | Notes |
|---|---|---|---|
| Founder / creator talking head | 30–120 s | 9:16 + 16:9 | Punchy cut, overlays, captions |
| Thought leadership | 2–6 min | 16:9 | Chapters, lower-thirds, slides/graphics inserts |
| Interview (single or two-person) | 3–30 min | 16:9 | Multi-cam/angle, names, B-roll |
| Personal intro / about me | 30–60 s | 9:16 / 1:1 | Warm, specific, one CTA (book, follow, hire) |
| Vlog / day in the life | 3–12 min | 16:9 / 9:16 | Story spine = the day; J/L cuts |
| CEO / leadership message | 1–3 min | 16:9 | Teleprompter delivery, plain language, captions mandatory |

## Intake extras

Raw takes or a shoot to plan? Retakes in the file? Teleprompter? Speaker's name/role spelling, how they like to look (framing), topics off-limits; whether to remove filler words; brand overlays style.

## Shoot guide (if not shot yet; send to the person)

Eye-level camera, lens at arm's length or further; soft light in front, window to the side; 1080p+ at 30 fps (or 4K for punch-ins); lav or close mic, 30 s room tone at the start; plain uncluttered background with depth; record each answer twice if unsure; phone vertical for 9:16-only content, landscape 4K if you need both.

## Workflow

1. **Ingest:** copy to `raw/` (read-only); `ray tool probe raw/take.mp4`.
2. **Transcribe:** `ray tool transcribe_words raw/take.mp4` (local) or herk Scribe (`transcribe-elevenlabs.mjs`, paid; announce).
3. **Cut silences:** herk `cut-silences.mjs … --apply` (gap 0.55 s default; lower for punchier).
4. **Mistake candidates:** herk `find-cut-candidates.mjs` → show the list with context → the person approves/edits (`approved-cuts.json`) → **G** → `apply-cuts.mjs --apply` → `edit/clean.mp4`. Zero cuts is valid.
5. **Read the whole transcript by hand** for retakes the detector missed; build the story order (paper edit) if reordering. → **G**
6. **Lock the cut** + retimed transcript → `assets/transcript.json` for the composition.
7. **Overlays:** plan beats anchored to phrases — lower-third on first appearance, full-screen takeovers for thesis/stat/quote, B-roll per noun phrase, punch-ins (1.1–1.2× scale) on emphasis (herk `hyperframes-video-beats`; validate with `validate-beat-sync.mjs`).
8. **Captions** from the retimed transcript; never over mouth/chin; seam position in splits.
9. **Audio:** dialogue clean-up (Audio module: high-pass ~80 Hz, gentle de-ess, compression 3:1, level), room tone into gaps, music −18 to −12 dB under, master −14 LUFS (−16 for spoken-word if requested).
10. **Versions:** 16:9 master; 9:16 via reframe-from-native-resolution or split layout (B-roll top / speaker bottom); clips via `playbooks/03-social-short-form.md`.

## Craft rules

- Cut between phrases, never inside one; never speed up a voice.
- Keep natural breaths after commas and sentence ends (0.14–0.24 s); remove dead air.
- First cut at 0.6–1.0 s for social; the speaker's face visible in the first frame.
- Join takes only where both sides are silent; a 20–30 ms fade hides clicks.
- Don't erase the speaker: B-roll supports, it doesn't replace.

## Consent and likeness

Speakers sign off on the final cut for sensitive messages; no voice cloning of the speaker without consent; never AI-alter what they said. Avatars/digital twins only for the consenting person, disclosed (`core/rights-and-safety.md`).

## Deliverables

Master per aspect, clean (no captions) version, SRT, transcript, chapters (long-form), cover frames, the cut log (EDLs) for future re-edits.

## Accelerators

Pireel (transcript-based trims, `remove_silence`, caption presets, multiple outputs), HyperFrames `/talking-head-recut` and `/embedded-captions` workflows, OpenMontage `talking-head` pipeline, avatar MCPs (HeyGen) only with consent.
