# 10 · Localisation and accessibility

Taking a finished piece to more people: subtitles, translated captions, dubbed and re-voiced versions, localised supers and end cards, audio description, and accessible variants.

## Options (cheapest → richest)

| Level | What changes | Tools |
|---|---|---|
| Subtitles (same language) | SRT/VTT + burned captions | `transcribe_words` → `captions_convert` |
| Translated subtitles | SRT/VTT per language | Translate the master SRT (Claude), native review |
| Localised graphics | Supers, end card, legal lines per market | Remotion props / HF variables per language |
| Re-voiced (TTS) | New VO per language in the brand voice | `voice.py generate --language xx` (cross-language cloning), VoiceStudio 600+ languages |
| Dubbed (speaker's own voice) | Lip-synced or voice-over dub of on-camera speech | VoiceStudio dubbing pipeline; OpenMontage `localization-dub`; lip-sync tools only with consent |
| Accessible version | Audio description, extended captions, simplified language, sign-language inset | AD script + VO track; sign interpreter footage composited |

## Workflow

1. **Lock the source:** final master, final script, `captions/words.master.json`, `scenes.json`.
2. **Translation pack:** export every string — VO lines (`scenes.json vo_text`), on-screen copy, legal lines, end card, post copy — into `localise/<lang>/strings.json`. Translate (Claude, or a professional for regulated content), keeping length budgets (VO ±15% of source duration; supers fit the layout).
3. **Native review** of strings → **G** (log reviewer in `DECISIONS.md`).
4. **Per language:**
   - New `scenes.<lang>.json` (copy + `vo_text`), voice: `ray tool voice generate --scenes scenes.<lang>.json --language <code> --out vo/<lang>/` (keep the reference transcript in its original language for cross-language cloning).
   - `ray tool transcribe_words vo/<lang>/ --script scenes.<lang>.json --language <code>` (never a `.en` model on non-English audio).
   - `ray tool timeline_from_vo scenes.<lang>.json --vo vo/<lang> --remotion remotion` (or a per-language HF project); scene lengths re-flow to the new VO.
   - Fonts: check glyph coverage (accents, CJK, Arabic/Hebrew RTL — Remotion skill has Arabic text rules); swap to a brand-approved fallback per script.
   - Render rows in `variants.json` with `_<lang>` ids.
5. **Dubbing on-camera speech:** VoiceStudio `/dub/*` (separate → transcribe → translate → per-segment TTS → QC → stems + SRT/VTT/ASS), or OpenMontage `localization-dub`. Consent from every speaker whose voice is cloned; disclose dubbing.
6. **QA per language:** fresh ASR vs translated script, caption timing, text overflow on every aspect, loudness, cultural check (gestures, colours, imagery) → **G**.

## Accessibility checklist

- Captions on every social and public video; accurate, synced, speaker IDs when needed, sound cues in brackets for deaf/HoH viewers ([music], [laughter]) in SDH versions.
- Audio description for visual-only information: write an AD script for gaps in dialogue; render as a separate audio track or an "AD version".
- Contrast ≥ 4.5:1 for text; text ≥ 44 px at 1080; no flashing more than 3 times per second; avoid red/green-only meaning.
- Plain language versions for public information; sign-language inset when required (interpreter footage, consented).
- Transcripts for long-form; chapters for navigation.

## Deliverables

Per language: master(s), SRT/VTT, localised stills/thumbnails, strings file, reviewer sign-off. Accessible: SDH captions, AD version, transcript.
