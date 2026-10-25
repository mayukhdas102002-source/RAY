# Quality bar: what "product grade" means for Ray

Nothing is presented as finished until it clears this bar. Evidence, not impressions: run the scripts, open the images, read the numbers.

## 1. Automated checks (every render)

```bash
python scripts/ray.py tool qa_check delivery/<file>.mp4 --size 1080x1920 --fps 30 --timeline timeline.master.json \
       --lufs -14 --tp -1 --sheet 12 --strips --verify VERIFY.md
python scripts/ray.py tool ledger check                                  # rights, duplicates, spend, AI flag
python scripts/ray.py tool transcribe_words delivery/<file>.mp4 --script scenes.json   # fresh ASR vs script
```
Pass = size/fps/duration exact (±1 frame), yuv420p, faststart, 48 kHz stereo, loudness ±1 LU of target, true peak under limit, no unintended black/frozen frames, no missing or mangled words.

## 2. Review scorecard (score 1–5; ship at ≥ 4 everywhere, never below 3)

| Dimension | 5 looks like | Red flags |
|---|---|---|
| **Message** | One promise, instantly clear, CTA obvious | Two ideas fighting; CTA buried |
| **Hook** | First 3 s stop the scroll with sound off | Logo/intro first; slow fade-in; text wall |
| **Story & pacing** | Every scene has a job; momentum; a pause before the payoff | Dead air > 1.5 s; same shot size repeated; "timer editing" |
| **Picture** | Composed, consistent, real or convincingly real | AI tells (hands, faces, physics, gibberish text); mismatched characters |
| **Brand** | Correct colours, fonts, logo, voice; reads as the brand with the logo covered | Off-palette, wrong font, stretched/recoloured logo |
| **Motion & type** | Purposeful, readable, on safe areas, one transition family | Decorative motion, tiny text, text over faces |
| **Sound** | Clear voice, bed under, effects on actions, consistent loudness | Music fights voice; clipped words; loud/quiet jumps |
| **Captions** | Accurate, synced, readable, on-brand | Wrong spellings, late cues, caption soup |
| **Accessibility** | Captions, contrast ≥ 4.5:1 for text, no flashing > 3/s, plain language | Low contrast, white on light, strobe effects |
| **Technical** | All QA checks pass at every aspect | Wrong size, loudness off, black frames |
| **Rights & truth** | Licences, consents, sources, disclosures on file | Unlicensed music, unbacked claims, undisclosed AI person |

Write the scores and fixes into `VERIFY.md` for Full-production jobs; for Standard, list any dimension below 4 with the fix.

## 3. Picture checks by eye

- First and last 3 seconds frame by frame.
- Every cut strip (`renders/**/qa/*.cut-*.jpg`): flash frames, half-drawn elements, caption across a cut.
- One frame per scene at every aspect: safe areas, nothing important cropped, faces clear of text.
- AI shots: the Direct module's realism checklist (`modules/direct/director/09-realism-checklist.md`).
- Logo occurrences: official file, correct colourway, clear space.

## 4. Sound checks

- Loudness and true peak on the **final encoded file**, not the WAV.
- Listen-equivalents you can do without ears: silence detection at cuts, waveform/spectrogram map (`ray.py tool audiomap`), word-level transcript of the final.
- For music-heavy or troubled mixes: Audio module diagnose workflow (measure → findings with exact fixes → re-measure).

## 5. Before hand-off

- Every deliverable in `delivery/manifest.json` with sha256 and QA = PASS.
- Sidecars (SRT/VTT) for platforms with native captions; clean versions if requested.
- `VERIFY.md` ticked from evidence; open items listed honestly.
- Plain-language summary to the person: what's delivered, where, what's left for them (e.g. "turn on Meta's AI label at upload").
