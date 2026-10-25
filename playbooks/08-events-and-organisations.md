# 08 · Events and organisations

Content organisations make for their people, members, funders and the public: event promos and recaps, conference sessions, internal comms, recruitment and employer brand, training/compliance, investor and pitch videos, annual reports, fundraising appeals, public information and campaign videos.

## Formats

| Format | Length | Aspect | Notes |
|---|---|---|---|
| Event promo / save-the-date | 15–45 s | 9:16 + 16:9 | Date, place, speakers, one reason to come |
| Event recap / sizzle | 60–120 s (+ 15–30 s) | 16:9 + 9:16 | Energy, faces, quotes, numbers, music-cut |
| Session highlight | 1–3 min | 16:9 + 9:16 clips | Speaker cuts + slides + captions |
| Internal comms / CEO update | 1–3 min | 16:9 | Plain language, captions, multilingual |
| Recruitment / employer brand | 45–120 s + clips | 16:9 + 9:16 | Real employees (consented), day-in-the-life, values shown not told |
| Training / compliance | 2–10 min modules | 16:9 | Learning objective, scenarios, knowledge checks |
| Investor / pitch video | 60–180 s | 16:9 | Problem, solution, traction numbers (sourced), team, ask |
| Annual report / impact video | 90–180 s | 16:9 + 1:1 | Data story + human stories |
| Fundraising appeal | 30–120 s | 9:16 + 16:9 | One person's story, clear ask, donate CTA |
| Public information | 15–60 s | all | Plain language, captions + sign language option, multilingual, accessible colours |

## Intake extras

Approvals chain (comms, legal, leadership), audiences (staff, members, donors, public), accessibility and language requirements, consents/releases for attendees and staff, brand/sub-brand rules, sensitive topics.

## Workflows

### Event recap (music-cut)
1. Ingest all footage + photos to `raw/`; log sources and photographer credits.
2. Select: `ray tool frames` contact sheets per clip (`--mode scene`) to find usable moments fast; pick faces, wides, reactions, signage-free brand moments, key quotes (transcribe speeches).
3. Music first: choose the track (licensed), beat grid (`music-grid.mjs`), structure intro/build/drop/outro.
4. Cut on the beat (cuts within 2 frames), quotes at the breathing points, numbers ("1,200 attendees") as cards, end card with next event/date.
5. Versions: 90 s, 30 s, 15 s, 9:16 clips per speaker.

### Internal / leadership message
Teleprompter-friendly script in plain language → shoot guide (`playbooks/06-people-on-camera.md`) → light cut → captions mandatory + translations (`playbooks/10-localisation-and-accessibility.md`) → accessibility QA.

### Training module
Learning objective → scenario script (realistic situations, dialogue) → presenter or animated scenarios (Remotion/HyperFrames; AI actors only labelled and with no real-person likeness) → knowledge-check cards → chapters → captions + transcript → LMS export.

### Investor / pitch
Numbers sourced and dated (`DECISIONS.md`), charts built from data (Remotion/HF chart components), founder on camera for the "why us", no forward-looking claims without disclaimers; versions for email (≤ 90 s) and deck embeds.

### Fundraising / impact
Dignity-first story (one person, their words, their consent), outcome data with source, one clear ask with amount examples, donate CTA on screen ≥ 3 s, captions on.

## Craft rules

- Faces and real moments over stage wides; signage and slides only when legible and relevant.
- Plain language (reading age ~12–14) for public and internal audiences; captions on everything.
- Representation: show the real diversity of the organisation without tokenism; consent from everyone identifiable.

## Deliverables

Masters, cutdowns, captions in every language required, transcripts, accessible versions, stills for newsletters, release log.

## Accelerators

Drive/Dropbox/Box connectors for event footage, Slack/Teams/email connectors for approvals (draft messages; send only on request), Canva connector for companion statics, OpenMontage `documentary-montage` for archive/footage-led pieces.
