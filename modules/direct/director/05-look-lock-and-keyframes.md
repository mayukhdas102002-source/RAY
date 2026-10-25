# 05 · Look lock and keyframes

Continuity is the difference between "AI clips" and "a film". Lock it before you make shot 1.

## Tokens (paste verbatim into every prompt)

Write each as one sentence of concrete, visible facts. Never vary the wording between shots.

- **[CHARACTER]** — age, heritage, skin tone, hair (colour, length, style), facial hair, build, exact wardrobe items, one distinctive accessory, and "natural skin texture with pores and fine flyaway hairs".
- **[SET]** — materials, colours, fixed furniture, light sources and their direction, windows and what's outside them, one signature detail.
- **[LOOK]** — camera and lens family, light philosophy (motivated, natural), contrast, grain, "no text, no logos".
- **[OBJECT]** — the hero prop (a binder, keys, a phone model), and how it's held.

Example tokens: `examples/homely-going-up/tokens.md`.

## Reference sheets (make these first and attach them to every generation)

1. **Character sheet per cast member.** Front, three-quarter and profile heads, one full body, neutral and smiling, plain mid-grey background, even light. For recurring cast use Higgsfield Soul ID (see `library/higgsfield/skills/higgsfield-soul/GUIDE.md`).
2. **Set sheet.** Four to five views of the main location, with the same light logic in every view.
3. **Hero prop or asset sheet** if a designed object recurs (a mascot, a vehicle, a folded bird).

The plain-grey sheet rule: backgrounds on sheets must be neutral, or they leak into shots.

## Keyframe rules

- **One approved still per shot.** Make 3–4 variants and pick one. A start and end pair for any transformation or continuous move.
- **Device screens blank.** Every phone, tablet, monitor, sign and floor display is generated "plain white" or "plain grey" and flat to camera where possible. Remotion replaces them (`07`).
- **Frame for the letterbox or crop.** If you'll deliver 16:9 and 9:16, keep action inside the centre safe area.
- **Mid shots over macro faces.** Extreme close-ups of eyes, teeth and hands expose AI fastest. Prefer 35–50mm with air around people.
- **Diffuse surfaces.** Brushed steel over mirror, matte over gloss, where reflections would have to be physically correct.
- **Background people soft.** Out of focus or motion-blurred.
- **Edit your own frames for callbacks.** To repeat a composition later (bookends), image-edit the earlier keyframe ("keep framing identical; change X") instead of generating fresh. It's free continuity.

## Keyframe prompt shape

```
[LOOK] + shot size and lens + subject token(s) doing a specific, held action + set token or location specifics +
light direction and quality + one environmental pressure + one micro-detail + what must be blank + safe-area note
```
Depth: `library/visual-skills/image/references/prompt-framework.md`, `golden-rules.md`, `de-slop.md` (anti-AI-look), and the model files `nano-banana.md` / `gpt-image.md`.

## Model choice for stills (Higgsfield)

- **Nano Banana / Gemini image.** Best for edits and consistency ("keep everything, change the brochure to keys").
- **GPT Image 2.** Structured sheets and layout-heavy frames.
- **Soul / Soul Cinema.** Photoreal people with a trained identity.
- **Seedream / FLUX.** Alternates for texture and photoreal environments.

Check current names and limits in `library/higgsfield/specs/IMAGE-MODEL-SPECS.md`.
