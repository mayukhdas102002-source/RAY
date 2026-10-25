#!/usr/bin/env python3
"""Generate a HyperFrames composition ("templated mode") from the locked timeline + brand tokens.

  python scripts/timeline_from_vo.py scenes.json --hyperframes hyperframes/      # first
  python scripts/hf_build.py hyperframes/ --size 1920x1080
  python scripts/hf_build.py hyperframes/ --size 1080x1920 --into hyperframes-9x16/   # one project per aspect
  cd hyperframes && npx hyperframes lint && npx hyperframes preview

Reads   hyperframes/timeline.json, hyperframes/transcript.json (optional), hyperframes/brand.css,
        brand/tokens/captions.style.json (optional, for caption colours)
Writes  hyperframes/index.html (standalone root, no <template>) with:
        - one .clip <section> per scene, crossfading by --overlap seconds (entrance = the transition; no exits)
        - word-timed caption groups with the active word highlighted
        - one <audio id> per VO line and the music bed (for preview; master the final mix with audio.py and mux)
        - exactly one paused GSAP timeline registered as window.__timelines["main"]

This is the fast, on-brand baseline. For hero/launch work switch to atelier mode: hand-author the
composition (see references/hyperframes.md) and keep this file only as timing reference.
Regenerating overwrites the file only if it still carries the generator marker (or with --force).
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import die, load_words, read_json, write_text  # noqa: E402

MARK = "<!-- generated-by: master-brand-video-pipeline/hf_build.py -->"
GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"


def ensure_gsap(H: Path) -> str:
    """Vendor GSAP locally (deterministic renders, offline, no CDN at render time). Falls back to the CDN URL."""
    dst = H / "assets" / "vendor" / "gsap.min.js"
    if dst.exists():
        return "assets/vendor/gsap.min.js"
    try:
        import io
        import tarfile
        import urllib.request
        with urllib.request.urlopen("https://registry.npmjs.org/gsap/-/gsap-3.14.2.tgz", timeout=60) as r:
            data = r.read()
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
            member = tf.extractfile("package/dist/gsap.min.js")
            if member is None:
                raise OSError("gsap.min.js not in tarball")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(member.read())
        return "assets/vendor/gsap.min.js"
    except Exception as e:  # noqa: BLE001
        print(f"note: could not vendor GSAP ({e}); using the jsDelivr CDN", file=sys.stderr)
        return GSAP


def esc(s: str | None) -> str:
    return html.escape(s or "", quote=True)


def group_words(words: list[dict], max_words: int, gap: float = 0.6) -> list[list[dict]]:
    groups, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or w["start"] - cur[-1]["end"] > gap or re.search(r"[.!?;:,]$", cur[-1]["text"])):
            groups.append(cur)
            cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    return groups


def scene_inner(s: dict, sid: str) -> str:
    k = s.get("kind", "statement")
    kicker = f'<div class="kicker">{esc(s.get("kicker"))}</div>' if s.get("kicker") else ""
    head = f'<h1 class="headline">{esc(s.get("headline"))}</h1>' if s.get("headline") else ""
    body = f'<p class="body">{esc(s.get("body"))}</p>' if s.get("body") else ""
    if k == "title":
        return f'<div class="content center">{kicker}<h1 class="headline hero">{esc(s.get("headline"))}</h1>{body}</div>'
    if k == "stat":
        return f'<div class="content">{kicker}<div class="stat">{esc(s.get("stat"))}</div>{head}{body}</div>'
    if k == "list":
        items = "".join(f'<li class="item"><span class="num">{i + 1}</span><span>{esc(t)}</span></li>' for i, t in enumerate(s.get("items") or []))
        return f'<div class="content">{head}<ol class="list">{items}</ol></div>'
    if k == "quote":
        return f'<div class="content"><div class="quote-mark">“</div>{head}{body}</div>'
    if k == "endCard":
        return '<div class="content center endcard">__ENDCARD__</div>'
    if k in ("footage", "image", "lowerThird"):
        media = s.get("media")
        if media and re.search(r"\.(png|jpe?g|webp|avif)$", media, re.I):
            m = f'<img class="media" src="{esc(media)}" alt="">'
        elif media:
            m = (f'<div class="media-wrap"><video id="{sid}-video" class="media" src="{esc(media)}" muted playsinline '
                 f'data-start="{s["_hf_start"]:.3f}" data-duration="{s["_hf_dur"]:.3f}" data-media-start="{s.get("mediaStart", 0)}" '
                 f'data-track-index="{s["_track"] + 5}"></video></div>')
        else:
            m = '<div class="media placeholder"></div>'
        lt = ""
        if k == "lowerThird" and (s.get("name") or s.get("headline")):
            lt = (f'<div class="lower-third"><div class="lt-name">{esc(s.get("name") or s.get("headline"))}</div>'
                  f'<div class="lt-role">{esc(s.get("role") or s.get("body") or "")}</div></div>')
        return f'{m}{lt}'
    return f'<div class="content"><div class="bar"></div>{kicker}{head}{body}</div>'


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("hfdir")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--overlap", type=float, default=0.4, help="Crossfade length between scenes (s)")
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--words", type=int, help="Words per caption group (default 3 vertical / 6 landscape)")
    ap.add_argument("--music-volume", type=float, default=0.25)
    ap.add_argument("--brand-tokens", help="brand/tokens folder (default: ../brand/tokens)")
    ap.add_argument("--into", help="Build a separate project for another aspect (copies brand, assets, timeline). "
                    "HyperFrames allows exactly one root index.html per project.")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    H = Path(a.hfdir)
    if a.into:
        D = Path(a.into)
        D.mkdir(parents=True, exist_ok=True)
        for f in ("brand.css", "frame.md", "hyperframes.json", "timeline.json", "transcript.json"):
            if (H / f).exists():
                shutil.copy2(H / f, D / f)
        if (H / "assets").is_dir():
            shutil.copytree(H / "assets", D / "assets", dirs_exist_ok=True)
        H = D
    T = read_json(H / "timeline.json")
    W, Hh = map(int, a.size.lower().split("x"))
    vertical = Hh / W > 1.3
    u = min(W, Hh) / 1080
    total = float(T["total"])
    out = H / "index.html"
    if out.exists() and MARK not in out.read_text(encoding="utf-8", errors="ignore") and not a.force:
        die(f"{out} was hand-authored (no generator marker). Use --into another folder or --force.")

    tok_dir = Path(a.brand_tokens) if a.brand_tokens else H.parent / "brand" / "tokens"
    capstyle = read_json(tok_dir / "captions.style.json") if (tok_dir / "captions.style.json").exists() else {}
    rem = read_json(tok_dir / "remotion.brand.json") if (tok_dir / "remotion.brand.json").exists() else {}
    hl = capstyle.get("resolved", {}).get("highlight", "#FFB36B")
    txt = capstyle.get("resolved", {}).get("text", "#FFFFFF")
    upper = capstyle.get("upper", True)
    brand_name = rem.get("name", "Brand")
    endcard = rem.get("endCard", {})
    tagline = rem.get("tagline", "")
    logo = (rem.get("logo") or {}).get("light")

    pad = ({"l": 90 * W / 1080, "r": 150 * W / 1080, "t": 200 * Hh / 1920, "b": 320 * Hh / 1920} if vertical
           else {"l": W * 0.07, "r": W * 0.07, "t": Hh * 0.09, "b": Hh * 0.09})

    css_rules = f"""
    .wrap {{ position: absolute; inset: 0; background: var(--color-bg); opacity: 0; }}
    .kind-quote .wrap {{ background: var(--color-surface); }}
    .content {{ position: absolute; left: {pad['l']:.0f}px; right: {pad['r']:.0f}px; top: {pad['t']:.0f}px; bottom: {pad['b']:.0f}px;
               display: flex; flex-direction: column; justify-content: center; align-items: flex-start; }}
    .content.center {{ align-items: center; text-align: center; }}
    .bar {{ width: {140 * u:.0f}px; height: {10 * u:.0f}px; border-radius: {10 * u:.0f}px; background: var(--color-primary); margin-bottom: {36 * u:.0f}px; }}
    .kicker {{ font-family: var(--font-mono); font-weight: var(--font-mono-weight); font-size: {34 * u:.0f}px; letter-spacing: 0.18em;
              text-transform: uppercase; color: var(--color-accent); margin-bottom: {28 * u:.0f}px; }}
    .headline {{ font-family: var(--font-heading); font-weight: var(--font-heading-weight); font-size: {(96 if vertical else 92) * u:.0f}px;
                line-height: 1.05; letter-spacing: var(--tracking-heading); color: var(--color-fg); margin: 0; max-width: 18ch; }}
    .headline.hero {{ font-size: {(128 if vertical else 120) * u:.0f}px; }}
    .body {{ font-family: var(--font-body); font-weight: var(--font-body-weight); font-size: {46 * u:.0f}px; line-height: 1.3;
            color: var(--color-muted); margin: {32 * u:.0f}px 0 0; max-width: 28ch; }}
    .stat {{ font-family: var(--font-heading); font-weight: 800; font-size: {(300 if vertical else 260) * u:.0f}px; line-height: 0.9;
            letter-spacing: -0.04em; color: var(--color-primary); }}
    .list {{ list-style: none; padding: 0; margin: {48 * u:.0f}px 0 0; display: flex; flex-direction: column; gap: {28 * u:.0f}px; }}
    .item {{ display: flex; align-items: center; gap: {28 * u:.0f}px; font-family: var(--font-body); font-weight: var(--font-body-weight);
            font-size: {50 * u:.0f}px; color: var(--color-fg); }}
    .num {{ width: {64 * u:.0f}px; height: {64 * u:.0f}px; border-radius: 50%; background: var(--color-primary); color: var(--color-bg);
           display: flex; align-items: center; justify-content: center; font-family: var(--font-mono); font-size: {30 * u:.0f}px; flex-shrink: 0; }}
    .quote-mark {{ font-family: var(--font-heading); font-size: {170 * u:.0f}px; line-height: 0.6; color: var(--color-primary); }}
    .media-wrap, .media {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
    .media.placeholder {{ background: var(--color-surface); }}
    .lower-third {{ position: absolute; left: {pad['l']:.0f}px; bottom: {pad['b'] * 1.2:.0f}px; background: var(--color-caption-box);
                   border-left: {10 * u:.0f}px solid var(--color-primary); border-radius: {11 * u:.0f}px; padding: {22 * u:.0f}px {34 * u:.0f}px; }}
    .lt-name {{ font-family: var(--font-heading); font-weight: var(--font-heading-weight); font-size: {48 * u:.0f}px; color: var(--color-fg); }}
    .lt-role {{ font-family: var(--font-body); font-size: {32 * u:.0f}px; color: var(--color-muted); }}
    .logo {{ width: {420 * u:.0f}px; height: auto; }}
    .wordmark {{ font-family: var(--font-heading); font-weight: var(--font-heading-weight); font-size: {120 * u:.0f}px; color: var(--color-fg); }}
    .tagline {{ font-family: var(--font-body); font-size: {46 * u:.0f}px; color: var(--color-muted); margin: {36 * u:.0f}px 0 0; }}
    .cta {{ margin-top: {56 * u:.0f}px; padding: {20 * u:.0f}px {44 * u:.0f}px; border-radius: 999px; background: var(--color-primary);
           color: var(--color-bg); font-family: var(--font-heading); font-weight: var(--font-heading-weight); font-size: {41 * u:.0f}px; }}
    .legal {{ position: absolute; bottom: 0; font-family: var(--font-body); font-size: {22 * u:.0f}px; color: var(--color-muted); }}
"""

    def scoped(cid: str) -> str:
        # Prefix every rule with the composition root id so sub-compositions never leak styles.
        out_lines = []
        for line in css_rules.splitlines():
            m = re.match(r"(\s*)([^{]+)\{(.*)", line)
            if m and not line.strip().startswith(("display", "font", "line", "text", "color", "letter", "border", "box", "padding", "margin")):
                sels = ", ".join(f"#{cid} {x.strip()}" for x in m.group(2).split(","))
                out_lines.append(f"{m.group(1)}{sels} {{{m.group(3)}")
            else:
                out_lines.append(line)
        return "\n".join(out_lines)

    gsap_src = ensure_gsap(H)
    comp_dir = H / "compositions"
    comp_dir.mkdir(parents=True, exist_ok=True)
    suffix = ""
    hosts, audios = [], []
    scenes = T["scenes"]
    for i, s in enumerate(scenes):
        cid = f"scene-{re.sub(r'[^A-Za-z0-9_-]', '', s['id'])}{suffix}"
        ov = a.overlap if i > 0 else 0.0
        s["_hf_start"] = max(0.0, s["start"] - ov)
        s["_hf_dur"] = s["duration"] + ov
        s["_track"] = 1 + (i % 2)
        local = dict(s)
        local["_hf_start"], local["_track"] = 0.0, 0
        inner = scene_inner(local, cid)
        if "__ENDCARD__" in inner:
            logo_html = (f'<img class="logo" src="assets/brand/logo/{esc(Path(logo).name)}" alt="{esc(brand_name)}">' if logo
                         else f'<div class="wordmark">{esc(brand_name)}</div>')
            inner = inner.replace("__ENDCARD__", f'{logo_html}<p class="tagline">{esc(tagline)}</p>'
                                  f'<div class="cta">{esc(endcard.get("cta", ""))} · {esc(endcard.get("url", ""))}</div>'
                                  + (f'<p class="legal">{esc(endcard.get("legal"))}</p>' if endcard.get("legal") else ""))
        js = [f'    tl.fromTo("#{cid} .wrap", {{opacity: 0}}, {{opacity: 1, duration: {max(ov, 0.01):.2f}, ease: "none"}}, 0);']
        sel_order = [".bar", ".kicker", ".stat", ".quote-mark", ".headline", ".body", ".list .item", ".logo, .wordmark", ".tagline", ".cta", ".legal", ".lower-third"]
        k = 0
        for sel in sel_order:
            names = [c.strip().split(" ")[-1].lstrip(".") for c in sel.split(",")]
            if any(re.search(rf'class="[^"]*\b{n}\b', inner) for n in names):
                full = ", ".join(f"#{cid} {x.strip()}" for x in sel.split(","))
                stagger = ", stagger: 0.12" if "item" in sel else ""
                js.append(f'    tl.fromTo("{full}", {{y: {40 * u:.0f}, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.6, ease: "power3.out"{stagger}}}, {ov + 0.05 + 0.12 * k:.3f});')
                k += 1
        if s.get("kind") == "image" and s.get("media"):
            js.append(f'    tl.fromTo("#{cid} .media", {{scale: 1.04}}, {{scale: 1.12, duration: {s["_hf_dur"]:.3f}, ease: "none"}}, 0);')
        sub = f"""<template>
  <div id="{cid}" class="kind-{esc(s.get('kind', 'statement'))}" data-composition-id="{cid}" data-width="{W}" data-height="{Hh}" data-duration="{s['_hf_dur']:.3f}">
    <style>
    #{cid} {{ position: absolute; inset: 0; }}
{scoped(cid)}
    </style>
    <div class="wrap">{inner}</div>
    <script>
    (function () {{
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    tl.to({{}}, {{ duration: {s['_hf_dur']:.3f} }}, 0);
    window.__timelines["{cid}"] = tl;
    }})();
    </script>
  </div>
</template>
"""
        write_text(comp_dir / f"{cid}.html", MARK + "\n" + sub)
        hosts.append(f'  <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
                     f'data-start="{s["_hf_start"]:.3f}" data-duration="{s["_hf_dur"]:.3f}" data-width="{W}" data-height="{Hh}" '
                     f'data-track-index="{s["_track"]}" style="z-index:{10 + i}"></div>')
        if s.get("vo"):
            vd = f' data-duration="{float(s["voDuration"]):.3f}"' if s.get("voDuration") else ""
            audios.append(f'  <audio id="vo-{esc(s["id"])}" src="{esc(s["vo"])}" data-start="{s["start"] + float(s.get("voDelay", 0)):.3f}"{vd} '
                          f'data-track-index="{30 + (i % 2)}" data-volume="{s.get("voVolume", 1)}"></audio>')
    if T.get("music") and T["music"].get("src"):
        audios.append(f'  <audio id="music-bed" src="{esc(T["music"]["src"])}" data-start="0" data-duration="{total:.3f}" '
                      f'data-track-index="33" data-volume="{T["music"].get("volume", a.music_volume)}"></audio>')

    # Captions: one sub-composition spanning the film; groups never straddle a scene cut.
    caps = []
    tp = H / "transcript.json"
    if not a.no_captions and tp.exists():
        words = load_words(str(tp))["words"]
        cuts = [float(sc["start"]) for sc in scenes[1:]]
        groups = []
        for g in group_words(words, a.words or (3 if vertical else 6)):
            cur = [g[0]]
            for w in g[1:]:
                if any(cur[-1]["end"] <= c <= w["start"] + 1e-6 for c in cuts):
                    groups.append(cur)
                    cur = []
                cur.append(w)
            groups.append(cur)
        for gi, g in enumerate(groups):
            caps.append([gi, g, max(0.0, g[0]["start"] - 0.066), g[-1]["end"] + 0.2])
        for idx in range(len(caps) - 1):
            caps[idx][3] = min(caps[idx][3], caps[idx + 1][2])
        ccid = f"captions{suffix}"
        items, cjs = [], []
        for gi, g, st, en in caps:
            spans = " ".join(f'<span class="w" id="{ccid}-w{gi}-{wi}">{esc(w["text"].upper() if upper else w["text"])}</span>' for wi, w in enumerate(g))
            items.append(f'    <p id="{ccid}-g{gi}" class="clip cap" data-start="{st:.3f}" data-duration="{max(0.05, en - st):.3f}" data-track-index="0">'
                         f'<span class="cap-box">{spans}</span></p>')
            for wi, w in enumerate(g):
                cjs.append(f'    tl.set("#{ccid}-w{gi}-{wi}", {{color: "{hl}"}}, {w["start"]:.3f}); tl.set("#{ccid}-w{gi}-{wi}", {{color: "{txt}"}}, {w["end"]:.3f});')
        sub = f"""<template>
  <div id="{ccid}" data-composition-id="{ccid}" data-width="{W}" data-height="{Hh}" data-duration="{total:.3f}">
    <style>
    #{ccid} {{ position: absolute; inset: 0; pointer-events: none; }}
    #{ccid} .cap {{ position: absolute; inset: 0; margin: 0; display: flex; justify-content: center; align-items: flex-end;
           padding: 0 {pad['r']:.0f}px {pad['b'] * (1 if vertical else 0.9):.0f}px {pad['l']:.0f}px; box-sizing: border-box; }}
    #{ccid} .cap-box {{ background: var(--color-caption-box); border: {1.5 * u:.1f}px solid var(--color-line); border-radius: {16 * u:.0f}px;
               padding: {14 * u:.0f}px {26 * u:.0f}px; font-family: var(--font-heading); font-weight: 800; font-size: {(64 if vertical else 54) * u:.0f}px;
               line-height: 1.15; text-align: center; color: {txt}; }}
    </style>
{chr(10).join(items)}
    <script>
    (function () {{
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(cjs)}
    tl.to({{}}, {{ duration: {total:.3f} }}, 0);
    window.__timelines["{ccid}"] = tl;
    }})();
    </script>
  </div>
</template>
"""
        write_text(comp_dir / f"{ccid}.html", MARK + "\n" + sub)
        hosts.append(f'  <div id="{ccid}" data-composition-id="{ccid}" data-composition-src="compositions/{ccid}.html" data-start="0" '
                     f'data-duration="{total:.3f}" data-width="{W}" data-height="{Hh}" data-track-index="20" data-track-kind="captions" style="z-index:900"></div>')

    doc = f"""<!doctype html>
{MARK}
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width={W}, height={Hh}">
  <title>{esc(T.get('title', 'Brand film'))}</title>
  <link rel="stylesheet" href="brand.css">
  <script src="{gsap_src}"></script>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; width: {W}px; height: {Hh}px; overflow: hidden; background: var(--color-bg); }}
    #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--color-bg); }}
  </style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{Hh}" data-duration="{total:.3f}" data-fps="{T.get('fps', 30)}">
{chr(10).join(hosts)}
{chr(10).join(audios)}
</div>
<script>
  const tl = gsap.timeline({{ paused: true }});
  tl.to({{}}, {{ duration: {total:.3f} }}, 0); // scene and caption timelines are nested automatically
  window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
    write_text(out, doc)
    print(f"HYPERFRAMES: {out} + {len(scenes)} scene sub-compositions{' + captions' if caps else ''} in compositions/ "
          f"({W}x{Hh}, {total:.2f}s). Next: npx hyperframes lint && npx hyperframes preview")


if __name__ == "__main__":
    main()
