# Homely · “Going Up” — :54.5 future-vision spot (2027)

The AI plates come from Higgsfield. Every screen, floor number, super and the end card is built here in Remotion, so no text in the film is ever drawn by AI.

## Run

```bash
npm install
npm run studio                 # scrub the edit, tweak timing
npm run render                 # out/going-up-animatic.mp4 (with burn-in)
npx remotion render src/index.ts GoingUpClean out/going-up-master.mp4
```

## Adding a Higgsfield plate

1. Name the clip by shot, e.g. `S11.mp4`, and put it in `public/plates/`.
2. In `src/Film.tsx`, add it to `PLATES`:
   ```ts
   export const PLATES = { S11: { file: 'S11.mp4', start: 0.5, speed: 1 } };
   ```
   `start` skips into the clip (keep the best seconds of a 5s generation). `speed` tightens or slows the motion.
3. The board for that shot disappears. For device shots (S02, S04, S09, S12, S15), corner-pin the matching screen onto the blank screen in your editor.

## Compositions

| ID | Size | Use |
|---|---|---|
| `GoingUp` / `GoingUpClean` | 1920×1080 | The full edit, with and without burn-in |
| `SCR-Profile` · `SCR-Eligible` · `SCR-Approved` · `SCR-Market` | 1080×2340 | Phone screens → corner-pin onto the blank phones in S04, S06, S12, S15 |
| `SCR-Ticket` | 1600×1000 | Lender CRM on the tablet in S09 |
| `SCR-Directory` | 1920×1080 | Lobby directory screen in S02 |
| `LED-01` … `LED-24` | 600×260, transparent | Floor display above the lift doors |
| `EndCard` | 1920×1080 | S16 |

Transparent floor display (WebM with alpha, reads in CapCut, Premiere, Resolve):

```bash
npx remotion render src/index.ts LED-12-23 out/LED-12-23.webm --codec=vp9 --pixel-format=yuva420p --image-format=png
```

## Editing

- Shots, timing, prompts and models live in `src/shots.json`, the same data as the storyboard page.
- Screen copy and numbers are in `src/screens/Screens.tsx`. Lender names are fictional placeholders.
- `Mark` in `src/ui/kit.tsx` is an approximation of the Homely logo. Swap in the official SVG.
- The project runs at 30 fps. For a 24 fps film finish, change `FPS` in `Film.tsx` and `Root.tsx` and re-time the screens.
