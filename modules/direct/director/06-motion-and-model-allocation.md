# 06 · Motion and model allocation

## Allocate by the shot's job, not by habit

| Shot job | First choice | Why | Fallback |
|---|---|---|---|
| Hero wow: crowds, many agents, complex physics, a big reveal | **Seedance 2.5** (1–2 shots per film) | Best complex motion and 30s single pass; omni-reference | Seedance 2.0 |
| Transformation or VFX between a start and end frame (wall collapses, object morphs, sofa lands) | **Minimax H3** | Strong start/end-frame VFX, cheap | Seedance 2.0 Fast |
| Camera move over a mostly static world (drone, dolly, locked-off time-lapse, crane) | **Wan 3.0** | Precise camera control, cheap, 2–30s | Kling 3.0 |
| Acting: faces, hands, small reactions, a character interacting with an object | **Kling 3.0** | Best subtle performance; lip-sync; multi-shot labels | Seedance 2.5 (faces) |
| Dialogue with lip-sync | **Kling 3.0** or **Veo 3.1** | Native audio and lips | Sync Lipsync on a finished plate |
| Time-lapse, drafts, anything forgiving | **Genjutsu (free)** · **Seedance 2.5 Draft / 2.0 Mini** | Zero or low cost | Minimax H3 |
| Scale reveal from ground to orbit | **Higgsfield Effects · Earth Zoom Out (free)** | One image in, the move out | Wan 3.0 with an end frame |
| Upscale / finish | **Topaz** · **Bytedance Video Upscale** | 4K from 1080p selects | — |

Check the live limits (durations, resolutions, modes, which media roles such as `start_image`/`end_image` are allowed) in `library/higgsfield/specs/MODEL-SPECS.md` before writing a header. Minimums matter: Minimax H3 starts at 4s, Seedance 2.5 at 4s, Kling 3.0 at 3s, and Wan 3.0 at 2s.

## Budget rule

- Two Seedance-class shots per film, maximum, unless the client's budget says otherwise.
- Draft every shot on a free or cheap model first. Check the timing in the Remotion animatic, then spend.
- Stop-rule: two same-flaw failures on an unchanged prompt means rewrite the prompt. Don't reroll a third time. Full ladder: `library/higgsfield/skills/higgsfield-troubleshoot/GUIDE.md`.

## Motion prompt shape

```
What moves, and how (one primary action, a chain of at most 2–3 connected steps) +
camera: ONE move, speed and reason ("slow push-in as she reads") +
what stays rigid ("lift interior rigid, no warping") +
real speed ("natural walking pace, no slow motion") +
duration + final state ("ends with the doors fully open, couple on the grass")
```

Rules that matter most for realism:
- **Describe consequences, not just actions.** "The key turns and the latch clicks open", not "she unlocks the door".
- **Start in the state** for results reached through a reversing motion (reach in and pull out). **Chain** for simple forward motion (see `library/higgsfield/skills/shared/house-rulings.md` P2-1).
- **One camera move per shot.** Stacked moves cause warping.
- **Walking is the hardest stunt.** Keep walks short, and prefer shots from behind or waist-up.
- **Keep dialogue off-mouth** unless you're using a lip-sync model. Lines land over shoulders, on reactions, or toward a ceiling speaker.
- **Generate at the minimum length and keep the best 2–3.5s** using the edit's `plateStart`.

## Per-model grammar

Open the one file for the model you chose:
- Seedance 2.0: `library/visual-skills/video/references/seedance.md` + `library/higgsfield/skills/higgsfield-seedance/GUIDE.md`
- Seedance 2.5: `library/visual-skills/video/references/seedance-25.md` + `library/higgsfield/skills/higgsfield-seedance-2-5/GUIDE.md`
- Kling 3.0: `library/visual-skills/video/references/kling.md`
- Veo: `library/visual-skills/video/references/veo.md`
- Minimax / Wan / others: `library/higgsfield/model-guide.md` and `library/higgsfield/skills/higgsfield-models/MODELS-DEEP-REFERENCE.md`
