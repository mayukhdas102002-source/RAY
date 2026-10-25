# Production OS: projects, gates, files and handoffs

## Project folders

Scaffold every job with `python scripts/ray.py new "<folder>" --kind person|brand|org --playbook <id> [--brand <kit>] [--engine remotion|hyperframes|both|none] [--film]`. It wraps `modules/produce/scripts/new_project.py`, adds the playbook checklist to `00_START_HERE.md`, and with `--film` (or AI-film playbooks) adds the Direct module's treatment, shot card, prompt pack and client write-up templates under `direction/`.

```
<Client or Person> - <Project>/
├── 00_START_HERE.md         status, gates, playbook checklist, open items
├── BRIEF.md  SCRIPT.md  DECISIONS.md  VERIFY.md
├── scenes.json              scene list (copy, VO lines, kinds, media, durations)
├── variants.json            one row per deliverable
├── direction/               (films) treatment.md, shots.json, prompt-pack.md, shot cards, client-shot-by-shot.md
├── brand/                   brand.json + logo/ + fonts/ + tokens/ (generated)
├── refs/                    reference media + REFERENCE-ANALYSIS.md
├── raw/                     untouched source footage/audio (read-only)
├── prompts/                 every generation prompt, one file per shot
├── assets/{images,video,music,sfx}/ + ledger.json
├── vo/                      per-scene WAVs + manifest.json + *.words.json
├── edit/                    talking-head cut outputs (EDLs, clean.mp4, retimed transcript)
├── captions/                master words, SRT/VTT/ASS
├── audio/                   sfx.json, master.wav, stems
├── remotion/ hyperframes/   composition projects (one HyperFrames project per aspect)
├── renders/drafts/          drafts + QA sheets
└── delivery/                finals + manifest.json + sidecars + stills
```

Reusable kits live in `<workspace>/_brands/<name>/` (brand.json, logo/, fonts/, voice reference + consent). Toolchain clones (OpenMontage, herk-edit-kit, Pireel) live in `<workspace>/_toolchain/` (env `BVP_TOOLS`).

## Gates by mode

| Gate | Quick | Standard | Full |
|---|---|---|---|
| 1 Brief approved (`BRIEF.md`) | plan confirmed in chat | ✓ | ✓ |
| 2 References read + concept chosen | – | if refs given | ✓ (3 concepts → 1) |
| 3 Script approved (`SCRIPT.md`) | – | ✓ | ✓ |
| 4 Look/brand lock (kit, tokens, look tokens, reference sheets) | – | kit only | ✓ |
| 5 Engine + mode decision logged | – | ✓ | ✓ |
| 6 Samples (voice line, 1–2 generated shots) before batch | – | if paid | ✓ |
| 7 Preview approved (Studio/preview link or animatic) | – | ✓ | ✓ |
| 8 Drafts approved | show final | ✓ | ✓ |
| 9 Finals QA'd + `VERIFY.md` | ✓ | ✓ | ✓ |
| 10 Client write-up / handover | – | optional | ✓ |

A gate ends Ray's turn until the person answers. Pre-authorisation ("do it all, don't ask") is logged once in `DECISIONS.md` as `approval_policy`; paid batches above the stated budget still need a yes.

## Decisions and spend

`DECISIONS.md` is append-only: route, mode, playbook, engine, voice, music, providers/models, claims, approvals, capability extensions. Paid calls get a row in the spend table (tool · model · sample/batch · estimate · actual · approved by). Assets get a ledger row (`ray.py tool ledger add …`).

## The two scene formats and the bridge

- **Direct module** (films): `direction/shots.json` — shot id, timing `t:[start,end]`, maker (AI / Remotion / effect), model, keyframe and motion prompts, sound, text layer.
- **Produce module** (everything rendered): `scenes.json` — scene id, kind, copy, `vo_text`, media, durations.
- Bridge: `ray.py tool shots_to_scenes direction/shots.json --out scenes.json --media-dir assets/video` once plates exist. Keep shot ids stable (S05a/S05b, never renumber).

## The master clock

`ray.py tool timeline_from_vo scenes.json --remotion remotion --hyperframes hyperframes` after every VO or cut change. Outputs `timeline.master.json` and `timeline.md`; Remotion/HyperFrames, captions, the mix and QA all read it.

## Naming and versions

`<Owner>_<Title>_<aspect>_<lang>_v<N>.<ext>` for deliverables (`Acme_SpringLaunch_9x16_en_v3.mp4`), sidecars with the same stem. Drafts carry `draft`. Never overwrite a delivered version: bump `vN`. Prompts: `prompts/<shot>_<model>_v<N>.txt`.

## Handover pack

`delivery/` (finals, SRT/VTT, end-card and thumbnail stills, `manifest.json` with hashes and QA verdicts), `VERIFY.md`, `DECISIONS.md`, the asset ledger, and for clients a two-minute shot-by-shot (`modules/direct/templates/client-shot-by-shot.md`). Tell the person the folder and the file names.

## Running in limited environments

| Missing | Ray still delivers |
|---|---|
| Node/FFmpeg on the machine | Brief, script, shot list, prompt pack, storyboards, exact install + render commands |
| Voice apps | Script with delivery notes; HyperFrames Kokoro or OpenMontage Piper scratch VO; or the person records |
| Higgsfield / video-gen connectors | Prompt pack with model choice, generate/keep lengths, tokens; animatic from keyframes |
| Time-limited shell | One variant per call; HyperFrames detached renders; Remotion `--frames` ranges |
