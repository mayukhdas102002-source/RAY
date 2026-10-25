# 03 · Social short-form

Vertical-first content that has to earn every second: Reels, TikToks, Shorts, Stories, LinkedIn/X video, recurring series, clips from long-form, carousel-to-video and trend formats.

## Formats

| Format | Length | Aspect | Notes |
|---|---|---|---|
| Reel / TikTok / Short | 7–60 s (sweet spot 15–35 s) | 9:16 1080×1920 | Hook ≤ 3 s, captions burned, safe area x 90–930 / y 200–1600 |
| Story | 5–15 s per card | 9:16 | Tap-through frames, sticker-safe zones |
| Feed video | 15–60 s | 4:5 / 1:1 | Square-safe framing |
| LinkedIn / X | 30–90 s | 1:1 / 4:5 / 16:9 | Professional tone, captions on, first frame readable as a thumbnail |
| Clip from long-form | 20–60 s | 9:16 | One idea per clip, self-contained |
| Series | 3–20 episodes | 9:16 | Repeatable format: same open, same structure, new content |

## Intake extras

Platform(s) first; handle and audience; recurring series or one-off; source material (long video, podcast, blog, deck, product); posting cadence; trends they want to join (sounds must be licensed for business accounts).

## Workflow (single reel)

1. **Hook first:** write 3 openings (problem / result glimpse / recognition) from the same true material; compare sound-off. → **G** (pick one)
2. **Beat plan:** hook → open loop → 2–4 beats of proof/value → payoff → CTA. 1–2 s per visual event as a diagnostic; every beat has an action.
3. **Source path:**
   - **Talking head:** herk `short-form-edit` (`modules/produce/references/herk-edit-kit.md`): transcribe, silence + mistake cuts, read the full transcript by hand, three openings, footage ledger, validators.
   - **VO + graphics:** script → `ray tool voice generate` → `transcribe_words` → `timeline_from_vo` → Remotion `BrandFilm-9x16` or `hf_build.py --size 1080x1920`.
   - **Footage/B-roll montage:** shot list → real clips/screen recordings → AI clips only for metaphors.
4. **Captions:** 1–3 words, active word highlighted, dark box, never over the mouth; brand case. Native platform captions off when burned in.
5. **Rough animatic** at low res, check first 3 s and every cut strip. → **G**
6. **Sound:** voice normalised, music bed 11 dB under (9–14), SFX on visible actions only; −14 LUFS / ≤ −1 dBTP on the final stereo encode.
7. **Render + QA:** `ray tool render_matrix variants.json --draft` → **G** → finals; thumbnail/cover frame per platform.

## Workflow (clips from long-form)

1. Transcribe the long video (`ray tool transcribe_words long.mp4`) or pull platform captions (`ray tool captions <url>`).
2. Find 5–15 candidate moments: a strong claim, a story, a surprising number, a how-to step, an emotional peak. Score each on hook strength and self-containedness.
3. Present the shortlist with timestamps → **G**.
4. For each: trim to the idea (cut between phrases), reframe the speaker (`ray tool reframe clip.mp4 --to 9x16 --mode crop --x <focus>` or Pireel `set_clip_framing punch-in`), captions, hook overlay text, end card.
5. Batch via `variants.json` (`engine: "file"` rows) or OpenMontage `clip-factory` / `podcast-repurpose` for big batches.

## Series design

Define once in `DECISIONS.md`: series name, open (≤ 1 s sting), structure, caption style, end card, cadence. Build the open and end card as reusable Remotion/HyperFrames compositions; each episode only swaps content.

## Craft rules

- Speech starts within 0.1 s; no logo intros; first cut at 0.6–1.0 s.
- Shots average 1.1–1.4 s for energetic edits (talking-head reels); explainers can hold 2–3 s.
- Speaker on screen ~40–50% for personal brands, never gone > 3.5 s.
- One visual per noun phrase; each list item gets its own shot; callback to the hook before the CTA.
- Trend audio: business accounts need commercially licensed sounds; otherwise use licensed music.

## Deliverables

9:16 masters, optional 4:5/1:1, cover frames, captions SRT, post copy (hook line, caption, hashtags, alt text) in `delivery/POSTS.md`.

## Accelerators

Higgsfield content-factory/shorts workflows (`modules/direct/library/higgsfield/skills/higgsfield-content-factory/`), Pireel for fast hands-on variants, scheduling/publishing connectors if attached (only with explicit approval to post).
