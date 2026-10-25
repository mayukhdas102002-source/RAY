# 01 · Ads and commercials

Spots that sell one promise fast: broadcast/online video (TVC, pre-roll), performance social ads, UGC-style ads, AI-generated hyper-real ad films, and the variant sets that feed testing.

## Formats

| Format | Length | Aspects | Notes |
|---|---|---|---|
| Hero spot (online/TV) | 15 / 30 / 60 s | 16:9 (+ 9:16, 4:5 cutdowns) | Broadcast: station loudness spec, safe titles, slate if required |
| Performance social ad | 6 / 15 / 20–30 s | 9:16, 4:5, 1:1 | Hook in 0–2 s, product by 3 s, captions burned, CTA end card ≥ 2.5 s |
| Bumper | 6 s | 16:9, 9:16 | One image, one line, logo |
| UGC-style ad | 15–45 s | 9:16 | Real creator (consented) or clearly scripted talent; phone-native look |
| AI ad film | 30–60 s | 16:9 + 9:16 | Direct module end to end, Higgsfield plates, Remotion text layer |
| Variant set | per cell | per placement | Hooks × angles × CTAs × aspects via `variants.json` |

## Intake extras

- Campaign objective (awareness, consideration, conversion) and the KPI; offer/price/terms (legal lines?).
- Placements and specs; whether paid media needs sound-off versions.
- Mandatories: logo, legal super, disclaimers, price display rules, product shots.
- Testing plan: how many hooks/angles; budget per variant.

## Workflow

1. **Brief + message hierarchy** (Direct `director/01-intake-and-brief.md`): one promise, ≤ 2 proofs, everything else to end card/landing page. → **G**
2. **Reference teardown** if refs given: `ray tool info <url>`, `ray tool captions <url>`, `ray tool frames <url> --mode scene`; Direct `cut_log.sh`, `contact_sheet.sh`; write `refs/REFERENCE-ANALYSIS.md` (shot log, cut rhythm, the one wow, product moment, lessons).
3. **Concepts:** 3–6 loglines (Direct `director/03-concept-and-story.md`, `modules/direct/templates/logline-sheet.md`), each with the image, the wow, the product moment, the line. Recommend one. → **G**
4. **Script/treatment:** 30 s ≈ 8–12 shots, ≈ 60–75 words VO max. Treatment (`modules/direct/templates/treatment.md`) for Full mode. → **G**
5. **Choose the making route** per shot:
   - Live-action-real look → AI plates (Direct `05`–`06`, Higgsfield via `connectors/higgsfield.md`) or client footage.
   - Graphic/product-led → Remotion/HyperFrames with product stills/renders.
   - UGC → real creator footage → herk cut chain (`playbooks/06-people-on-camera.md`).
   Log engine + models → **G**
6. **Look lock (AI films):** cast/set/look tokens, reference sheets, one approved keyframe per shot; screens blank for Remotion inserts. → **G**
7. **Samples before spend:** one hero shot draft on a cheaper model/setting, cost quoted (`get_cost` on Higgsfield). → **G**, then batch. Ledger every plate.
8. **Voice:** brand clone (`ray tool voice generate …`) or casting brief for a human VO; music direction; sound plan (Direct `08`).
9. **Build the edit:** `ray tool shots_to_scenes direction/shots.json --out scenes.json` → text layer, supers, legal, product UI, end card in Remotion (`modules/produce/templates/remotion-brand` or `modules/direct/templates/remotion-starter`). Animatic first. → **G**
10. **Finish:** one LUT/grade, one grain, mix (`ray tool audio mix … --lufs -14` or broadcast target), captions.
11. **Variants:** fill `variants.json` with hook × CTA × aspect rows; draft all → **G** → finals.
12. **QA:** quality bar + realism checklist (Direct `09`) + legal supers readable (≥ 2 s per line, contrast).

## Craft rules

- The product appears as a real thing in a real hand by second 3–5; the phone/product is the hinge that changes the world.
- One wow, motivated by the promise. Two at most. No stacks of metaphors.
- Show the benefit, not the feature list; one engine for multi-feature asks (Direct `03` "one engine").
- Brand name/visual identity in the first 3 s for performance ads, and again at the end.
- Generate long, cut short: keep the cleanest 2–3.5 s of each plate.

## Sound

Music lands on the reveal; VO dry and close; SFX on product interactions; sonic logo on the end card if the brand has one (`playbooks/07-podcast-and-audio.md`). Social −14 LUFS; broadcast per station (often −23 LUFS EBU R128 / −24 LKFS ATSC A/85).

## Deliverables

Masters per aspect, clean (textless) versions if requested, captions SRT, end-card stills, thumbnails, the variant matrix with manifest, client shot-by-shot, prompt pack + ledger for AI shots.

## Accelerators

Higgsfield MCP (plates, Marketing Studio DTC formats), voice MCPs, Canva/Figma connectors for static companions, storage connectors to pull product shots, OpenMontage `cinematic` pipeline for provider-agnostic generation.
