# 11 · Personalised and at-scale video

One template, many outputs: personalised videos (names, cities, offers), data-driven variants, product catalogue videos, real-estate listing videos, event speaker cards, dynamic ad sets, localised retail versions.

## Pick the engine

| Need | Engine | How |
|---|---|---|
| Up to a few hundred, local | Remotion `--props` per row | `render_matrix.py` rows with `props` (whole timeline or fields) |
| Hundreds to thousands, fast | Remotion Lambda | `npx remotion lambda render <site> <comp> --props=row.json` (AWS keys in `.env`) |
| HTML-first, simple fields | HyperFrames variables | `npx hyperframes render --batch rows.json --output "renders/{index}-{city}.mp4"` |
| Huge HTML batches | HyperFrames Lambda | `npx hyperframes lambda render-batch` (JSONL rows) |
| Per-row voice | `voice.py generate --text …` per row, then props reference the file | cache by text hash |

## Intake extras

The data source (CSV/Sheet/CRM export/API), which fields vary, privacy (personal data handling, retention, consent for personalised outreach), volume and deadline, delivery method (files, hosted links, email), QA sampling rate.

## Workflow

1. **Data contract:** define fields, types, max lengths, required/optional, defaults, and validation rules → `batch/schema.json`. Clean the data; reject rows that break limits (never silently truncate names).
2. **Template:** build one composition that takes props/variables (Remotion zod schema or HF `data-composition-variables`); compute duration from data (`calculateMetadata`); text fits with `fitText`/`fitTextFontSize`.
3. **Stress rows:** longest name, shortest, accented/RTL characters, missing optional fields, largest numbers. Render stills for each → **G**.
4. **Voice per row (optional):** generate lines with pinned seed; QC a sample for pronunciation of names (lexicon entries for tricky names); never clone a recipient's voice.
5. **Pilot batch:** 10–20 rows → QA (`qa_check` on each) → **G**.
6. **Full batch:** `ray tool render_matrix variants.json` (local) or Lambda; parallelism tuned with `npx remotion benchmark`.
7. **QA at scale:** automated QA on 100%; visual review on a random 5% + all stress rows; manifest with row id → file → hash.
8. **Delivery:** files named by row id (no personal data in filenames if shared), manifest CSV, delete intermediate personal data when done (note it in `DECISIONS.md`).

## Real-estate / catalogue specifics

- Listing video template: hero exterior → 5–8 room shots (photo push-ins only if no video; label as photos) → key specs card → map/location card → agent end card. Specs from the data feed only.
- E-commerce: SKU template (hero, detail, in-use, price/offer), price lines from data with market-specific legal text.
- Never let AI invent features of a property or product; generated shots only for lifestyle context, labelled where required.

## Deliverables

Rendered files, manifest (row → file → hash → QA), sample review sheet, the template + schema for future runs.
