# Brand system: one brand.json, every engine

`brand/brand.json` (schema `bvp.brand/1`, example in `templates/brand.example.json`) is the only place brand values live. `scripts/brand_tokens.py` compiles it and checks it. Keep reusable kits in `AI Production/_brands/<brand>/` and copy them into projects with `new_project.py --brand`.

## Building a kit

1. Collect official assets: logo files (SVG preferred; light and dark versions; icon), brand fonts (WOFF2/TTF with a licence that allows video embedding), colour values, the brand guidelines PDF.
   - No official logo? Use the brand name set in the heading font. Never redraw, trace or generate a logo.
   - No font files? Pick the closest family the engines resolve without files (Inter, Poppins, Montserrat, Outfit, Roboto, Open Sans, Lato, Playfair Display, IBM Plex Mono, JetBrains Mono, Bebas Neue…) and say so.
2. Fill `brand.json`. Paths are relative to the file. Colour roles:

| Role | Use |
|---|---|
| `bg` / `fg` | Ground and ink. fg on bg must be ≥ 4.5:1. |
| `primary` | The one voltage colour: bars, CTA, key numbers. One primary element per frame. |
| `accent` | The active thing: spoken caption word, current list item. |
| `secondary`, `surface` | Panels, quote cards, lower-third backing. |
| `muted` | Supporting copy (≥ 3:1 on bg). |
| `line` | Hairlines, caption box edge. |
| `light_bg` / `light_fg` | Optional light mode for brands that live on white. |

3. Motion personality: `energy`, `spring_damping` (200 = no bounce), `entrance_s`, `stagger_s`, `gsap_ease`, `css_ease`, one `transition` family.
4. Captions: case, words per page (vertical 3 / horizontal 6–7), position, box, highlight role.
5. Audio: `lufs_target` (−14 social/YouTube default), `true_peak_db`, `music_under_voice_db`, music mood, SFX style.
6. Voice: provider, profile, engine, seed, `instruct` (delivery), lexicon (respellings for TTS only; captions keep real spelling), consent flag.
7. Imagery style, prompt prefix and avoid-list for any generated stills/video (fed to OpenMontage and Direct module (AI Director) prompts).
8. Claims policy and approved claims.

## What brand_tokens.py writes

| File | Consumer |
|---|---|
| `remotion/src/brand.json` + `remotion/public/brand/{fonts,logo}` | Remotion starter (`src/brand.ts` loads fonts with `@remotion/fonts`, blocks render until ready) |
| `hyperframes/brand.css` (`:root` vars `--color-*`, `--font-*`, `--radius`, `--ease`, `@font-face`) + `hyperframes/assets/brand/` | HyperFrames compositions (`var(--color-primary)` etc.) |
| `brand/tokens/frame.md` (copied to `hyperframes/frame.md` if absent) | HyperFrames design spec: YAML tokens (normative) + prose (intent). HF workflows read `frame.md` → `design.md` → `DESIGN.md`. |
| `brand/tokens/openmontage-style.yaml` | Copy to `OpenMontage/styles/<brand>.yaml`; pick it as the style playbook at proposal. OpenMontage's `lib/hyperframes_style_bridge.py` maps playbooks to CSS vars. |
| `brand/tokens/pireel-frame.md` | Pireel Studio Frame (`packages/studio-frames/content/<id>/frame.md`; merge with `mergeFrameRegistries` in a custom shell). |
| `brand/tokens/BRAND.md` | Human/agent brief; herk-edit-kit projects read `BRAND.md`. |
| `brand/tokens/captions.style.json` | Caption colours/case for `hf_build.py` and `captions_convert.py --to ass`. |
| `brand/tokens/provenance.json` | sha256 of brand.json, logos, fonts: proves the official files were used. |
| `brand/tokens/check.md` | WCAG contrast results and missing-file list. |

Missing fonts/logos are dropped from engine outputs (so renders never block) and listed as FIX items.

## Rules that keep it on-brand

- Never hand-type a hex or font family into a scene; read `BRAND`/CSS vars. Changing the brand means editing brand.json and re-running the script.
- One primary element per frame; accent only for the active thing; never pure white text on light footage; captions always on the caption box.
- Safe areas: landscape ~7% sides / 9% top-bottom; 9:16 copy inside x 90–930, y 200–1600 (UI chrome lives outside).
- Minimum sizes at 1080 short side: headline 84 px, supporting text 44 px.
- Logo: official file, minimum width from brand.json, clear space respected, never recoloured, stretched, animated into a different shape, or placed on busy footage without a backing panel. Check every occurrence in the encoded file.
- Brand test (herk showreel rule, useful for any film): take 6 random frames, cover the logo; each should still read as the brand.
