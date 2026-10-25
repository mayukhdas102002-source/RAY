# 08 · Assembly, sound and finish

## Assembly order

1. **Animatic first.** Render the Remotion edit with boards, live screens and subtitles. Watch it for timing before generating a single paid plate.
2. **Draft plates.** Free or cheap generations drop into `public/plates/` and are listed in `PLATES`. Check the flow.
3. **Final plates.** Re-run on the assigned models. Trim with `plateStart` and adjust `plateSpeed` (for example 1.5–1.8× to tighten a slow dolly).
4. **Screens and overlays** corner-pinned on (`07`).
5. **Picture lock**, then sound, then grade and finish.

## Sound (sells realism more than picture)

- **Room tone** under every shot, even silent ones.
- **One signature sound** repeated as rhythm (a lift ding, a phone buzz, a chime). It can soften or intensify as the story turns.
- **J and L cuts.** The next shot's sound starts early, so cuts feel intentional, not stitched.
- **Silence before the payoff**, a full second, then the biggest hit.
- **VO and dialogue.** Use real actors, or a licensed synthetic voice with a clear brief (age, accent, warmth, pace). Lines land off-mouth unless lip-sync is used.
- **Music.** Commission or license it for the master. Save AI music for drafts only. Enter late (not under the setup), rise into the reveal, and resolve on the logo.
- **Local detail.** Native birds, street sounds, and the accents the audience knows.

Deep reference: `library/higgsfield/skills/higgsfield-audio/GUIDE.md`.

## Finish

- **One LUT for every shot.** Grade everything through the same look, then match shots to each other.
- **One grain and halation pass** over the whole film (35mm-style), applied after the grade. This hides model texture differences.
- **Upscale selects** to 4K (Topaz or Bytedance upscale), master at 1080p or 4K, and deliver at the frame rate you generated in. Prefer 24 fps if every plate was generated at 24.
- **Deflicker** time-lapses and any shot with light flicker (Higgsfield Video Deflicker).

## Deliverables

Master, :30 and :15 cutdowns, 16:9 plus 9:16 if needed, a version with burned-in subtitles, clean plates, the Remotion project, and the prompt pack.
