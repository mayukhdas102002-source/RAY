# 02 · Brand films and stories

Longer, emotional pieces that build belief: brand films, manifestos, origin stories, customer case studies, testimonials, impact stories and mini-documentaries.

## Formats

| Format | Length | Primary aspect | Core material |
|---|---|---|---|
| Brand film / manifesto | 45–120 s | 16:9 (+ 9:16 cut) | VO-led, cinematic plates or footage, music-driven |
| Origin story | 60–180 s | 16:9 | Founder interview + archive + recreations |
| Case study | 60–150 s | 16:9 + 1:1 | Customer interview, product in use, numbers |
| Testimonial | 30–90 s | 9:16 / 1:1 | Real customer, consented, lightly cut |
| Impact story (nonprofit) | 60–180 s | 16:9 + 9:16 | Beneficiary voice (consented, dignified), outcome data |
| Mini-doc | 3–10 min | 16:9 | Interviews, verité, archive, chapters |

## Intake extras

Who is the protagonist (customer, founder, community, employee)? What changed for them? What's true and provable? Interview availability and consents; archive/photo rights; the brand's belief in one line.

## Workflow

1. **Belief and story** (G): write the brand belief, the tension it resolves, and the protagonist's change. Pick a structure from `core/craft.md` (hero's small journey, manifesto, interview arc).
2. **Research & references:** read references (Read module); collect facts and sources for any numbers.
3. **Interview plan** (footage-led): question list that draws out situation → turning point → result → feeling; shoot/remote-record notes (clean audio first, room tone 30 s).
4. **Paper edit:** transcribe interviews (`ray tool transcribe_words raw/interview.mp4`), select bites in `SCRIPT.md` with source timecodes; build the arc with ~20% more than needed. → **G**
5. **Cut the talk track:** herk chain for each interview (`modules/produce/references/herk-edit-kit.md`): silences, reviewed mistake cuts, lock `edit/clean.mp4` + transcript.
6. **Coverage:** B-roll list per bite (real first); AI plates for recreations/metaphors via Direct (labelled if realistic), archive with rights logged.
7. **VO-led films instead:** script → brand clone or human VO → `timeline_from_vo`.
8. **Assemble:** Remotion/HyperFrames for titles, lower-thirds (`modules/produce/templates/hyperframes-brand/compositions/brand-lower-third.html`), data cards, chapters; music edited to the arc. Preview → **G**
9. **Mix & finish:** dialogue clean-up (Audio module: noise, EQ, levelling), music 12 dB under speech, room tone under cuts, grade.
10. **Versions:** 16:9 master, 60/30 s cutdowns, 9:16 clips per strong bite (`playbooks/03-social-short-form.md`).

## Craft rules

- Specific beats general: one real moment > five adjectives.
- Let moments breathe (4–8 s holds on emotional beats); speed is for social cutdowns.
- Speakers on screen for credibility; never erase them behind B-roll for long; lower-third on first appearance only.
- Numbers on their own beat with a source line.
- Dignity in impact stories: no pity framing; the beneficiary is the hero, not the organisation.

## Sound

Dialogue intelligibility first (Audio module transcription/clean-up pipeline). Music that builds over the arc; drop out before the turning point; land the resolution. −14 LUFS web; broadcast spec if aired.

## Deliverables

Master + cutdowns + captions (SRT) + chapter markers (mini-docs) + stills + release/consent log.

## Accelerators

Storage connectors for footage pulls; Pireel for hands-on clip selection and variants; OpenMontage `documentary-montage` for archive-led pieces; Higgsfield for recreations (with disclosure).
