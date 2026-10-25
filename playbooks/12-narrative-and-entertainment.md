# 12 · Narrative and entertainment

Story-first work: short films, branded entertainment, music videos, trailers and teasers, episodic series, character-led pieces, animation and AI films.

## Formats

| Format | Length | Notes |
|---|---|---|
| Short film / branded short | 1–15 min | Script, characters, scenes, sound design, score |
| Music video | song length | Performance + narrative/concept, cut to the track |
| Trailer / teaser | 30–150 s / 10–30 s | Hook, world, stakes, escalation, title, date |
| Series episode | 1–10 min | Recurring cast/look/format bible |
| Character piece / mascot | 15–90 s | Character sheet, voice, consistent rig or Soul ID |
| Animation | any | 2D (SVG/GSAP rigs), motion design, stylised AI |

## Intake extras

Logline, genre and tone references, cast (real actors with releases vs AI characters), world and look, music (licensed/commissioned), runtime, distribution (festival, YouTube, social, internal).

## Workflow

1. **Logline + premise** (Direct `03`): one sentence: who wants what, what stands in the way, what changes. 3 options → **G**
2. **Beat sheet / script:** acts, scenes, turning points; dialogue sounds like people; screenplay format in `direction/script.md` for anything with dialogue. → **G**
3. **Bible:** characters (tokens + reference sheets, Soul ID/character design guides in `modules/direct/library/higgsfield/skills/higgsfield-soul|higgsfield-character-design`), locations/sets, look (lens, light, grade, grain), sound world. → **G** (look lock)
4. **Shot list + storyboard:** `direction/shots.json`, one keyframe per shot (Direct `05`); dialogue timing (`higgsfield-seedance-vfx/references/dialogue-timing.md`); animatic with scratch VO (`boards_from_edit.py`, Remotion animatic). → **G**
5. **Production:** live-action shoot and/or AI generation per shot with model allocation (Direct `06`): hero shots on the best model, acting shots on acting-strong models, drafts cheap first. Sample → **G** → batch; ledger every take.
6. **Voices:** actors, or consented cloned voices; dialogue lip-sync tools only with consent; ADR lines via `voice.py`.
7. **Edit:** assemble on the animatic timeline; cut for performance and rhythm; carry sound across cuts.
8. **Sound:** dialogue edit, ambience beds per location, Foley/SFX, score (commissioned/licensed/generated with rights), mix (Audio module), −14 LUFS web or festival/broadcast spec (often −24 LKFS/−23 LUFS with 5.1/stereo deliverables).
9. **Titles & credits** in Remotion/HF (never AI-drawn), grade, grain, QA, realism audit for AI shots.
10. **Trailers/teasers/clips** from the finished film (`playbooks/03-social-short-form.md`).

## Music videos

Analyse the track (BPM, sections, energy curve: Audio module + `music-grid.mjs`), map sections to visual chapters, performance shots cut on downbeats, concept shots on phrases; lyric-synced moments from the vocal transcript; artist approval at treatment and rough cut.

## Trailers

Structure: cold open image → world → protagonist + want → obstacle → escalation montage (beat-cut) → button moment → title card → date/CTA. Never spoil the ending; use the best 2–3 lines of dialogue only.

## Craft rules

- Characters consistent across shots (tokens pasted verbatim, reference sheets attached every time).
- Performances: micro-expressions and eye life (Higgsfield acting/FACS guides); avoid "AI stare".
- Shots breathe; generate long, cut short; one camera move per shot.
- Real people are never deepfaked; AI characters are original; no lookalikes of celebrities or existing characters.

## Deliverables

Film master(s), trailer/teaser, clips, subtitles, credits list, music cue sheet, licences/releases, prompt pack + ledger for AI shots, festival/broadcast specs if needed.
