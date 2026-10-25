# QA, versions and delivery

## Draft → approval → final

1. `python scripts/render_matrix.py variants.json --draft` (half-res Remotion, `--quality draft` HyperFrames) → `renders/drafts/` + QA sheets.
2. Open the contact sheet and cut strips with Read; send the user the drafts (or the Studio/preview link) and stop for Gate 6.
3. On approval: `python scripts/render_matrix.py variants.json` → `delivery/<id>.mp4` (rendered muted, `audio/master.wav` muxed, QA'd) + `delivery/manifest.json` (sha256, duration, QA verdict).
4. Fill `VERIFY.md` from evidence; send the delivery list.

Long renders in a time-limited shell: render one variant per call (`--only`), use HyperFrames detached mode, or hand the user the exact command.

## QA checklist (what `qa_check.py` measures, and what you must look at)

Automatic (`qa_check.py <file> --size WxH --fps N --timeline timeline.master.json --lufs -14 --tp -1 --sheet 12 --strips --verify VERIFY.md`):
- container/codec, size, fps, duration within ±1 frame, `yuv420p` (soft), `+faststart`
- audio present, 48 kHz, stereo; integrated LUFS ±1 LU; true peak ≤ target
- black frames (pix_th 0.04 so dark brand grounds don't trip it), frozen video ≥1.5 s (fine on held cards, a bug on footage), silences ≥1.5 s
- contact sheet, 10-frame strips across every scene cut, single frames on request

By eye (open the images; never claim a pass from numbers alone):
- First 3 seconds frame by frame: does the hook read with sound off?
- Every cut strip: no flash frames, half-drawn elements, caption straddling a cut, jumpy footage.
- Text inside safe areas at every aspect; nothing over faces/mouths; contrast on footage.
- Logos: official, correct colourway, never distorted; brand colours and fonts match tokens.
- AI plates: hands, faces, text artefacts, physics.

By ear / transcript:
- Fresh transcription of the final audio vs the script (`transcribe_words.py delivery/x.mp4` then compare): no missing/mangled words, brand names right.
- Words not clipped at cuts; music not masking speech; last word not faded.

Project checks: `ledger.py check` (licences, duplicates, spend, AI flag), claims vs approved list, consent on file for cloned voices/likeness.

## Aspect ratios and versions

| Aspect | Size | Typical placement |
|---|---|---|
| 16:9 | 1920×1080 (or 3840×2160) | YouTube, web hero, LinkedIn, presentations, TV |
| 9:16 | 1080×1920 | Reels, TikTok, Shorts, Stories |
| 4:5 | 1080×1350 | Instagram/Facebook feed |
| 1:1 | 1080×1080 | Feed, LinkedIn, marketplaces |

- Render each aspect **natively** (Remotion `BrandFilm-<aspect>`, `hf_build.py --size`), not by cropping: text and safe areas reflow. `reframe.py` is a fallback for footage plates.
- Cutdowns (30/15/6 s): new `scenes.json` per cut (drop scenes, keep the promise and CTA), re-run the clock; don't speed up.
- Hooks A/B: duplicate the first scene with different openings; one variant row each.
- Languages: per-language VO + captions + supers; filename tag `_<lang>`.
- Clean master (no burned captions) + SRT/VTT for platforms with native captions; burned-in for sound-off social.
- Check each platform's current upload specs before delivery (they change); keep H.264 High, yuv420p, AAC 48 kHz stereo, `+faststart` as the safe default.

## Naming and handover

`<Brand>_<Title>_<aspect>_<lang>_v<N>.mp4` (e.g. `Homely_SpringRates_9x16_en_v3.mp4`), sidecars with the same stem (`.srt`, `.vtt`), stills (`_endcard.png`, `_thumb.png`). `delivery/manifest.json` lists hashes; `VERIFY.md` records evidence; `DECISIONS.md` records approvals and spend. For clients, a short shot-by-shot write-up (Direct module (AI Director) `templates/client-shot-by-shot.md`) helps sign-off.

## Disclosure

Turn on the platform's AI-generated content label when the video contains realistic AI people, places, events or cloned voices. Keep consent records. Mark future-product visuals as concept.
