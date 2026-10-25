> **RAY module.** This folder is part of RAY (`../../SKILL.md`). Its `SKILL.md` is renamed `MODULE.md` so it doesn't register as a separate skill; install RAY, not this folder. Standalone install notes below are kept for reference.

# AI Director

A master skill for making production-grade, hyper-real AI ad films on **Higgsfield**, with **Remotion** handling every screen, super and end card. It covers the whole job, from brief to reference teardown, concept, shot list, keyframes, motion, edit, finish and client write-up.

## Folder map

```
AI Director/
├── SKILL.md                  ← start here (the pipeline, hard rules, routing)
├── director/                 ← the method, one file per stage (01–11)
├── templates/                ← treatment, shot card, prompt pack, client shot-by-shot,
│   └── remotion-starter/       logline sheet, shots.json schema, working Remotion project
├── tools/                    ← ffmpeg teardown helpers (cut log, contact sheet, keyframes)
├── examples/                 ← Homely "Going Up" package, loglines, Zillow teardown
├── library/
│   ├── visual-skills/        ← CC BY 4.0 · dramaturgy, universal rules, Seedance/Kling/Veo, image craft
│   └── higgsfield/           ← MIT · Higgsfield models, specs, Seedance 2.0/2.5, acting, audio, troubleshooting
├── LICENSES/
└── CREDITS.md
```

## Install

- **Claude (Cowork / claude.ai):** add it as a skill. Zip the `AI Director` folder with `SKILL.md` at the top level of the zip and upload it in Settings → Capabilities → Skills, or save it from the skill card.
- **Claude Code:** copy the folder to `~/.claude/skills/ai-director/`.
- **Remotion starter:** `cd templates/remotion-starter && npm install && npx remotion studio` (Node 18+).
- **Tools:** need `ffmpeg` and `python3`. On Windows, use WSL or Git Bash.

## Use

Ask things like:
- "Tear down these reference ads and pitch five loglines for our home-loan app."
- "Turn concept 2 into a 45-second shot list with Higgsfield model allocation."
- "Write keyframe and motion prompts for S07 on Kling 3.0."
- "Build the Remotion animatic from this shots.json."
- "Write the client shot-by-shot for this film."

## Credits

See `CREDITS.md`. It includes material by Serge Shima (CC BY 4.0) and O-Side Media (MIT), and techniques studied from the higgsfield-seedance2-jineng collection.
