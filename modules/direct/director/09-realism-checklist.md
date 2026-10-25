# 09 · Realism checklist: "nobody can tell it's AI"

Run this on every plate before it goes into the cut. If a plate fails any item, regenerate it or cut around the flaw. Don't try to fix it in post.

## Tells to reject on sight

- [ ] Hands: extra, fused or melting fingers, objects passing through hands, "mimed" manipulation where the hand moves but the object doesn't.
- [ ] Faces: identity drift across the shot, waxy skin, dead eyes (no blinks, no eye life), mouth moving without sound.
- [ ] Feet sliding on the floor, and walk cycles that float.
- [ ] Physics: liquids, cloth or hair that ignore gravity, and doors or lids that open without a hinge logic.
- [ ] Text: any readable text the model drew (signs, screens, labels). It must be blank or out of focus.
- [ ] Reflections and shadows that don't match their sources.
- [ ] Background people morphing, duplicating or merging.
- [ ] Geometry warping during camera moves (straight lines bending, rooms breathing).
- [ ] Temporal flicker or light pulsing.
- [ ] Hyper-smooth "AI glide" camera with no weight.

## Prevent them in the prompt

- Mid shots at 35–50mm, with people given room. No macro faces unless it's the hero close-up.
- One camera move, at a real speed, with a tripod or dolly feel.
- Name what stays rigid ("walls rigid, no warping").
- Real timing ("natural walking pace", "no slow motion" unless it's deliberate).
- Blank devices, soft background extras, diffuse surfaces.
- Start or end in stable states, and describe consequences.
- Positive-phrased constraints: `library/higgsfield/skills/shared/negative-constraints.md`.
- The slop catalogue and the fixes: `library/higgsfield/skills/higgsfield-seedance-2-5/VFX-PIPELINE.md` and `library/higgsfield/skills/higgsfield-seedance/FAILURE-MODES.md`.

## Make it feel shot, not generated

- Motivated light: every light has a source in the scene (a window, lamp, screen or downlight), and its direction stays consistent within a location.
- Imperfection: slight handheld breathing, occasional focus hunting on a rack, lens breathing, gentle flare from real sources.
- Casting: faces with texture, varied ages and body types, and clothes with creases and wear.
- Lived-in sets: a mug ring, a charger cable, a scuffed skirting board.
- One grade, one grain, and consistent black levels across the whole film (`08`).
- Sound: room tone, foley and real acoustics (`08`).

## The final check

Watch the cut at full speed, on a TV, with sound, three times: once for story, once for continuity (wardrobe, props, screen direction, light direction), once hunting for the tells above. Then show it to someone who hasn't seen it and ask what the film says. If they can't say the promise, the edit isn't finished.
