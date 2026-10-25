# herk-edit-kit: talking-head cutting, overlays, reels and showreels

Nate Herk's agent editing kit on top of HyperFrames + GSAP (`nateherkai/herk-edit-kit` v2.0.0). Skills live in `.claude/skills/` (canonical; `.agents/skills/` is a Codex mirror). Projects live in `video-projects/<slug>/` (`npm run new-video -- <slug>`; 1920×1080 30 fps starter; run HyperFrames from inside the project folder). In Claude Code inside the clone: `/edit-video`.

You can run its scripts against a project in this pipeline's folder too: paths are arguments.

## Three timelines (never mix them)

`raw` (source) → `silenced` → `clean` (after mistake cuts). Approved cuts are on the **input** timeline of the step that applies them. Every transcript must match the video it describes; copy the final `*.mistakes-transcript.json` to the composition's `assets/transcript.json`. Raw-timeline times against the edited video is the classic bug.

Transcript format all tools read: `{"text": "...", "audio_duration_secs": 12.3, "words": [{"text":"Hello","start":0.2,"end":0.6}]}` (Scribe shape with `type` accepted; SRT/segment-only rejected; this skill's `transcribe_words.py` writes this shape).

## The long-form chain (`edit-video`)

1. **Probe** (`ffprobe`), copy the source into the project (raw stays untouched).
2. **Transcribe:** `node scripts/transcribe-elevenlabs.mjs raw.mp4 [--language en] [--no-diarize]` (ElevenLabs Scribe, word-level) **or** local: `python <skill>/scripts/transcribe_words.py raw.mp4` / `npx hyperframes transcribe raw.mp4 --model small.en`. Explain uploads/costs before any paid call.
3. **Cut silences** (deterministic):
   ```
   node .claude/skills/cut-silences/scripts/cut-silences.mjs raw.json --video raw.mp4 --out-dir edit [--gap 0.55] [--head-pad 0.22] [--tail-pad 0.34] --apply
   ```
   Pauses < `--gap` stay; trimmed pauses keep a breath (0.24 s after ≥2 s pauses, 0.20 s after sentence ends, 0.14 s otherwise; 55/45 split). Outputs `*.silence-edl.json`, `*.silence-transcript.json`, `*.silence-decisions.md`, `*.silenced.mp4` (libx264 crf 18, AAC 192k, faststart). Removes ~15–20% of a typical take. Needs FFmpeg 7+ and exactly one video + one audio stream.
4. **Cut mistakes** (review-gated):
   ```
   node .claude/skills/cut-mistakes/scripts/find-cut-candidates.mjs edit/raw.silence-transcript.json --out-dir edit
   # present candidates (stutter / retake / false_start, with confidence) to the user; write approved-cuts.json
   node .claude/skills/cut-mistakes/scripts/apply-cuts.mjs edit/raw.silence-transcript.json --cuts edit/approved-cuts.json \
        --video edit/raw.silenced.mp4 --output edit/clean.mp4 --out-dir edit --apply
   node scripts/build-edl-review.mjs edit/raw.mistakes-edl.json --original raw.mp4 --edited edit/clean.mp4 --output edit/review.html
   npx serve . -p 8080 -n     # Range-capable server for scrubbing
   ```
   `approved-cuts.json`: `{"cuts":[{"start":s,"end":s,"reason":"..."}]}` on the silenced timeline; you may widen a range to the clean restart; **zero cuts is valid**. False positives: emphatic repetition, "is, is this…" questions, lists. Joins are hard cuts.
5. **Plan the story** (`video-storytelling` for a persistent visual world; `hyperframes-video-beats` for overlays on a talking head). One visual idea per beat, anchored to transcript phrases.
6. **Author** overlays (read `MOTION_PHILOSOPHY.md`, but framework contracts and the brief override its code recipes). Cards from `style-library/` (406 drafts in two styles, slots + tokens) are starting points; restyle with this brand's `brand.css`.
7. **Check:** `node scripts/preflight.mjs <project>` (catches "0:00 / 0:00" causes), `npx hyperframes lint`, `node scripts/validate-beat-sync.mjs <project> [--suggest-fix]` (beat start must sit −0.2…+1.8 s before its `data-anchor` phrase).
8. **Draft → inspect → final.** Read encoded frames and transitions, listen across every cut, check face framing and A/V sync; `VERIFY.md`.

### Overlay beats on a talking head (`hyperframes-video-beats`)
- Full-screen takeover (4–12 s) for thesis/list/section/big stat/quote; glass lower-third (12–30 s) for explanations, ~68–72vw wide, centred at the bottom, never over the face.
- No more than 20–30 s without a beat early, 30–45 s in the body. Start 0.2–0.6 s before the anchor phrase; clear 0.1–0.5 s before the next card.
- Copy readable in under a second. Don't restore a beat the user shortened.

### Visual storytelling rules (`video-storytelling`)
One persistent world (never redraw/relabel an element), camera as the edit (world/region/detail altitudes), exactly one element at full brightness (active 1.0 / context 0.56 / spent 0.33 opacity), spatial open loops, ~20 words on screen per section, exits faster than entrances, no cross-fades between full-bleed layers, beats 0.15–0.25 s before the anchor word, dead screen > 1.5 s flagged. Leave air: if a sentence gap is ~10× tighter than the speaker's median, insert 4–8 frames of room tone (never `anullsrc`). Render with `--workers 1`. Build and review **one** section end to end (muted, three times) before the rest.

## Short-form reels (`short-form-edit`, 1080×1920)

First gate: in 3 seconds, is someone convinced to watch to the end?
1. Read `docs/EDITING-PLAYBOOK.md`; probe; transcribe the actual take.
2. With a reference: contact sheets + strips → `REFERENCE-ANALYSIS.md`; borrow mechanisms, not copy.
3. Asset shortlist (exact usable intervals, action, provenance, story role) before locking the concept.
4. Silence + mistake tools, **then read the whole transcript by hand**. Lock the cut after the rough animatic; later timing changes rebuild captions/graphics/SFX from one map.
5. `DESIGN.md`, beat plan (hook → open loop → escalation → evidence → payoff → CTA), `OPEN-LOOPS.json`; **three openings**, compared sound-off; low-res moving animatic before polish.
6. Phone-safe text x 90–930, y 200–1600. Captions at exact word onsets (≤ 2 frames, ≤ 0.15 s anticipation); every graphic beat has an action and outcome.
7. Logos: official asset with source URL + checksum, or plain text. Real people: verified photos only.
8. Footage: each B-roll scene once per reel (recrop/speed/regrade doesn't make it new) → `assets/footage-ledger.json`; contain framing by default; a still with a push is not B-roll.
9. Generation (Kie.ai etc.): check credits, record model/prompt/task id, inspect corners for gibberish text.
10. Audio: normalise voice, bed 14–20 dB under to start then duck; `short-form-edit` targets ~−16 LUFS / ≤ −1 dBTP while the playbook says −14 / ≤ −1.5: brand.json `audio` decides, measured on the final stereo encode; SFX on visible events aligned to the audible peak.
11. Validators: `npm run validate:short-form -- video-projects/<slug>` (plan.json ↔ transcript ↔ edit-decisions: caption words within 5 ms, scenes contiguous and frame-aligned, no >2.2 s visual gap without `holdReason`), `npm run validate:footage -- …`.
12. `ENTERTAINMENT-REVIEW.md` (where attention drops; never invent retention numbers) and `VERIFY.md`.

House reel style (measured from 27 reels): speech starts within 0.1 s; phrase gaps < ~0.2 s; 4.0–4.7 words/s; shots 1.1–1.4 s average, none > ~2.8 s; first cut at 0.6–1.0 s; layouts split 30–42% / full B-roll 50–55% / punch-in 5–15%; speaker on screen ~45%, never gone > 3.5 s. Captions 1–3 words, Montserrat ExtraBold caps ~62–64 px, serif accent on 5–20% of chunks, colour on 25–45%, one dark box, never over mouth/chin. Bed ~11 dB under voice. Encode once (segment concat drifts lip sync); never speed up the voice; cut between phrases, never inside one.

## Motion showreel (`motion-showreel`, 10–30 s cut to music)

```
node .claude/skills/motion-showreel/scripts/analyze-reference.mjs ref.mp4 out --fps 6 --bpm 128
node .../music-grid.mjs take.mp3 --bpm 128 --beats --json grid.json        # kick-band phase, not full band
node .../splice-music.mjs take.mp3 --period 0.4644 --phase 0.085 --segments "4-28,48-56.7" --length 15 --gap 16 --out music-bed.wav
node .../beatgrid.mjs --period 0.4644 --fps 60 --length 15 --chapters "01 Physics:4, 02 Type:8, 03 Grid:4, 04 Drop:4, 05 Lookdev:4, Flurry:4, 07 End:rest"
node .../sfx.mjs kit.json assets/audio/sfx                                 # ElevenLabs SFX (paid)
node .../mix.mjs --bed music-bed.wav --events events.json --out master.wav --lufs -14
ffmpeg -i render.mp4 -i master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest final.mp4
```
Grammar: one brand motif through 6–7 labelled craft chapters, persistent HUD, cuts on the beat (120–130 BPM, within 2 frames), animate on off-beats, ending mirrors the opening in the logo lockup. Verify cuts within ~35 ms of a beat; brand test with the HUD covered.

## Other kit pieces

- `make-a-video`: 8-gate beginner flow (intent → script/voice → style → BRIEF hard approval → scaffold + STORYBOARD → build → lint + Studio gate → draft, frames opened with Read, sign-off, final).
- `website-to-hyperframes`: capture → DESIGN → SCRIPT → STORYBOARD → VO (`npx hyperframes tts`, ElevenLabs, or this skill's `voice.py`) → transcribe → build → validate.
- `style-templates/`: `dark-graph-paper-template` (8 s loop background), `left-glass-popout` (camera reframe + glass panel; needs `assets/source.mp4`). Localise their CDN GSAP.
- `scripts/video-use-to-hyperframes-transcript.mjs <edl.json>`: multi-source EDL → output-timeline transcript (`out_t = (src_t − seg_start) + seg_offset`).

## Licence notes

Kit code MIT; pipeline material under its use permission (keep the notice); bundled HF skills Apache-2.0. The AIS brand assets and example projects in the repo are **not** licensed for reuse; "Vox", "Kallaway" names are aesthetic references only.
