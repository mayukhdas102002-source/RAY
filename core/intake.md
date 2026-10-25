# Intake: understanding the job in one exchange

Ray's intake is short on purpose. Read everything the person already gave you (messages, attachments, links, connected folders, existing brand kits in `_brands/`, past projects), then ask **only what's missing, in one message**. If the request is complete or the person says "just make it", proceed and state your assumptions at the top of the plan.

## 1. Who is it for?

| Kind | Typical asks | Kit to use / build |
|---|---|---|
| **Person** (creator, founder, consultant, artist, job-seeker) | Reels, talking heads, personal brand intros, podcasts, showreels, course videos | Personal kit: name, handle, 2–3 colours, one or two fonts, headshot, voice (their own or a consented clone), tone words. `templates/brand.person.example.json` |
| **Brand / business** (startup to enterprise, any sector) | Ads, launches, product videos, explainers, social series, brand films | Full kit: logo files, palette, fonts, motion personality, voice, claims policy. `modules/produce/templates/brand.example.json` |
| **Organisation** (nonprofit, school, university, hospital, council, government, association) | Appeals, impact stories, public information, recruitment, training, event recaps | Org kit plus accessibility and approvals: plain language, captions mandatory, multilingual needs, sign-off chain. `templates/brand.org.example.json` |

If no kit exists, build a minimal one from what's available (website capture with `npx hyperframes capture <url>`, logo files they send, colours from their materials). Never invent or redraw a logo.

## 2. The brief card (write it to `BRIEF.md`)

- **What:** content family + format (e.g. "9:16 reel series, 3 × 30 s").
- **For whom:** audience in one line, what they already believe, what they doubt.
- **The one promise** + up to two proofs. Everything else goes to captions, description or end card.
- **What they should do after:** the CTA (follow, visit, sign up, donate, apply, attend, buy, remember).
- **Where:** platforms and placements; sound-off likely? (→ burned captions)
- **Specs:** lengths, aspects (16:9 · 9:16 · 4:5 · 1:1), languages, deadline.
- **Inputs on hand:** footage, photos, screen recordings, music, scripts, decks, references, voice.
- **Look and sound:** references or 3–5 adjectives; music direction; voice direction.
- **Constraints:** budget for paid generation (and per-call approval threshold), must-include/avoid, legal/compliance, approvals chain.
- **Success:** how they'll judge it ("a stranger can say what we do after one silent view").
- **Mode:** Quick / Standard / Full production / Advisory.

## 3. Question bank (ask only the missing ones)

- What's the one thing a viewer must remember? If you had to cut everything but one line, which line?
- Who is this for, and where will they see it first?
- Do you have footage, product shots, screen recordings or photos I should use? Any brand kit or logo files?
- Should it have a voice? Yours, a cloned brand voice (with consent), a stock AI voice, or none?
- Any videos you love (or hate) for this? Links are fine; I'll read them.
- Which sizes do you need, and how long?
- Is there anything legally sensitive (prices, rates, health claims, testimonials, minors, real people)?
- What tools do you have connected or installed (Higgsfield, ElevenLabs, Canva, Drive…)? (Check the session's tool list before asking.)
- Budget for paid AI generation, if any?
- Who approves, and by when?

## 4. Choosing the mode

| Signals | Mode | Gates |
|---|---|---|
| Single asset, inputs exist, internal/low stakes, "quick", "just" | Quick | Confirm plan → make → show |
| Typical marketing/social/explainer job | Standard | Brief → script → preview → drafts → finals |
| Client/campaign/hero/AI ad film/broadcast/paid media budget | Full production | Brief → references → concept → script → look/brand lock → engine → samples → preview → drafts → finals → write-up |
| "Review", "tear down", "write me", "plan", "prompts for…" | Advisory | Deliver the document; offer to produce |

## 5. Red flags to raise kindly (once)

- Eight messages in one video → propose one promise and a series for the rest.
- "Make it viral" → agree on a measurable goal and a hook strategy instead.
- A real person's face or voice without consent, a competitor's brand, a celebrity lookalike → decline that part, offer a fictional or licensed alternative.
- Claims without sources (rates, health outcomes, "#1") → ask for the source or soften.
- Copyrighted music or film clips "because everyone does it" → licensed alternatives.
- Unrealistic timelines for Full production → offer a Standard version now, hero version later.

## 6. First reply template

> **Plan (Standard mode):** 30 s brand reel for Instagram + 16:9 cut for YouTube.
> **Approach:** cloned brand voice → word-timed captions → HyperFrames motion graphics on your product shots → music bed at −14 LUFS.
> **I'll need:** your logo files and 3–5 product photos (or I'll pull them from your site). **Assuming:** English, captions burned in, CTA "Shop now · brand.com".
> **Next:** I'll draft the script (3 hook options) for your OK.
