# Higgsfield with Ray

Higgsfield is the person's AI video/image platform (Seedance, Kling, Veo, Minimax, Wan, Nano Banana, GPT Image, Soul ID, Marketing Studio, Cinema Studio, Effects and more). Ray's Direct module already holds the craft and model knowledge (`modules/direct/library/higgsfield/`); this file is how Ray **executes** through whatever Higgsfield surface is present.

The authoritative coexistence guide is `modules/direct/library/higgsfield/skills/higgsfield-stack/GUIDE.md` (surfaces, preflight, bundled workflows, detection, handoff wording). Read it before the first Higgsfield call in a job. Model limits: `modules/direct/library/higgsfield/specs/`.

## Surfaces and how to tell which one is attached

| Surface | Signals | Use when |
|---|---|---|
| **MCP connector** (`https://mcp.higgsfield.ai/mcp`) | Session tools such as `models_explore`, `generate_image`, `generate_video`, `balance`, `transactions`, `media_upload_widget`, `media_import_url`, `list_voices`, `show_marketing_studio`, `get_workflow_instructions` | claude.ai web / desktop / Cowork sessions |
| **CLI** (`higgsfield`, `higgs`, `hf`) | `which higgsfield` on the person's machine (`ray.py doctor` reports it) | Terminal sessions on the person's computer (Higgsfield recommends the CLI there) |
| **Bundled skills** (`higgsfield-ai/skills`) | `/higgsfield:*` skills installed | Their workflows: generate, soul-id, product photoshoot, brandkit, thumbnails… |
| **None** | — | Ray delivers a prompt pack for higgsfield.ai and offers to connect |

To connect the MCP: claude.ai or the desktop app → Settings → Connectors → Add custom connector → `https://mcp.higgsfield.ai/mcp` → sign in. Then enable it for the chat.

## Ray's generation flow (MCP)

1. **Direct first.** Shot list, look lock and per-shot prompts come from the Direct module (`director/04`–`06`, model guides in the library). Tokens pasted verbatim; screens blank; no text in frame.
2. **Schema check** for each model you'll call: `models_explore(action="get", model_id=…)` → durations, aspect ratios, modes, media roles. Never pass parameters the schema doesn't list.
3. **Balance + quote:** `balance`, then the generate call with `get_cost: true` (no job submitted) for the planned shot; multiply by expected takes (`production-benchmarks.md` acceptance rates). Present: model · shot · settings · cost per take · planned takes · total → **G**.
4. **References in:** local files via `media_upload_widget` (the remote connector can't read chat attachments) or `media_import_url` for web media; keep returned media ids in `prompts/<shot>.json`.
5. **Sample:** one take of the hero shot (cheaper model/resolution for drafts where sensible). Review frames (download → `ray tool frames` → Read) against the realism checklist (`modules/direct/director/09-realism-checklist.md`) → **G**.
6. **Batch** approved shots; poll job status as the tool describes; download results into `assets/video/<shot>_<model>_t<N>.mp4`.
7. **Log:** `ray tool ledger add assets/video/S04_kling_t2.mp4 --source generated --provider higgsfield --model "Kling 3.0" --prompt-file prompts/S04.txt --task-id <id> --cost <credits→$> --scene S04 --use 1.2-4.0`.
8. **Keep the cleanest 2–3.5 s**; hand plates to the Produce module (`shots_to_scenes` → Remotion text layer, VO, mix, versions).
9. **Spend summary** in `DECISIONS.md` (credits used, takes per shot, acceptance rate).

## Higgsfield's own workflows

When a request is squarely one of the connector's bundled workflows (ad multiplier, character sheet, thumbnails, UGC-style videos, faceless video, narrator, product photoshoot, brand assets, subtitles, video editing), load it with `get_workflow_instructions` and follow it, feeding it what Ray's craft layer produced (character, hook, style laws, audio plan). Map: `higgsfield-stack/GUIDE.md` § Higgsfield's bundled workflows. Ray still owns brand compliance, text/logo layers, the mix, captions and QA.

## What stays outside Higgsfield

- All on-screen text, UI, logos and end cards (Remotion/HyperFrames).
- Final mix and loudness (Produce `audio.py`, Audio module).
- Captions (word-timed from the final audio).
- QA and delivery manifests.
- Consent checks for any real person's likeness or voice (Soul ID and voice cloning only for consenting people).

## No connector? Prompt-pack mode

Deliver `direction/prompt-pack.md` (`modules/direct/templates/prompt-pack.md`): per shot the model, keyframe prompt (start/end if needed), motion prompt, generate length vs keep length, references to attach, and the tokens block. Add the Seedance lint tip when relevant. Say plainly that generation is the person's step, then continue with everything else (animatic, text layer, VO, music) so the plates drop straight in.
