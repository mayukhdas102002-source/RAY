# Verify: {{TITLE}}

Nothing is "done" until every box below is ticked from evidence (measurements, frames actually opened, a fresh transcript),
not from the plan. `qa_check.py --verify VERIFY.md` appends the technical sections automatically.

## Picture
- [ ] Contact sheet and cut strips opened and read (every cut, not one frame per scene)
- [ ] First 3 seconds read frame by frame: the hook lands with sound off
- [ ] No text outside the safe area at any aspect; nothing over a face or mouth
- [ ] No AI-drawn text, logos or signage; every logo is the official file (hash matches `brand/tokens/provenance.json`)
- [ ] No black/frozen frames except intentional holds; no flicker at scene joins
- [ ] Colours/fonts match the brand tokens (spot-check 3 frames against `brand/tokens/BRAND.md`)

## Sound
- [ ] Final file measured: ____ LUFS integrated, ____ dBTP (target from brand.json)
- [ ] Music under voice everywhere; no clipped words at cuts; last word not faded
- [ ] Fresh ASR of the final render compared with the script: no missing or mangled words
- [ ] Captions match the audio (word timing within ~2 frames) and spell brand names correctly

## Rights and disclosure
- [ ] `ledger.py check` passes: every asset has a source and licence; no B-roll reused in one reel
- [ ] Synthetic voice used with written consent; AI-content label planned for platforms that require it
- [ ] Claims match `BRIEF.md` approved claims

## Delivery
- [ ] Every variant in `delivery/manifest.json` with sha256, duration and QA verdict
- [ ] Files named `<brand>_<title>_<aspect>_<lang>_v<N>.mp4`; SRT/VTT sidecars where captions aren't burned in
