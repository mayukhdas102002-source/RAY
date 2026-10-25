#!/usr/bin/env python3
"""Compile one brand.json into tokens for every engine, and check it.

  python scripts/brand_tokens.py brand/brand.json --project .          # write tokens + feed remotion/ and hyperframes/ if present
  python scripts/brand_tokens.py brand/brand.json --check              # validate only (contrast, files, logo hashes)

Writes into <project>/brand/tokens/:
  remotion.brand.json      -> also copied to remotion/src/brand.json (+ fonts/logos into remotion/public/brand/)
  brand.css                -> also copied to hyperframes/brand.css  (+ fonts/logos into hyperframes/assets/brand/)
  frame.md                 -> HyperFrames design spec (YAML tokens + prose); copied to hyperframes/frame.md if absent
  openmontage-style.yaml   -> OpenMontage style playbook (copy into OpenMontage/styles/<slug>.yaml)
  pireel-frame.md          -> Pireel Studio Frame (packages/studio-frames/content/<slug>/frame.md)
  BRAND.md                 -> human/agent brief, also used as herk-edit-kit BRAND.md
  captions.style.json      -> caption tokens shared by all engines
  provenance.json          -> sha256 of every logo and font file (proves official assets were used)
  check.md                 -> contrast + file checks
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import die, eprint, read_json, write_json, write_text  # noqa: E402


# ------------------------------------------------------------- colour maths

def parse_color(c: str) -> tuple[float, float, float, float]:
    c = c.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?", c)
    if m:
        h = m.group(1)
        a = int(m.group(2), 16) / 255 if m.group(2) else 1.0
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a
    m = re.fullmatch(r"#([0-9a-fA-F]{3})", c)
    if m:
        h = m.group(1)
        return int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16), 1.0
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?\s*\)", c)
    if m:
        a = m.group(4)
        alpha = (float(a[:-1]) / 100 if a.endswith("%") else float(a)) if a else 1.0
        return float(m.group(1)), float(m.group(2)), float(m.group(3)), alpha
    raise ValueError(f"Unparseable colour: {c}")


def over(fg: str, bg: str) -> tuple[float, float, float]:
    r, g, b, a = parse_color(fg)
    R, G, B, _ = parse_color(bg)
    return r * a + R * (1 - a), g * a + G * (1 - a), b * a + B * (1 - a)


def lum(rgb: tuple[float, float, float]) -> float:
    def ch(v: float) -> float:
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(fg: str, bg: str, base: str | None = None) -> float:
    bgc = over(bg, base) if base else parse_color(bg)[:3]
    base_hex = "#%02x%02x%02x" % tuple(int(round(x)) for x in bgc)
    fgc = over(fg, base_hex)
    l1, l2 = sorted([lum(fgc), lum(bgc)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "brand"


def font_format(file: str) -> str:
    ext = Path(file).suffix.lower()
    return {".woff2": "woff2", ".woff": "woff", ".ttf": "truetype", ".otf": "opentype"}.get(ext, "woff2")


# ------------------------------------------------------------- emitters

def remotion_json(B: dict) -> dict:
    C = B["colors"]
    T = B["typography"]
    cap = B.get("captions", {})
    hl = cap.get("highlight", "accent")
    font_files = []
    for role in ("heading", "body", "mono"):
        for f in T.get(role, {}).get("files", []) or []:
            font_files.append({"family": T[role]["family"], "file": Path(f["file"]).name, "weight": str(f.get("weight", T[role].get("weight", 400))),
                               "style": f.get("style", "normal")})
    uniq = {(f["family"], f["file"]): f for f in font_files}
    logo = B.get("logo", {})
    return {
        "_generated": "by scripts/brand_tokens.py from brand.json; do not hand-edit",
        "name": B["name"], "url": B.get("url", ""), "tagline": B.get("tagline", ""),
        "colors": {
            "primary": C["primary"], "secondary": C.get("secondary", C["primary"]), "accent": C.get("accent", C["primary"]),
            "bg": C["bg"], "surface": C.get("surface", C["bg"]), "fg": C["fg"], "muted": C.get("muted", C["fg"]),
            "line": C.get("line", "rgba(255,255,255,0.15)"),
            "captionBox": cap.get("box_color", "rgba(0,0,0,0.8)"), "captionText": cap.get("text_color", "#FFFFFF"),
            "captionHighlight": C.get(hl, hl if str(hl).startswith("#") else C.get("accent", C["primary"])),
        },
        "fonts": {r: {"family": T[r]["family"], "weight": int(T[r].get("weight", 400)), "fallback": T[r].get("fallback", "system-ui, sans-serif")}
                  for r in ("heading", "body", "mono") if r in T},
        "fontFiles": list(uniq.values()),
        "logo": {"light": f"brand/logo/{Path(logo['light']).name}" if logo.get("light") else None,
                 "dark": f"brand/logo/{Path(logo['dark']).name}" if logo.get("dark") else None},
        "radius": B.get("shape", {}).get("radius_px", 16),
        "motion": {"springDamping": B.get("motion", {}).get("spring_damping", 200), "entranceSeconds": B.get("motion", {}).get("entrance_s", 0.6),
                   "stagger": B.get("motion", {}).get("stagger_s", 0.12), "exitFrames": B.get("motion", {}).get("exit_frames", 6)},
        "captions": {"enabled": cap.get("enabled", True), "upper": cap.get("upper", False), "combineMs": cap.get("combine_ms", 900),
                     "position": cap.get("position", "bottom"), "box": cap.get("box", True)},
        "endCard": {"cta": B.get("end_card", {}).get("cta", ""), "url": B.get("end_card", {}).get("url", B.get("url", "")),
                    "legal": B.get("end_card", {}).get("legal", "")},
    }


def brand_css(B: dict, R: dict, font_prefix: str) -> str:
    C = R["colors"]
    lines = ["/* GENERATED by scripts/brand_tokens.py from brand.json. Do not hand-edit. */"]
    for f in R["fontFiles"]:
        lines.append(f"@font-face {{ font-family: '{f['family']}'; src: url('{font_prefix}{f['file']}') format('{font_format(f['file'])}'); "
                     f"font-weight: {f['weight']}; font-style: {f['style']}; font-display: block; }}")
    m = B.get("motion", {})
    lines += [":root {"]
    for k, v in C.items():
        lines.append(f"  --color-{re.sub(r'([A-Z])', lambda x: '-' + x.group(1).lower(), k)}: {v};")
    for r, f in R["fonts"].items():
        lines.append(f"  --font-{r}: '{f['family']}', {f['fallback']};")
        lines.append(f"  --font-{r}-weight: {f['weight']};")
    lines += [f"  --radius: {R['radius']}px;", f"  --stroke: {B.get('shape', {}).get('stroke_px', 2)}px;",
              f"  --ease: {m.get('css_ease', 'cubic-bezier(0.16,1,0.3,1)')};", f"  --entrance: {m.get('entrance_s', 0.6)}s;",
              f"  --tracking-heading: {B.get('typography', {}).get('tracking_heading', '-0.02em')};", "}"]
    lines.append("/* GSAP: ease '" + m.get("gsap_ease", "power3.out") + "' for entrances, '" + m.get("gsap_ease_inout", "power2.inOut") + "' for moves. */")
    return "\n".join(lines) + "\n"


def frame_md(B: dict, R: dict) -> str:
    C = R["colors"]
    col = "\n".join(f'  {k}: "{v}"' for k, v in C.items())
    typ = "\n".join(f'  {r}: {{ fontFamily: "{f["family"]}", weight: {f["weight"]} }}' for r, f in R["fonts"].items())
    vt = B.get("voice_and_tone", {})
    logo = B.get("logo", {})
    return f"""---
version: alpha
name: {B['name']} — Frame
description: >
  Frame-scale design system for {B['name']} videos, generated from brand.json by the
  master-brand-video-pipeline skill. Tokens are normative; prose is intent.
unit: the frame — 1920×1080 primary; 9:16, 1:1 and 4:5 documented
principle: brand atoms are sacred · one focal point per frame · numbers come from the script

colors:
{col}

typography:
{typ}

spacing:
  pad-x: "7cqw"
  pad-y: "9cqh"
  radius: "{R['radius']}px"

components:
  caption:
    background: "{C['captionBox']}"
    color: "{C['captionText']}"
    highlight: "{C['captionHighlight']}"
  end-card:
    cta: "{B.get('end_card', {}).get('cta', '')}"
    url: "{B.get('end_card', {}).get('url', B.get('url', ''))}"
---

# {B['name']} — {B.get('tagline', '')}

## Overview
{B.get('category', '')}. Audience: {B.get('audience', '')}.
Personality: {', '.join(vt.get('personality', []))}.

## Palette semantics
- `bg` is the ground; `fg` is the ink. `primary` is the one voltage colour: one primary element per frame.
- `accent` marks the active thing (spoken word, current item, the number that matters). `muted` is for support copy.
- Never pure white text on light footage; captions always sit on the caption box.

## The frame
- Safe area: 7% sides, 9% top/bottom on landscape; on 9:16 keep copy inside x 90–930, y 200–1600.
- Headline ≥ 84px at 1080 short side, support ≥ 44px. One focal point per frame.

## Logo
Use only the official files ({', '.join(v for k, v in logo.items() if k in ('light', 'dark', 'icon') and v)}). Minimum width {logo.get('min_width_px', 200)}px, clear space {logo.get('clearspace', '0.5× height')}.
Never: {'; '.join(logo.get('never', []))}.

## Motion personality
Energy: {B.get('motion', {}).get('energy', 'confident')}. Entrances {B.get('motion', {}).get('entrance_s', 0.6)}s with `{B.get('motion', {}).get('gsap_ease', 'power3.out')}`; stagger {B.get('motion', {}).get('stagger_s', 0.12)}s. Transition family: {B.get('motion', {}).get('transition', 'fade')} only.

## Say / avoid
- Say: {' '.join(vt.get('say', []))}
- Avoid: {'; '.join(vt.get('avoid', []))}
"""


def openmontage_yaml(B: dict, R: dict) -> str:
    C = R["colors"]
    F = R["fonts"]
    m = B.get("motion", {})
    a = B.get("audio", {})
    img = B.get("imagery", {})
    q = lambda s: json.dumps(str(s), ensure_ascii=False)  # noqa: E731
    avoid = ", ".join(img.get("avoid", []))
    return f"""# GENERATED by master-brand-video-pipeline/scripts/brand_tokens.py. Copy to OpenMontage/styles/{slug(B['name'])}.yaml
identity:
  name: {q(B['name'] + ' Brand')}
  category: brand
  mood: {q(', '.join(B.get('voice_and_tone', {}).get('personality', [])))}
  pace: {q(m.get('energy', 'moderate'))}
  best_for: {q('All ' + B['name'] + ' brand, product and social videos')}

visual_language:
  color_palette:
    primary: [{q(C['primary'])}, {q(C['secondary'])}]
    accent: [{q(C['accent'])}]
    background: {q(C['bg'])}
    text: {q(C['fg'])}
    muted: {q(C['muted'])}
  composition: one focal point per frame, generous safe margins
  texture: {q('film grain ' + str(B.get('shape', {}).get('grain', 0)) if B.get('shape', {}).get('grain') else 'clean, no grain')}

typography:
  headings:
    font: {q(F['heading']['family'])}
    weight: {F['heading']['weight']}
    tracking: {q(B.get('typography', {}).get('tracking_heading', '-0.02em'))}
  body:
    font: {q(F['body']['family'])}
    weight: {F['body']['weight']}
    line_height: 1.4
  code:
    font: {q(F.get('mono', F['body'])['family'])}
    weight: 400

motion:
  transitions: [{m.get('transition', 'fade')}]
  animation_style: {q('entrances ' + str(m.get('entrance_s', 0.6)) + 's ' + m.get('css_ease', 'ease-out') + ', no bounce')}
  pacing_rules:
    min_scene_hold_seconds: {m.get('min_scene_hold_s', 2.5)}
    max_scene_hold_seconds: 10
    text_card_hold_seconds: 3.5
    stat_card_hold_seconds: 3.0
    transition_duration_seconds: {m.get('transition_s', 0.4)}

audio:
  voice_style: {q(B.get('voice', {}).get('instruct', 'warm, clear'))}
  music_mood: {q(a.get('music_mood', ''))}
  music_volume: 0.08
  sfx_style: {q(a.get('sfx_style', ''))}

asset_generation:
  image_prompt_prefix: {q(img.get('image_prompt_prefix', ''))}
  image_negative_prompt: {q('text, letters, logos, watermark, ' + avoid)}
  consistency_anchors:
    - {q(C['primary'] + ' as the single accent colour')}
    - {q(img.get('style', ''))}
"""


def pireel_frame(B: dict, R: dict) -> str:
    C = R["colors"]
    pal = (f'{{ paper: "{C["bg"]}", panel: "{C["surface"]}", panel-2: "{C["secondary"]}", fg: "{C["fg"]}", muted: "{C["muted"]}", '
           f'accent: "{C["primary"]}", accent-2: "{C["accent"]}", line: "{C["line"]}", grid: "{C["line"]}", radius: "{R["radius"]}px", '
           f'shadow: "0 20px 60px rgb(0 0 0 / 0.45)", glow: "0 0 40px rgb(0 0 0 / 0)", font-head: "\'{R["fonts"]["heading"]["family"]}\', sans-serif" }}')
    return f"""---
id: {slug(B['name'])}
title: {B['name']}
summary: {B.get('tagline', '')}
icon: ◆
showcase: [title-card, big-number, list, cta, compare, quote]
palette: {pal}
version: 0.1.0
---

# {B['name']} — brand frame

{B.get('category', '')}. {B.get('audience', '')}

## Palette semantics
- `paper` is the ground, `fg` the ink. `accent` ({C['primary']}) is the one voltage colour; `accent-2` marks the active item.

## Signature
- Official logo only, on the end card and nowhere it would fight the speaker.
- One focal element per composition; captions on a dark box.

## Motion personality
{B.get('motion', {}).get('energy', 'confident')}: entrances {B.get('motion', {}).get('entrance_s', 0.6)}s, no bounce, one transition family ({B.get('motion', {}).get('transition', 'fade')}).

## Taboos
{'; '.join(B.get('voice_and_tone', {}).get('avoid', []) + B.get('logo', {}).get('never', []))}
"""


def brand_md(B: dict, R: dict) -> str:
    C = R["colors"]
    v = B.get("voice", {})
    a = B.get("audio", {})
    rows = "\n".join(f"| {k} | `{val}` |" for k, val in C.items())
    return f"""# {B['name']} — brand brief for video

Generated from brand.json. This is the BRAND.md every engine and agent reads (herk-edit-kit, HyperFrames, OpenMontage, Pireel).

**Tagline:** {B.get('tagline', '')}  ·  **URL:** {B.get('url', '')}
**Audience:** {B.get('audience', '')}
**Personality:** {', '.join(B.get('voice_and_tone', {}).get('personality', []))}

## Colours
| Role | Value |
|---|---|
{rows}

## Type
{chr(10).join(f"- {r}: {f['family']} {f['weight']}" for r, f in R['fonts'].items())}

## Logo rules
Official files only (sha256 in provenance.json). Never: {'; '.join(B.get('logo', {}).get('never', []))}.

## Voice
{v.get('provider', '')} profile "{v.get('profile', '')}", engine {v.get('engine', '')}, seed {v.get('seed', '')}. Direction: {v.get('instruct', '')}.
Consent on file: {v.get('consent_on_file', False)}. Disclose synthetic voice: {v.get('disclose_synthetic', True)}.

## Audio
Deliver at {a.get('lufs_target', -14)} LUFS integrated, true peak ≤ {a.get('true_peak_db', -1)} dBTP. Music bed {a.get('music_under_voice_db', 12)} dB under the voice.
Music: {a.get('music_mood', '')}. SFX: {a.get('sfx_style', '')}

## Claims
{B.get('claims', {}).get('policy', '')}

## Imagery
{B.get('imagery', {}).get('style', '')} Avoid: {', '.join(B.get('imagery', {}).get('avoid', []))}.
"""


# ------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("brand")
    ap.add_argument("--project", help="Project folder (default: parent of the brand folder)")
    ap.add_argument("--check", action="store_true", help="Validate only")
    a = ap.parse_args()

    bp = Path(a.brand).resolve()
    bdir = bp.parent
    B = read_json(bp)
    for k in ("name", "colors", "typography"):
        if k not in B:
            die(f"brand.json missing '{k}'")
    for k in ("primary", "bg", "fg"):
        if k not in B["colors"]:
            die(f"brand.json colors missing '{k}'")
    R = remotion_json(B)
    C = R["colors"]

    problems, notes = [], []
    for k, v in C.items():
        try:
            parse_color(v)
        except ValueError as e:
            problems.append(str(e))
    checks = [("fg on bg", C["fg"], C["bg"], 4.5), ("muted on bg", C["muted"], C["bg"], 3.0),
              ("caption text on caption box", C["captionText"], C["captionBox"], 4.5),
              ("primary on bg (large text/shapes)", C["primary"], C["bg"], 3.0),
              ("bg on primary (CTA label)", C["bg"], C["primary"], 4.5)]
    for name, fg, bg, need in checks:
        try:
            r = contrast(fg, bg, base=C["bg"])
            (notes if r >= need else problems).append(f"{name}: {r:.2f}:1 (need ≥ {need})")
        except ValueError:
            pass
    prov = {"brand_json": {"path": str(bp), "sha256": sha256(bp)}, "logos": {}, "fonts": {}}
    logo = B.get("logo", {})
    for k in ("light", "dark", "icon"):
        if logo.get(k):
            p = bdir / logo[k]
            if p.exists():
                prov["logos"][k] = {"file": logo[k], "sha256": sha256(p)}
            else:
                problems.append(f"logo.{k} missing: {p}")
    if not logo.get("light") and not logo.get("dark"):
        notes.append("No logo files: end cards fall back to the brand name in the heading font. Never generate or redraw a logo.")
    for role in ("heading", "body", "mono"):
        for f in B["typography"].get(role, {}).get("files", []) or []:
            p = bdir / f["file"]
            if p.exists():
                prov["fonts"][f["file"]] = sha256(p)
            else:
                problems.append(f"font file missing: {p} (renders will fall back to {B['typography'][role].get('fallback', 'system fonts')})")

    # Only reference files that exist, so renders never block on a missing font or logo.
    present_fonts = {Path(f["file"]).name for role in ("heading", "body", "mono")
                     for f in B["typography"].get(role, {}).get("files", []) or [] if (bdir / f["file"]).exists()}
    R["fontFiles"] = [f for f in R["fontFiles"] if f["file"] in present_fonts]
    for k in ("light", "dark"):
        if logo.get(k) and not (bdir / logo[k]).exists():
            R["logo"][k] = None

    report = "# Brand check\n\n" + "\n".join(f"- OK  {n}" for n in notes) + "\n" + "\n".join(f"- FIX {p}" for p in problems) + "\n"
    print(report)
    if a.check:
        sys.exit(1 if problems else 0)

    proj = Path(a.project).resolve() if a.project else bdir.parent
    out = bdir / "tokens"
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "remotion.brand.json", R)
    write_text(out / "brand.css", brand_css(B, R, "assets/brand/fonts/"))
    write_text(out / "frame.md", frame_md(B, R))
    write_text(out / "openmontage-style.yaml", openmontage_yaml(B, R))
    write_text(out / "pireel-frame.md", pireel_frame(B, R))
    write_text(out / "BRAND.md", brand_md(B, R))
    write_json(out / "captions.style.json", {**B.get("captions", {}), "font": R["fonts"]["heading"], "resolved": {
        "box": C["captionBox"], "text": C["captionText"], "highlight": C["captionHighlight"]}})
    write_json(out / "provenance.json", prov)
    write_text(out / "check.md", report)

    def copy_assets(dst_root: Path) -> None:
        for role in ("heading", "body", "mono"):
            for f in B["typography"].get(role, {}).get("files", []) or []:
                p = bdir / f["file"]
                if p.exists():
                    (dst_root / "fonts").mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, dst_root / "fonts" / p.name)
        for k in ("light", "dark", "icon"):
            if logo.get(k) and (bdir / logo[k]).exists():
                (dst_root / "logo").mkdir(parents=True, exist_ok=True)
                shutil.copy2(bdir / logo[k], dst_root / "logo" / Path(logo[k]).name)

    rem = proj / "remotion"
    if (rem / "src").is_dir():
        write_json(rem / "src" / "brand.json", R)
        copy_assets(rem / "public" / "brand")
        print(f"REMOTION: {rem / 'src' / 'brand.json'} + public/brand/")
    hf = proj / "hyperframes"
    if hf.is_dir():
        write_text(hf / "brand.css", brand_css(B, R, "assets/brand/fonts/"))
        if not (hf / "frame.md").exists():
            write_text(hf / "frame.md", frame_md(B, R))
        copy_assets(hf / "assets" / "brand")
        print(f"HYPERFRAMES: {hf / 'brand.css'} + assets/brand/ (+ frame.md if absent)")
    print(f"TOKENS: {out}")
    if problems:
        eprint(f"{len(problems)} brand issue(s) to fix: see {out / 'check.md'}")


if __name__ == "__main__":
    main()
