# 09 · Motion and design

Pure motion pieces: logo animations and stings, intros/outros, title sequences, kinetic typography, lyric videos, animated infographics, slides/decks to video, social templates, looping backgrounds and screen content for events/retail.

## Formats

| Format | Length | Aspect | Engine of choice |
|---|---|---|---|
| Logo sting / reveal | 2–6 s | all + alpha versions | HyperFrames registry `logo-sting` blocks, Remotion with `@remotion/paths`/`shapes` |
| Intro / outro / bumper | 3–10 s | all | Remotion/HF component reused across a series |
| Title sequence | 20–90 s | 16:9 | HF/Remotion, music-cut |
| Kinetic typography | 10–60 s | 9:16 / 16:9 | Word-timed from VO/lyrics transcript |
| Lyric video | song length | 16:9 / 9:16 | Word timestamps from the vocal stem |
| Animated infographic / data viz | 15–90 s | all | Chart blocks/components, data-driven |
| Slides / deck → video | 1–10 min | 16:9 | Slides as scenes + VO + transitions |
| Motion showreel | 10–30 s | 16:9 | herk `motion-showreel` (beat-locked chapters) |
| Loops / screen content | 5–60 s seamless | any (LED walls: custom) | Seamless loop, no text for ambient screens |
| Social templates | per format | 9:16 / 1:1 | Parameterised compositions (props/variables) |

## Intake extras

Brand motion personality (energetic/calm/precise/playful), logo construction files (SVG layers), music or no music, transparent output needed (overlays), screen specs for LED/retail (resolution, frame rate, codec), reuse as a template?

## Workflow

1. **Motion principles** from the kit (`brand.json → motion`): easing, entrance time, stagger, transition family. → **G** (style frames: 3 stills from Remotion `still`/HF `snapshot`)
2. **Catalog first (HyperFrames):** `npx hyperframes catalog --query "<effect>" --json` before hand-writing any named effect; `npx hyperframes add <block>`; restyle with `brand.css`.
3. **Build** in the chosen engine, frame-pure/deterministic. For logo animation: animate the official SVG's layers; never redraw or reshape the logo; end on the exact lockup.
4. **Music-cut pieces:** beat grid first (`music-grid.mjs`/`npx hyperframes beats`), cuts on beats, motion on off-beats, flurry before the lockup (herk showreel grammar).
5. **Kinetic/lyric:** `ray tool transcribe_words vocal.wav --script lyrics.txt` (align to the real lyrics; lyrics need rights) → word groups → animate per word.
6. **Slides → video:** export slides as images/PDF (pptx/pdf skills or the person's export), one scene per slide, VO per slide (`voice.py`), Remotion `image` scenes or HF `/slideshow` workflow; add motion to builds, not to everything.
7. **Alpha deliverables:** HF `--format mov` (ProRes 4444) / `--format webm`; Remotion `--codec prores --prores-profile 4444 --pixel-format yuva444p10le --image-format png`.
8. **Loops:** make the last frame match the first (seeded noise, cycle lengths that divide the duration); verify by concatenating twice and checking the seam strip.

## Craft rules

- Motion has a reason: reveal, direct attention, show change. Nothing pulses for decoration.
- Brand test: cover the logo on 6 random frames; it should still read as the brand.
- Kinetic type: ≤ 3–4 words on screen at once, readable ≥ 0.6 s, hierarchy by size/weight not colour noise.
- Data viz: start axes at zero for bars; label directly; one insight per chart; source line.

## Deliverables

MP4 masters, alpha versions (MOV/WebM), PNG sequences if requested, GIF/WebM web loops, the reusable template (Remotion composition with props or HF composition with variables) and usage notes.

## Accelerators

Figma connector or `npx hyperframes figma tokens|asset` for design sources, Canva connector for static companions, Higgsfield motion-design/vibe-motion workflows for generative textures (`modules/direct/library/higgsfield/skills/higgsfield-motion-design/`).
