# Playbooks: pick the workflow for the content

Each playbook gives formats and specs, intake extras, a step-by-step workflow (module · script · gate), craft rules, sound, QA extras, deliverables, and which connectors speed it up. Shorthand used in all playbooks:

- `ray tool <name> …` = `python scripts/ray.py tool <name> …` (runs any script in `modules/read/scripts`, `modules/produce/scripts`, `modules/direct/tools`)
- **Read / Direct / Produce / Audio** = the modules in `modules/`
- **G** = a gate: stop and get approval (skip in Quick mode unless noted)

## Find the playbook

| The person says… | Playbook | ID for `ray.py new --playbook` |
|---|---|---|
| ad, commercial, TVC, spot, promo, campaign, UGC ad, performance creative, AI ad | 01 Ads & commercials | `ads` |
| brand film, manifesto, our story, about us, case study, testimonial, mini-doc, impact story | 02 Brand films & stories | `brand-film` |
| reel, TikTok, Short, story, clips, series, hooks, carousel to video, repurpose | 03 Social short-form | `social` |
| explainer, how it works, tutorial, how-to, lesson, course, onboarding, data story | 04 Explainers & education | `explainer` |
| launch, demo, feature video, walkthrough, product video, e-commerce, unboxing | 05 Product & tech | `product` |
| founder video, talking head, interview, thought leadership, personal brand, vlog | 06 People on camera | `people` |
| podcast, audiogram, voiceover, audiobook, jingle, sonic logo, music, sound design, clean up audio | 07 Podcast & audio | `audio` |
| event recap/promo, conference, internal comms, recruitment, training, investor video, pitch, annual report, fundraising appeal, public information | 08 Events & organisations | `org` |
| logo animation, sting, intro/outro, title sequence, kinetic type, lyric video, infographic, slides to video, loop, screen background | 09 Motion & design | `motion` |
| translate, dub, subtitles, other languages, accessibility, audio description | 10 Localisation & accessibility | `localise` |
| personalised, 100 versions, from a spreadsheet, catalogue, listings, dynamic ads | 11 Personalised & at scale | `batch` |
| short film, music video, trailer, series, character, animation, story | 12 Narrative & entertainment | `narrative` |
| any of the above for finance, health, property, travel, food, fashion, SaaS, education, government, nonprofit, automotive, B2B | 13 Industry notes (add-on) | – |

Mixed asks are normal: a launch campaign = 05 (hero) + 01 (ads) + 03 (cutdowns) + 10 (languages). Plan them as one project with one brand kit, one script family and one `variants.json`.

## The shared spine (every playbook follows it)

1. **Understand** — `core/intake.md`; read references (`ray tool info|captions|frames|transcribe`); brief → G.
2. **Kit** — `ray tool brand_tokens brand/brand.json --project .` (build a kit if none).
3. **Story** — concepts → script with picture/VO/on-screen text/sound columns → G.
4. **Plan the making** — scene list (`scenes.json`) or shot list (`direction/shots.json`); engine choice (Remotion/HyperFrames/OpenMontage/herk/Pireel/Higgsfield) logged → G.
5. **Voice & assets** — samples first → G → batch; ledger every file.
6. **Lock the clock** — `ray tool timeline_from_vo scenes.json --remotion remotion --hyperframes hyperframes`.
7. **Compose** — preview link → G.
8. **Captions, mix, master** — `ray tool captions_convert …`, `ray tool audio mix …`.
9. **Drafts → QA → finals** — `ray tool render_matrix variants.json --draft` → G → finals → `core/quality-bar.md`.
10. **Deliver** — manifest, sidecars, stills, `VERIFY.md`, summary.
