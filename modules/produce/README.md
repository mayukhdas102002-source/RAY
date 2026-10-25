> **RAY module.** This folder is part of RAY (`../../SKILL.md`). Its `SKILL.md` is renamed `MODULE.md` so it doesn't register as a separate skill; install RAY, not this folder. Standalone install notes below are kept for reference.

# Master Brand Video Pipeline

A Claude skill that runs brand video production end to end by orchestrating seven open-source tools — **Remotion, HyperFrames, OpenMontage, herk-edit-kit, Pireel, Voicebox and VoiceStudio** — with one brand kit, one clock, gated approvals and measured QA. It works alongside the Direct module (AI Director), Read module (vidreader) and Audio module skills in this folder.

## Folder map

```
master-brand-video-pipeline/
├── SKILL.md                    ← start here: toolchain, pipeline stages + gates, routing, hard rules, scripts
├── references/
│   ├── setup.md                install + Windows notes for every tool, versions
│   ├── routing.md              intake, references, story, 13 recipes (brand film, site-to-video, explainer,
│   │                           talking head, short-form, AI ad film, motion piece, batch, localisation…)
│   ├── brand-system.md         brand.json schema and what each engine receives
│   ├── remotion.md             starter, CLI, authoring rules, Lambda, porting
│   ├── hyperframes.md          contract, CLI, registry, workflows, gotchas
│   ├── openmontage.md          pipelines, operating rules, brand/voice integration, budget
│   ├── herk-edit-kit.md        silence/mistake cutting, overlays, reels, showreels
│   ├── voice.md                Voicebox + VoiceStudio: cloning, APIs, licences, MCP
│   ├── captions-audio.md       master clock, captions, mix and loudness
│   ├── assets.md               footage, AI generation, stock, music, SFX, ledger
│   ├── pireel.md               finishing/variants editor (local vs hosted)
│   ├── qa-delivery.md          drafts → finals, QA checklist, aspects, naming, disclosure
│   └── interop.md              file contracts and conversions between tools
├── scripts/                    stdlib Python 3.10+ (FFmpeg + Node 22 where noted)
│   ├── doctor.py  new_project.py  brand_tokens.py  voice.py  transcribe_words.py
│   ├── timeline_from_vo.py  captions_convert.py  hf_build.py  audio.py
│   └── render_matrix.py  qa_check.py  reframe.py  ledger.py  shots_to_scenes.py  _common.py
└── templates/
    ├── brand.example.json      the brand kit schema, filled with an example
    ├── project/                BRIEF, SCRIPT, DECISIONS, VERIFY, START_HERE, scenes.json, variants.json, sfx
    ├── remotion-brand/         Remotion 4.0.537 brand film: 4 aspects, scenes, captions, VO, music ducking, end card
    ├── hyperframes-brand/      HyperFrames project shell + an example lower-third sub-composition
    └── openmontage/            local_voice_tts.py: Voicebox/VoiceStudio TTS providers for OpenMontage
```

## Install the skill

- **Cowork / claude.ai:** zip this folder with `SKILL.md` at the top level and add it in Settings → Capabilities → Skills (or save it from a skill card).
- **Claude Code:** copy the folder to `~/.claude/skills/master-brand-video-pipeline/`.

## Quick start

```bash
python scripts/doctor.py --tools-dir "<AI Production>/_toolchain"
python scripts/new_project.py "<AI Production>/Homely - Spring Rates" --brand "<AI Production>/_brands/homely" --engine both
cd "<AI Production>/Homely - Spring Rates"
# fill BRIEF.md, SCRIPT.md, scenes.json, then:
python <skill>/scripts/voice.py generate --scenes scenes.json --brand brand/brand.json
python <skill>/scripts/transcribe_words.py vo/ --script scenes.json
python <skill>/scripts/timeline_from_vo.py scenes.json --remotion remotion --hyperframes hyperframes
cd remotion && npm install && npx remotion studio            # or: python <skill>/scripts/hf_build.py hyperframes
python <skill>/scripts/audio.py mix --timeline timeline.master.json --music assets/music/bed.wav --out audio/master.wav
python <skill>/scripts/render_matrix.py variants.json --draft   # then finals after approval
```

Ask Claude things like: "Make a 30-second Homely brand film for Reels and YouTube with our cloned voice", "Cut this founder interview into a 60-second reel with captions", "Turn homely.co.nz into a product launch video", "Render 40 personalised versions from this CSV", "Set up OpenMontage with our Voicebox voice".

## Tested

Scaffold → brand tokens → timeline → Remotion render (9:16, 1:1) → HyperFrames build, lint (0 errors) and render → mix to −14 LUFS → mux → QA → render matrix with manifest, run end to end on Linux with Node 22 and FFmpeg 6 (Oct 2026). Voicebox/VoiceStudio calls follow their source code but were not exercised against running apps.

See `CREDITS.md` for upstream projects and licences.
