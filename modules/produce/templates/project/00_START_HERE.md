# {{TITLE}}

Made with the **master-brand-video-pipeline** skill. Started {{DATE}}.

## Where things are
| Folder / file | What |
|---|---|
| `BRIEF.md` → `SCRIPT.md` → `scenes.json` | The idea, the words, the scene list (gates 1 and 2) |
| `DECISIONS.md` | Append-only log: route, engine, voice, music, paid calls, approvals |
| `brand/brand.json` + `brand/tokens/` | Brand kit and the tokens generated for every engine |
| `vo/` | Voiceover per scene + `manifest.json` + `*.words.json` word timings |
| `timeline.master.json`, `timeline.md` | The locked master clock (re-run `timeline_from_vo.py` after any VO change) |
| `captions/` | Master word file, SRT/VTT/ASS exports |
| `raw/` | Untouched source footage (never edit in place) |
| `edit/` | Talking-head cut outputs (silence/mistake EDLs, clean.mp4, retimed transcript) |
| `assets/` + `assets/ledger.json` | Images, video, music, SFX with provenance |
| `remotion/` · `hyperframes/` | Composition projects |
| `audio/master.wav` | Final mix at the delivery loudness |
| `renders/drafts/` → `delivery/` | Drafts for review → approved finals + `manifest.json` |
| `VERIFY.md` | Evidence that it's actually finished |

## Status
- [ ] Gate 1 · Brief approved
- [ ] Gate 2 · Script approved
- [ ] Gate 3 · Scene plan + engine choice approved
- [ ] Gate 4 · Voice/assets approved (sample before batch)
- [ ] Gate 5 · Preview approved (Studio / preview link)
- [ ] Gate 6 · Drafts approved
- [ ] Finals rendered, QA'd, delivered

## Open items
-
