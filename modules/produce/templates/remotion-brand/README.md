# Remotion brand film starter

Data-driven brand film: `src/brand.json` (brand_tokens.py), `src/timeline.json` + `src/captions.json` (timeline_from_vo.py) drive every composition. Remotion 4.0.537, React 19, Node 22+.

```bash
npm install
npx remotion studio                         # BrandFilm-16x9 / -9x16 / -1x1 / -4x5, EndCard-*, Thumbnail-*
npm run draft                               # half-res 16:9 draft
node scripts/render-all.mjs --draft         # every aspect
npx remotion render BrandFilm-9x16 renders/reels.mp4 --props='{"showCaptions":true}'
npx remotion render BrandFilm-16x9 renders/clean.mp4 --muted --props='{"showCaptions":false}'   # mux audio/master.wav after
```

- Scenes: `src/scenes/Scenes.tsx` (title, statement, stat, list, quote, footage, image, lowerThird, endCard). Restyle here; never hardcode colours (use `BRAND`).
- Layout/safe areas/type scale: `src/layout.ts`. Captions: `src/Captions.tsx`. Music ducking + VO placement: `src/BrandFilm.tsx`.
- Media goes in `public/` (the pipeline scripts copy VO to `public/vo`, music to `public/audio`, footage to `public/media`, brand files to `public/brand`).
- Personalised/batch: pass a whole `timeline` (and `captions`) via `--props`; duration follows.
- Licence: Remotion is free for individuals and companies of ≤3 people; others need a Company License.
