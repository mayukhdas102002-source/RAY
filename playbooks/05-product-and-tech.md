# 05 · Product and tech

Showing a product working: launches, feature releases, demos, app walkthroughs, SaaS motion design, e-commerce product videos, unboxings and spec explainers.

## Formats

| Format | Length | Aspect | Core |
|---|---|---|---|
| Launch film | 30–90 s | 16:9 + 9:16 | Reveal, problem → product → proof → CTA |
| Feature release | 15–45 s | 16:9 / 1:1 / 9:16 | One feature, before/after, UI close-ups |
| Product demo / walkthrough | 1–5 min | 16:9 | Real screen recording or real product handling, chapters |
| E-commerce product video | 10–30 s | 1:1 / 4:5 / 9:16 | Hero turntable, details, scale in hand, use in context |
| Website-to-video | 30–60 s | 16:9 / 9:16 | Captured site → animated story |
| App store preview | 15–30 s | device-specific | Real UI only; platform rules on content |

## Intake extras

Product truth: what it does, for whom, the "aha" moment, real UI or real product access, pricing/availability lines, launch date; brand UI kit (Figma), product renders/3D, screen recordings.

## Workflow

1. **Find the aha** → **G**: the single moment the product earns attention (a tap that changes the world, a before/after, a speed or simplicity proof).
2. **Capture real first:** screen recordings at native resolution (60 fps if motion-heavy), clean data, no personal info, no cookie banners clicked on camera; product footage on clean sets or product photography for stills.
3. **Website/product page available?** `npx hyperframes capture <url> -o captures/site` → `/product-launch-video` HyperFrames workflow or herk `website-to-hyperframes` (capture → DESIGN → SCRIPT → STORYBOARD → VO → build → validate). Brand kit wins over captured styles.
4. **Script** with the launch shape: hook (the old pain) → reveal → 2–3 proofs (each a UI moment) → availability → CTA. → **G**
5. **UI animation:** rebuild key UI moments as Remotion/HyperFrames components (crisp at any size, editable), or zoom/pan real recordings with motion blur; phones/devices as real-looking frames with real UI composited (never AI-drawn UI text).
6. **AI plates** only for lifestyle context (hands, places), with screens blank for compositing (Direct `07-ui-and-text-layer-remotion.md`).
7. **Voice/music/SFX:** UI SFX (taps, swipes) on visible interactions; music builds to the reveal.
8. **Preview → G → drafts → G → finals** in all placements; app-store versions follow store rules (real UI, no misleading features).

## E-commerce specifics

- Shot list per SKU: hero (3 s), detail ×2, scale (in hand/on body), in use, variant colours, packaging.
- Batch the edit: one Remotion/HyperFrames template, SKU rows in `variants.json` (`playbooks/11-personalised-and-batch.md`).
- Price/offer lines from data, not typed by hand; legal lines per market.

## Craft rules

- Real UI at real speed (speed up only scrolling/loading, and say so if it matters).
- One feature per beat; highlight the active element (dim the rest).
- Show the product in a real hand/context by second 5.
- Never show features that don't exist yet without labelling "Coming soon".

## Deliverables

Launch master + cutdowns per placement, feature clips, GIF/WebM loops for web (`--format webm` or `--codec gif`), stills, captions, chaptered demo.

## Accelerators

Figma connector (UI assets), Higgsfield Marketing Studio/product photoshoot workflows for lifestyle stills, storage connectors for product libraries, OpenMontage `screen-demo` and `ProductReveal` composition.
