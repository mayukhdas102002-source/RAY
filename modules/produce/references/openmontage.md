# OpenMontage: the agentic production system

OpenMontage (`calesthio/OpenMontage`, AGPL-3.0) has no orchestrator binary: **you** are the orchestrator. It gives you YAML pipeline manifests, stage-director skills, ~100 Python tools behind a registry, 60+ providers, a budget governor, checkpoints and a review board. Use it when a job needs research, provider choice, many generated/stock assets, or one of its specialist pipelines.

## Operating contract (from its AGENT_GUIDE.md: read it in the clone before the first run)

1. **Rule Zero:** all production goes through a pipeline. Pick a manifest in `pipeline_defs/`, read it, run preflight, and for each stage read `skills/pipelines/<pipeline>/<stage>-director.md` first, plus the Layer-3 vendor skills (`.agents/skills/<vendor>`) named by each tool's `agent_skills` before calling it. No ad-hoc scripts that call tools directly; the exception is `skills/meta/capability-extension.md` (idempotent scripts in `projects/<p>/scripts/`, logged as `capability_extension`).
2. **Announce before paying:** tool, provider, model, why, sample vs batch. Ask before switching provider/model/still-vs-motion/composition engine, dropping narration or music, or sample → batch. No substitutions. Blockers reported as: attempted · failed · class (auth/access/bug/quality) · options · recommendation.
3. **Present both runtimes** (Remotion and HyperFrames) and log `render_runtime_selection` with both in `options_considered`.
4. **Composition mode:** `templated` (stock scene types) or `atelier` (bespoke; default for hero/brand/launch: route through `skills/meta/taste-direction.md` then `bespoke-composition.md`, finish with a distinctness review).
5. **Motion-required briefs** (trailers, teasers, avatar) never fall back to stills/Ken Burns silently.
6. **Music plan at proposal:** `music_library/` → music search → music generation → bring-your-own → none.
7. **Gates are binding:** write the checkpoint as `awaiting_human` and end the turn. Writing a gated stage `completed` without `human_approved=True` raises GATE VIOLATION. Pre-authorisation = a `decision_log` entry, `category: "approval_policy"`.
8. `decision_log` is append-only.

## Pipelines (`pipeline_defs/*.yaml`)

| Pipeline | Use for | Stages (G = gated) |
|---|---|---|
| `animated-explainer` (production) | Data/teacher explainers, motion graphics | research · proposal G · script G · scene_plan G · assets G · edit · compose · publish G |
| `animation` / `cinematic` (production) | Kinetic/animated pieces; trailers, teasers, brand cinematics | same |
| `character-animation` (beta) | SVG-rig characters with GSAP | + character_design G, rig_plan |
| `avatar-spokesperson`, `hybrid` (production) | Presenter/avatar videos; footage + support graphics | idea G · script G · scene_plan G · assets G · edit · compose · publish G |
| `screen-demo` (production) | Product/app walkthroughs (`real_capture` or `synthetic_terminal`) | same |
| `talking-head` (beta) | Face-cam edits | same |
| `clip-factory`, `podcast-repurpose` (beta) | Many shorts from long content; audiograms | same |
| `localization-dub` (beta) | Translated/dubbed versions | same |
| `documentary-montage` (beta) | Real-footage montage from archives/stock (CLIP-indexed corpus) | idea G · scene_plan G · assets G · edit G · compose |

Stage chain: `research → proposal → script → scene_plan → assets → edit → compose → publish` (footage-led pipelines start at `idea`).

## Running it

```bash
cd "<toolchain>/OpenMontage" && source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.provider_menu_summary(), indent=2))"
# show the user "X of Y configured" per capability, plus composition_runtimes and setup_offers
python -c "from lib.checkpoint import init_project; init_project('homely-spring-rates', title='Spring Rates', pipeline_type='animated-explainer')"
python -m backlot open homely-spring-rates        # review board (filmstrip, decisions, costs); optional
```
Tools are called as `ToolClass().execute({...})` → `ToolResult(success, data, error, artifacts, cost_usd)`. Selectors (`tts_selector`, `image_selector`, `video_selector`) score providers (task fit 30, quality 20, control 15, reliability 15, cost 10, latency 5, continuity 5). Always pass explicit `output_path` under `projects/<id>/`.

Project workspace: `projects/<id>/` with `project.json`, `checkpoint_<stage>.json`, `artifacts/` (brief, script, scene_plan, asset_manifest, edit_decisions, render_report, final_review, decision_log…), `assets/{images,video,audio,music}`, `hyperframes/` (if HF runtime), `renders/final.mp4`. Override the root with `OPENMONTAGE_PROJECTS_DIR` (point it at the client project folder if you want everything in one place).

## Bringing the brand in

- **Style playbook:** copy `brand/tokens/openmontage-style.yaml` to `OpenMontage/styles/<brand>.yaml`; choose it at proposal. `lib/hyperframes_style_bridge.py` turns it into `:root` vars + DESIGN.md for HF; Remotion compositions read the playbook palette.
- **Voice (local, free, consistent):** copy `templates/openmontage/local_voice_tts.py` to `OpenMontage/tools/audio/`. Set `VOICEBOX_PROFILE` / `VOICESTUDIO_PROFILE` (and `VOICESTUDIO_ENGINE=voxcpm2`) in `.env`. The registry discovers `voicebox_tts` / `voicestudio_tts`; call `tts_selector` with `preferred_provider: "voicebox"`. Log a `capability_extension` decision. Alternative: generate WAVs with this skill's `voice.py` and register them in `asset_manifest.assets[]` (`type: audio`, `source_tool`, `provider`, `duration_seconds`).
- **Captions:** run OpenMontage's `transcriber` (WhisperX/faster-whisper) on the narration and pass `narration_transcript_path` to `video_compose` so its transcript-vs-script check runs. Word-level caption burn (`remotion_caption_burn`, `TalkingHead`) is **Remotion-only** inside OpenMontage.
- **Logo/end card:** add the official logo to the asset manifest; never let a generator draw it.

## Composition inside OpenMontage

- `video_compose` operation `render` routes on `edit_decisions.render_runtime` (`remotion | hyperframes | ffmpeg`). Remotion compositions in `remotion-composer/src`: `Explainer`, `CinematicRenderer`, `TalkingHead`, `TitledVideo`, `ProductReveal`, `CollageBurst`, `LyricOverlay`, `HeroTitle`, `EndTag`, `CaptionOverlayOnly`; cut types `text_card`, `stat_card`, `callout`, `comparison`, `hero_title`, `terminal_scene`, `bar_chart`, `line_chart`, `pie_chart`, `kpi_grid`, `progress_bar`…
- `hyperframes_compose`: `render`, `render_existing` (atelier index.html), `lint`, `validate`, `check`, `add_block`, `scaffold_workspace`.
- Gotchas: scene props are flat on the cut object; `kpi_grid.change` is a number; 4–6 s per scene, charts ≥4 s; `npx remotion render Explainer --props=… --output=…` (no entry file); in HF use known fonts, no `repeat:-1`, never `hyperframes init` from the pipeline, the npm package is `hyperframes`.

## Quality and cost

- Reviewer (`skills/meta/reviewer.md`): schema first, then review focus, playbook, taste profile, success criteria; severities critical/suggestion/nitpick; ≤2 rounds.
- Pre-compose: delivery-promise check, slideshow-risk score, `composition_validator` (missing files, narration longer than video, music shorter than video, bad cut times).
- Post-render `final_review`: ffprobe, 4 sampled frames, silence/clipping, promise preservation, subtitles, transcript-vs-script. Failing review = don't present.
- `config.yaml → budget`: `mode: observe|warn|cap` (default warn), `total_usd: 10`, `single_action_approval_usd: 0.50`, `require_approval_for_new_paid_tool: true`. Mirror paid calls in this project's `DECISIONS.md`.

## Providers (env vars in `OpenMontage/.env`; all optional)

Video: `FAL_KEY` (Kling, Veo, Seedance, MiniMax, Wan…), `KLING_API_KEY`, `RUNWAY_API_KEY`, `HIGGSFIELD_API_KEY`+`HIGGSFIELD_API_SECRET`, `XAI_API_KEY`, `HEYGEN_API_KEY`, `LTX_API_KEY`, `ARK_API_KEY`, `REPLICATE_API_TOKEN`, `COMFYUI_SERVER_URL`; local GPU via `VIDEO_GEN_LOCAL_ENABLED`. Images: FLUX/Imagen/GPT Image/Recraft/Ideogram (`IDEOGRAM_API_KEY`)… TTS: ElevenLabs, OpenAI, Google, Azure, Fish, Cartesia, Inworld, Piper (local). Music/SFX: `SUNO_API_KEY`, ElevenLabs, Lyria, Freesound, Pixabay, `MUSIC_LIBRARY_DIR`. Stock: `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `UNSPLASH_ACCESS_KEY` + free archives (Archive.org, NASA, Wikimedia, LOC…). Never hardcode providers; read `install_instructions` from the registry.

## Handing results back to this pipeline

Take `renders/final.mp4`, `artifacts/asset_manifest.json` (→ `ledger.py add` each asset with provider/model/prompt/cost), narration WAVs and transcripts. Re-mix with `audio.py` if the brand loudness target differs, then `render_matrix.py` (`engine: "file"` rows) for QA and the delivery manifest.
