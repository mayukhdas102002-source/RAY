# 04 · Treatment and shot list

## Treatment (1 page)

Use `templates/treatment.md`: the idea in one paragraph, four "why" boxes (why this setting, why the wow, why the product device, why it's believable), five anchors, look, sound, cutdowns, and open items.

## Shot list as data

Write the shot list as `shots.json` (schema: `templates/shots.example.json`). The same file drives:
- the storyboard or client page,
- the Remotion animatic and final edit,
- the prompt pack.

Edit once and everything stays in sync.

Every shot carries: `id`, `t` [start, end], `act`, `name`, `maker` (AI / AI + Remotion / Remotion / Higgsfield effect), `model`, `point` (which message or feature), `frame` (what we see), `sound`, `remotion` (UI layer), `key` / `key_start` (image prompts), `motion` (video prompt), `note`.

## Shot card (for each row)

Beat · job (change emotion / advance action / raise pressure; if none, cut it) · frame size and lens · composition · camera move and why · action · eye-trace · duration · cut type · sound · light · UI layer · message. Template: `templates/shot-card.md`. Deeper method: `library/visual-skills/video/references/dramaturgy.md` §10–12.

## Tempo budget

| Master | Shots | Typical lengths |
|---|---|---|
| :15 | 6–9 | 1.5–2.5s, one 3s hold |
| :30 | 8–12 | 2–3.5s, one 4–5s hero |
| :45–:55 | 13–17 | 2.5–4s, two heroes of 4.5–8s |
| :60–:90 | 16–25 | 2.5–5s, one oner or montage section |

Rules:
- Durations must sum exactly to the runtime.
- **No shot under 2s** unless it's inside a deliberate montage run. When a cut feels "stitched", lengthen neighbours before adding transitions. (Real feedback: a 45s version with 1–2s inserts felt abrupt, and stretching to 54.5s with 2–4s shots fixed it.)
- One pause before the biggest moment (silence, stillness, a breath).
- Rhythm ladder for the product arc: longer, shorter, shorter, pause, impact, then hold.

## Monotony audit

No three consecutive shots with the same size AND the same camera move. Alternate wide / medium / close and static / move. Cut on action or on a sound (the lift ding, a phone buzz).

## Transitions that feel expensive, not stitched

- **Sound bridges (J/L cuts).** The next shot's sound starts under the current one.
- **Match cuts.** Shape, motion or colour carried across (a white page into a white door).
- **Motivated wipes.** A car passing, a door closing, a page hitting the lens.
- **Continuous camera.** One move carried through two plates (end frame of A = start frame of B).
- **Avoid:** generic crossfades between unrelated shots, whip-pans without a motion match, and flash frames.

## Numbering

Use S01, S02… in shot order. Split a shot as S20a / S20b rather than renumbering, because clients and editors refer to the numbers.
