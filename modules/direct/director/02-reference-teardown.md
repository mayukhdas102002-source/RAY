# 02 · Reference teardown

When the user shares reference ads, analyse them properly before pitching. A teardown is evidence, not taste.

## Method

1. **Probe each file.** Duration, resolution, fps: `tools/probe.sh <file>`.
2. **Cut log.** Scene-change timestamps give the number of shots and the average shot length: `tools/cut_log.sh <file> [threshold=0.25]`.
3. **Dense contact sheet.** About 30 timestamped frames per ad, so every cut and transition is visible: `tools/contact_sheet.sh <file> [frames=30]`. For a :90, sample about every 2s. For a :15, sample every 0.5s. Twelve frames is too few to see how an ad is built.
4. **Key frames.** Four frames per ad (open, product moment, wow, end card) for the write-up page: `tools/keyframes.sh <file> t1 t2 t3 t4`.
5. **Audio.** If speech-to-text is available, transcribe. If not, say so and read the on-screen text and supers. Great ads put the message on screen anyway.

## What to extract per ad

| Field | Question |
|---|---|
| Length · shots · avg shot | e.g. :15 · 12 shots · 1.25s |
| Story | One sentence: who wants what, what changes |
| The wow | The single heightened device (if any) and how long it lasts |
| Product moment | When the product appears, as what (a real screen?), and the exact words on it |
| Copy | Count of supers or VO lines, and the brand line |
| Look | Light, lens feel, grade, casting |
| Lesson for us | One sentence we can apply |

## Patterns found in the Zillow and Revolut-style spots (reusable)

- One real person, one real moment, recognisable in two seconds. No setup exposition.
- At most one surreal beat, about a second, played as a joke about speed or ease. Longer metaphors lose the audience.
- The phone is the hinge: a tap, then the world changes.
- One screen, three to five words ("You're pre-approved!", "Your loan has been approved").
- Show the after, not the process. No application forms on screen.
- At most two lines of copy. The brand line ends it.
- Warm practical light, lived-in homes, real casting, 35mm feel.
- Cut rhythm: :15 ≈ 8–12 shots, :30 ≈ 8–11 shots, :90 ≈ 20–25 shots. Montage shots go under 1.5s, story shots 2.5–4s.
- Revolut-style: the app itself is the hero, with confident, fast UI motion and bold type. Keep this for product moments only, built in Remotion.

## Write-up format

A page with, per ad: 4 thumbnails, the stats line, the story, the wow, the product moment, and the lesson. Then "Why ours didn't land" (if revising), then the rules we'll follow, then the concepts. See `examples/zillow-teardown.md`.
