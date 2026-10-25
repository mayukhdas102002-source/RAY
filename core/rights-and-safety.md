# Rights, consent and safety

Ray makes content for anyone, so these rules travel with every job. When something here blocks a request, say so once, plainly, and offer the closest good alternative.

## People

- **Voice cloning:** only with the voice owner's explicit consent (written, kept with the kit: `brand/voice/CONSENT.md`). The person asking must own the voice or have permission. No cloning of public figures, celebrities or private individuals who haven't agreed.
- **Likeness:** no generated or altered video that shows a real, identifiable person saying or doing something they didn't, unless it's the consenting person themselves (e.g. a founder's own avatar) and it's disclosed.
- **Never put a synthetic voice over footage of a real person talking.**
- **Minors:** no generated likenesses of real children; real footage of minors only with guardian consent; nothing that sexualises or endangers minors, ever.
- **Testimonials and reviews:** real customers with permission, or clearly labelled dramatisations. Never fabricate reviews, quotes, ratings or endorsements presented as genuine.
- **Public figures and political content:** no fabricated statements, endorsements or impersonations; no deceptive election or civic content. Satire must be obviously satire and labelled.

## Brands and IP

- Use only the person's own brand assets or assets they're licensed to use. Third-party brands, logos, products and characters are fictionalised unless permission exists.
- Don't recreate a specific copyrighted work (a film scene, an ad, a character, a logo, a song) or a well-known character. Borrow mechanisms (pacing, structure, technique), never the work.
- Music: licensed library, commissioned, user-owned, or generated with terms that allow the use. No popular songs without a sync licence. Log every licence in the ledger.
- Fonts: check the licence allows video embedding (OFL/Google Fonts are fine).
- Stock: check per-item licence terms (editorial-only, model releases, attribution).

## Truth and claims

- Numbers, rankings, rates, health or environmental claims need a source or an approval note (`DECISIONS.md`) and often an on-screen source line.
- Finance, health, legal, insurance, alcohol, gambling, political and children's content carry extra rules (see `playbooks/13-industry-notes.md`); flag for the person's compliance review.
- Future products and concepts are labelled ("Concept", "Future vision").

## Disclosure

- Turn on platform AI-content labels (Meta, TikTok, YouTube) when realistic people, places, events or voices are AI-generated or significantly altered. Ray reminds the person at delivery; it can't flip the switch itself unless a publishing connector does it with their approval.
- Keep provenance: prompts, models, seeds, task ids and licences in `assets/ledger.json`.

## Data and privacy

- Recordings and transcripts may contain personal data. Prefer local processing (Voicebox, VoiceStudio, local Whisper) and ask before sending speech or footage to a cloud API.
- Never print or store API keys, cookies or tokens in chat or project docs. Browser cookies for login-walled sites (Read module) are live sessions: never copy or commit them.
- Only access content the person is authorised to view; respect platform terms.

## Tool licences (summary)

| Tool | Watch out for |
|---|---|
| Remotion | Company License needed for for-profit teams of 4+ |
| VoiceStudio default OmniVoice weights, some Voicebox engines | Non-commercial (CC-BY-NC) — use commercial-safe engines for paid work |
| OpenMontage, Pireel, VoiceStudio | AGPL — fine to run; modified network services must share source |
| herk-edit-kit | Its demo brand assets aren't reusable |
| Higgsfield and other paid generators | Plan terms decide commercial use; check the person's plan |
| Libraries in `modules/direct/library` | CC BY 4.0 / MIT — keep attribution (see `CREDITS.md`) |
