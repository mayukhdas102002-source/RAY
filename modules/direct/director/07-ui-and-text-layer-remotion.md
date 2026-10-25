# 07 · UI and text layer (Remotion)

AI video cannot render readable, stable text. Every word on screen comes from Remotion: app screens, tablet dashboards, signs, floor displays, supers, logos and end cards. This is also where the "Revolut feel" lives, with confident, fast, clean UI motion.

## Starter project

`templates/remotion-starter/` is a working Remotion 4 project (from the Homely "Going Up" film):

- `src/shots.json` is the shot list and the single source of truth.
- `src/Film.tsx` is the edit. It shows animatic boards until plates exist, then plays `public/plates/<ID>.mp4`. `PLATES` sets `start` and `speed` per shot.
- `src/screens/Screens.tsx` holds phone screens (1080×2340, a logical 864×1872 layout scaled 1.25), a tablet CRM (1600×1000), a directory sign, an LED floor display (transparent), and the end card.
- `src/ui/kit.tsx` has the logo mark, supers, glass cards, typing chat bubbles, count-up numbers and pop springs.
- `src/theme.ts` has fonts bundled locally (Poppins and IBM Plex Mono via `@remotion/fonts`) and brand colours.

Setup:
```bash
cd remotion-starter && npm install
npx remotion studio                                     # preview
npx remotion render src/index.ts GoingUp out/animatic.mp4
```
Point headless renders at a Chromium if needed: `--browser-executable=/path/to/chrome`. Low-core machines need `--concurrency=2`, and heavy frames need `--timeout=180000`.

## Screen design rules

- Real product logic. Each screen has one headline, one number, and one primary action button at the bottom, like a shipping app. Empty lower halves read as fake.
- Show state changes (connecting, verified, ready) with ticks and springs. Numbers count up.
- Use fictional third-party names (banks, partners) unless there's permission.
- Mark future features in the end card: "Concept film · Future product vision".
- Match the brand exactly: swap the approximated `Mark` for the official SVG, and the fonts for the brand fonts.

## Getting screens onto plates

1. Generate the plate with the device screen **plain white or grey, flat to camera, and steady**.
2. Render the screen composition from Remotion at native size (`SCR-*` compositions, duration = shot length).
3. Corner-pin or planar-track it onto the device in CapCut, Resolve (Fusion), After Effects (Mocha) or Premiere. Add a subtle screen glare and match the blur and grain.
4. Transparent overlays (floor displays, supers over live plates) render as WebM with alpha:
```bash
npx remotion render src/index.ts LED-12-23 out/LED-12-23.webm --codec=vp9 --pixel-format=yuva420p --image-format=png
```
ProRes 4444 also works (`--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`) but the files are about 30× larger.

## Supers and end card

- At most two supers in the body of the film. Use one typeface, sit them in the lower third, and hold each at least 1.5s.
- End card: the promise line, then the logo and brand line, then a small disclaimer. About 4s, with the logo landing on the last music hit.
- Burn-in version for rooms without sound: add dialogue lines as subtitles (the starter's animatic already does this).
