---
name: master-brand-video-pipeline
description: End-to-end brand video production pipeline that orchestrates Remotion, HyperFrames, OpenMontage, herk-edit-kit, Pireel, Voicebox and VoiceStudio. Use for any brand, product, social, explainer, talking-head, launch, logo-sting, data, localised or personalised video - from brief, brand kit and script through cloned-voice VO, word-timed captions, motion graphics, AI/stock assets, talking-head cutting, mix and loudness mastering, multi-aspect renders, QA and delivery. Also use to set up or troubleshoot any of those tools, or to convert work between them.
---

# Master Brand Video Pipeline

> Part of RAY (module: produce). Paths below are relative to `modules/produce/`. RAY's `SKILL.md` decides when this module runs.


You are the producer, editor and finishing house for brand video. Seven open-source tools do the making; this skill decides which one does what, keeps them on one brand and one clock, and proves the result before anyone sees it.

The spine is this file. Details live in `references/` (read the file a stage names before doing that stage). Deterministic glue lives in `scripts/` (stdlib Python 3.10+, FFmpeg, Node 22). Starters live in `templates/`.

## The toolchain

| Tool | What it is here | Licence (check before client work) |
|---|---|---|
| **Remotion** (`remotion-dev/remotion`) | React → video. Data-driven brand films, parametrised/personalised renders, captions, Lambda scale-out. Template: `templates/remotion-brand`. | Source-available: free for individuals, non-profits and companies of **≤3 people**; a **Company License** is required otherwise (remotion.pro). |
| **HyperFrames** (`heygen-com/hyperframes`) | HTML + GSAP → video, no build step. Fast motion graphics, registry of ~400 blocks/components, website capture, batch variables, local Kokoro TTS + whisper transcription. Template: `templates/hyperframes-brand` + `scripts/hf_build.py`. | Apache-2.0. |
| **OpenMontage** (`calesthio/OpenMontage`) | Agentic production system: 12 pipelines (explainer, cinematic, avatar, screen-demo, talking-head, clip-factory, podcast, localisation, documentary…), 100+ tools, 60+ providers, budget control, review gates. | AGPL-3.0 (fine to run locally; modified network service must share source). |
| **herk-edit-kit** (`nateherkai/herk-edit-kit`) | Talking-head editing chain: word transcript → silence cut → reviewed mistake cut → story/beat planning → HyperFrames overlays; short-form reel playbook; music-cut motion showreels. | MIT (kit) + pipeline-use permission; its AIS brand assets are **not** reusable. |
| **Pireel** (`pireel/pireel`) | Browser timeline editor for humans + agents: finishing, caption presets, multi-output variants, B-roll placement. OSS = local editor; agent control (MCP) = hosted pireel.com. | AGPL-3.0; agent plugin Apache-2.0. Hosted generation costs credits. |
| **Voicebox** (`jamiepine/voicebox`) | Local voice studio: cloning, 9 TTS engines (Qwen3-TTS default), Whisper STT, effects, Stories timeline, MCP. API `127.0.0.1:17493`. | MIT app; check each model's weights (OmniVoice = non-commercial). |
| **VoiceStudio** (`debpalash/voicestudio`) | Local voice studio: cloning/design, 600+ languages, **word-timestamp transcription (WhisperX)**, dubbing pipeline, MCP. API `127.0.0.1:3900`. | AGPL-3.0; default OmniVoice weights are **CC-BY-NC**. Use `voxcpm2`/`cosyvoice` for commercial work. |

Sibling modules inside RAY plug in where they're strongest: **Direct** (`../direct/`, formerly AI Director / AI Video Buddy) for hyper-real AI ad films on Higgsfield (concept, shot list, keyframe/motion prompts, model allocation); **Read** (`../read/`, formerly claude vidreader) for reading reference videos and URLs; **Audio** (`../audio/`, formerly master-ai-audio-director) for mix diagnosis and mastering judgement. Connected MCP tools (Higgsfield, ElevenLabs, HeyGen…) are covered in `../../connectors/`. Use them; don't re-derive what they already do.

## The pipeline

Work in order. Every gate ends your turn until the user approves (write the approval into `DECISIONS.md`). If the user pre-authorises the whole run, log that once as `approval_policy` and continue.

| # | Stage | Read | Do | Gate / output |
|---|---|---|---|---|
| 0 | **Setup check** | `references/setup.md` | `python scripts/doctor.py --tools-dir <toolchain>` | Only the tools this route needs are green. Install steps come from the doctor output. |
| 1 | **Intake + route** | `references/routing.md` | Fill `BRIEF.md` (one promise, ≤2 proofs, audience, platforms, lengths, aspects, CTA, budget, claims). Pick a route. `python scripts/new_project.py <folder> --brand <brand dir> --engine both` | **Gate 1:** brief approved. |
| 2 | **Brand lock** | `references/brand-system.md` | Build/verify `brand/brand.json` (+ official logo + font files). `python scripts/brand_tokens.py brand/brand.json --project .` | Contrast + file checks pass; tokens written for every engine. |
| 3 | **References** (if any) | `references/routing.md` §References | vidreader / OpenMontage `video-reference-analyst` / herk `analyze-reference.mjs` / `hyperframes capture <url>` | `refs/REFERENCE-ANALYSIS.md`: what to borrow (mechanisms, pacing), what not to copy. |
| 4 | **Concept + script** | `references/routing.md` §Story | 3 concepts → pick → `SCRIPT.md` (picture · exact VO · on-screen text · sound). AI ad films: run Direct module (AI Director) stages 0–3. | **Gate 2:** script approved; lines copied to `scenes.json`. |
| 5 | **Scene plan + engine** | `references/remotion.md`, `references/hyperframes.md`, `references/openmontage.md` | Kinds, copy, media per scene. Present Remotion **and** HyperFrames (and OpenMontage if relevant) with a recommendation; templated vs atelier mode. | **Gate 3:** engine + mode logged in `DECISIONS.md`. |
| 6 | **Voice** | `references/voice.md` | Clone once (`voice.py clone`), sample one line, then `voice.py generate --scenes scenes.json --brand brand/brand.json`; `transcribe_words.py vo/ --script scenes.json` | **Gate 4a:** sample approved before the batch. `vo/*.wav` + `*.words.json`. |
| 7 | **Assets** | `references/openmontage.md`, `references/assets.md` | Real footage first; then generated/stock via OpenMontage or Direct module (AI Director)/Higgsfield; music + SFX. Log every file: `ledger.py add`. Announce each paid call (tool, provider, model, sample/batch, est. $). | **Gate 4b:** sample before batch; ledger complete. |
| 8 | **Footage edit** (talking head / footage-led) | `references/herk-edit-kit.md` | transcribe → `cut-silences` → `cut-mistakes` (user reviews candidates) → lock `edit/clean.mp4` + retimed transcript. | Cut locked. Never use raw-timeline times on the edited video. |
| 9 | **Lock the clock** | `references/captions-audio.md` | `python scripts/timeline_from_vo.py scenes.json --remotion remotion --hyperframes hyperframes` | `timeline.master.json`, `timeline.md`, captions on the master clock. |
| 10 | **Compose** | engine reference | Remotion: data files feed `templates/remotion-brand`; edit scenes in `src/scenes/`. HyperFrames: `hf_build.py` (templated) or hand-author (atelier). Open Studio/preview and give the user the link. | **Gate 5:** preview approved. Never render finals because lint passed. |
| 11 | **Captions** | `references/captions-audio.md` | Burned-in from the engine; sidecars with `captions_convert.py --to srt/vtt/ass`. | Words match audio within ~2 frames; brand spellings right. |
| 12 | **Mix + master** | `references/captions-audio.md` | `python scripts/audio.py mix --timeline timeline.master.json --music … --sfx audio/sfx.json --out audio/master.wav` (or herk `mix.mjs`, or the audio director skill for problem mixes) | Measured at target LUFS / true peak. |
| 13 | **Drafts → QA → finals** | `references/qa-delivery.md` | `render_matrix.py variants.json --draft` → show → on approval `render_matrix.py variants.json` (renders muted, muxes master, runs `qa_check.py`). Open the contact sheets and cut strips with Read. | **Gate 6:** drafts approved. `delivery/manifest.json` all PASS. |
| 14 | **Finish + versions** (optional) | `references/pireel.md`, `references/qa-delivery.md` | Pireel for human touch-ups/variants; `reframe.py` only as a fallback; localisation via VoiceStudio dub or OpenMontage `localization-dub`. | `VERIFY.md` ticked from evidence. |

## Routing at a glance

Full recipes (exact steps per route) are in `references/routing.md`.

| Ask | Route | Primary engines |
|---|---|---|
| Brand film / promo with VO, supers, end card | **Narrated brand film** | VO (Voicebox/VoiceStudio) → Remotion brand template or HyperFrames |
| Product launch from a URL / website | **Site-to-video** | `hyperframes capture` → `/product-launch-video` workflow, brand tokens |
| Explainer (faceless, data, teacher) | **Explainer** | OpenMontage `animated-explainer` (or HF `/faceless-explainer`) with brand playbook + local VO |
| Founder / talking-head video | **Talking head** | herk chain → overlays (HyperFrames cards or Remotion) → captions → mix |
| Reels/Shorts/TikTok from long footage | **Short-form** | herk `short-form-edit` or OpenMontage `clip-factory` / `podcast-repurpose` |
| Hyper-real AI ad / brand story | **AI ad film** | Direct module (AI Director) (Higgsfield) for plates → this pipeline for text layer, VO, mix, versions |
| Logo sting / showreel / motion-only (<30 s) | **Motion piece** | herk `motion-showreel` or HF `/motion-graphics`, registry `logo-sting` blocks |
| Many personalised or data-driven versions | **Batch** | Remotion `--props` / Lambda or HF `render --batch rows.json` via `render_matrix.py` |
| Same video in other languages | **Localisation** | VoiceStudio dubbing or OpenMontage `localization-dub` → re-time captions → re-render |
| Screen demo / app walkthrough | **Screen demo** | OpenMontage `screen-demo` (real or synthetic terminal) + brand overlays |
| Avatar / spokesperson | **Avatar** | OpenMontage `avatar-spokesperson` (HeyGen/Kling/SadTalker), with consent |
| Podcast → audiogram / clips | **Podcast** | OpenMontage `podcast-repurpose`, captions, brand frame |
| Edit/finish existing footage by hand | **Finishing** | Pireel (local editor; hosted for agent control) |

## Choosing the composition engine

Present both and recommend one; log the choice (OpenMontage's hard rule, and good practice).

- **Remotion** when: the film is data-driven or personalised, you need typed props/zod schemas, React components, Lambda-scale rendering, precise frame math, `@remotion/captions`, 3D/Lottie/Skia, or the user already has Remotion work (the Direct module (AI Director) starter is Remotion). Licence check first.
- **HyperFrames** when: speed of authoring matters, the look is motion-graphics/editorial, you want registry blocks (charts, logo stings, caption styles, shader transitions), website capture, `--batch` variables, or the user wants Apache-2.0. Authoring is HTML/CSS/GSAP in seconds-based time.
- **Both** in one film is fine: render overlays from one as transparent video (`--format webm`/`mov` in HF; ProRes 4444 or VP9 alpha in Remotion) and composite (`references/interop.md`).
- **OpenMontage** wraps both: use it when the job needs research, provider selection, generation and cost control across many assets, and drive its pipelines by its own rules (`references/openmontage.md`).

## Hard rules

1. **One brand source of truth.** Colours, fonts, logo, motion, caption and loudness values come from `brand/brand.json` via `brand_tokens.py`. Never hand-type a hex or font into a scene.
2. **AI never draws text or logos.** All supers, UI, numbers, signage and end cards are Remotion/HyperFrames layers. Logos are the official files (hash in `brand/tokens/provenance.json`); if none exists, use the name in the brand font.
3. **One promise per film**, ≤2 proofs, one focal point per frame, one transition family per film. Every scene has one job (orientation, comprehension, belief, recall, feeling, action).
4. **One clock.** Lock the cut or the VO, then derive all timing (scenes, captions, beats, SFX) from word timestamps via `timeline_from_vo.py`. Change inputs and re-run; never nudge times by hand downstream.
5. **Deterministic compositions.** No `Math.random`/`Date.now`/render-time fetches/CSS transitions/`repeat:-1`. Remotion: pure function of the frame, `random(seed)`. HyperFrames: one paused timeline per composition, registered synchronously.
6. **Preview before render; drafts before finals.** Never render finals because a linter passed. Show the Studio/preview link or draft and wait.
7. **Gates end the turn.** Brief, script, engine, voice sample, asset sample, preview, drafts. Approvals go in `DECISIONS.md` (append-only).
8. **Announce every paid call** (tool · provider · model · why · sample or batch · est. cost) and ask before switching provider/model/engine, dropping narration or music, or going from sample to batch. No silent substitutions.
9. **Licences are part of the brief.** Remotion Company License for teams of 4+; OmniVoice/other NC weights never in commercial work; stock/music/SFX licences logged in the ledger; AGPL tools run unmodified locally.
10. **Voices need consent.** Clone only voices with written consent on file; never put a synthetic voice over footage of a real person talking; disclose AI voice/visuals where platforms require it.
11. **Real before generated.** Prefer real footage and screen recordings, then labelled UI mocks, then AI video. An AI still with a push-in is not B-roll. Each B-roll scene appears once per reel.
12. **Measure, don't assume.** ffprobe every file, measure loudness on the final encode, open contact sheets and cut strips with Read, re-transcribe the final audio against the script. Don't claim to hear audio.
13. **Raw media is read-only.** Every stage writes a new file; outputs go beside their sources in the project folder.
14. **Secrets stay in `.env`.** Never ask for API keys in chat or print them; `doctor.py` reports only presence.
15. **Claims and compliance.** Numbers need a source or approval note; financial/medical/legal language gets flagged; third-party brands are fictionalised unless permission exists.
16. **Never claim media you didn't make.** If a step (Higgsfield, hosted Pireel, a paid API) can't run from this session, deliver prompts, files and exact commands, and say plainly it's the user's step.

## Scripts (all print what they wrote; all take `--help`)

| Script | Does |
|---|---|
| `doctor.py` | Checks Node/FFmpeg/Python/uv/pnpm/Docker, Voicebox + VoiceStudio APIs and profiles, toolchain clones, which API keys exist (names only), and which routes are ready. |
| `new_project.py` | Scaffolds a project folder (brief/script/decisions/verify, scenes/variants, Remotion + HyperFrames starters) and runs `brand_tokens.py`. |
| `brand_tokens.py` | brand.json → Remotion `brand.json`, HyperFrames `brand.css` + `frame.md`, OpenMontage style playbook, Pireel frame, `BRAND.md`, caption style, provenance hashes, contrast report. |
| `voice.py` | `health · list · clone · generate` against Voicebox or VoiceStudio (per-scene WAVs + `vo/manifest.json`, brand lexicon, seeds, licence guard). |
| `transcribe_words.py` | Word timestamps via VoiceStudio (WhisperX), faster-whisper, HyperFrames, OpenAI or ElevenLabs; script-spelling alignment. |
| `timeline_from_vo.py` | Locks the master clock from VO lengths; feeds Remotion and HyperFrames; master captions. |
| `captions_convert.py` | Transcript → SRT, VTT, ASS (brand karaoke), Remotion `Caption[]`, HyperFrames transcript, caption groups. |
| `hf_build.py` | Templated HyperFrames composition (scene + caption sub-compositions, local GSAP, audio) per aspect. |
| `audio.py` | `measure · mix · normalize · mux`: VO placement, music bed under voice with sidechain duck, SFX, two-pass loudnorm. |
| `render_matrix.py` | Renders every variant (Remotion / HyperFrames / file), muxes the master mix, runs QA, writes `delivery/manifest.json`. |
| `qa_check.py` | Size, fps, duration, pixel format, faststart, audio, LUFS/true peak, black/frozen/silence, contact sheet, cut strips. |
| `reframe.py` | Fallback aspect conversion (crop with focus, blurred fill, brand pad). |
| `ledger.py` | Asset provenance, licence, cost, AI flag, duplicate-use check. |
| `shots_to_scenes.py` | Direct module (AI Director) `shots.json` → `scenes.json`. |

## Working in Cowork

- The user's files, Node, FFmpeg and local voice apps live on **their computer**. Run project work there with `device_bash` inside the connected folder; Voicebox (17493) and VoiceStudio (3900) are reachable only from that machine, never from the cloud container.
- Use the cloud container only for what the computer can't do (viewing frames/PDFs with Read, a tool that won't install locally). Stage only those files.
- Long renders: split into steps under the shell time limit (draft per variant; `HYPERFRAMES_RENDER_DETACHED=1` for HyperFrames; Remotion `--frames` ranges), or give the user the exact command to run.
- Deliverables land in the project folder; tell the user the folder and file names. Keep chat short: what was made, what's needed from them.

## Output formats

State the format in the first line. Brief (`BRIEF.md`), script table (`SCRIPT.md`), scene plan (`scenes.json` + `timeline.md`), decision log, preview link, draft set, delivery set with `manifest.json` + `VERIFY.md`, or an audit (of a cut, a mix, a composition): what works, what breaks, the fix with exact values.
