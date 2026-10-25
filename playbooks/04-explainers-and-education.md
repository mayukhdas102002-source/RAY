# 04 · Explainers and education

Making something understood: product/service explainers, how-tos, tutorials, course lessons, onboarding, data stories and "how it works" pieces.

## Formats

| Format | Length | Aspect | Style options |
|---|---|---|---|
| Explainer | 60–120 s | 16:9 (+ 9:16 cut) | Motion graphics, illustrated, kinetic type, hybrid footage |
| How-to / tutorial | 1–8 min | 16:9 | Screen recording + VO + callouts; or hands-on footage |
| Course lesson | 3–15 min per lesson | 16:9 | Presenter + slides/graphics, chapters, quiz cards |
| Onboarding | 30–90 s per step | 16:9 / in-app | Short, task-focused, one action per video |
| Data story | 45–120 s | 16:9 / 1:1 | Charts that build, one number per beat |
| Micro-lesson | 30–60 s | 9:16 | One concept, one example, one takeaway |

## Intake extras

Learner and starting knowledge; the single learning objective ("after this, you can…"); source material (docs, decks, SME interviews); accuracy reviewer; accessibility needs (captions mandatory, transcripts, plain language level).

## Workflow

1. **Objective + misconceptions** → **G**: write the one objective and the 2–3 misconceptions to correct.
2. **Script** with the teacher structure: hook (why it matters) → concept in plain words → concrete example → visual model → recap → next step. ~130–150 words/min for teaching VO. → **G**
3. **Visual model:** design one persistent visual world (herk `video-storytelling` rules: never redraw, camera moves between world/region/detail, one element at full brightness).
4. **Route:**
   - OpenMontage `animated-explainer` (research-grounded, provider selection, budget caps, review gates; brand style playbook + local voice) — best for research-heavy topics.
   - HyperFrames `/faceless-explainer` workflow or `hf_build.py` + registry blocks (`data-chart`, `flowchart`, `code-diff`, `bar-chart-race`).
   - Remotion starter with `stat`/`list` scenes and chart components; OpenMontage Remotion `Explainer` composition cut types (`bar_chart`, `kpi_grid`, `comparison`…).
   - Screen tutorials: real capture (OBS/Screen Studio), cursor visible, zoom to the action; OpenMontage `screen-demo` for synthetic terminal demos.
   Log the choice → **G**
5. **Voice:** brand clone or presenter; `transcribe_words` for captions and beat anchoring.
6. **Build:** charts ≥ 4 s; label everything that's spoken; nothing on screen that isn't said (or vice versa) unless it's a deliberate reading moment.
7. **Accuracy review:** send the draft + script to the reviewer; log corrections. → **G**
8. **Finish:** captions burned or sidecar (both for courses), chapter markers, transcript export (`ray tool captions_convert … --to vtt`).

## Craft rules

- One idea per scene; ≤ 20 words on screen per section; numbers on their own beat.
- Show the example before the abstraction when the audience is new.
- Recap with the same visuals used to teach (recall), not new ones.
- Tutorials: state the end result first; then steps numbered on screen; pause points.

## Sound

Clear, warm, unhurried VO; light music bed (−18 to −22 dB under VO) or none for tutorials; UI click/whoosh SFX sparingly.

## Deliverables

Master + chapters + captions (SRT/VTT) + transcript (TXT) + thumbnail; LMS-friendly MP4 (H.264, AAC) and optionally per-chapter files.

## Accelerators

OpenMontage research/stock connectors (archives, Pexels/Pixabay), Figma connector or `npx hyperframes figma` for brand assets, docs/drive connectors for source material.
