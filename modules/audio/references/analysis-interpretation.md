# Analysis Interpretation Guide

How to read output from the audio-analyzer MCP (`audio_info`, `spectral_features`, `harmonic_analysis`, `rhythm_analysis`, `full_analysis`, `compare`).

## Resolution parameter

| Value | Density | Use for |
|---|---|---|
| (none) | Summary stats only | Quick check |
| `low` | ~0.5 points/sec | Broad overview of long files |
| `medium` | ~1 point/sec | Default; about 180 rows for a 3-minute track |
| `high` | ~4 points/sec | Transitions, drops, problem spots |
| numeric string | Custom | Fine control |

Use `start_time` / `end_time` on `full_analysis` to zoom into a section instead of raising resolution for the whole file.

## Metrics and what they mean

| Metric | Reading |
|---|---|
| Spectral centroid ("brightness") | Higher = brighter. Compare against reference, not absolute numbers |
| Spectral bandwidth ("richness") | Higher = fuller, more complex; low = thin or simple |
| Spectral rolloff | Frequency below which most energy sits; low rolloff = dark or dull |
| Spectral flatness | Near 0 = tonal; near 1 = noisy |
| Spectral contrast (dB) | Higher = clear and defined; lower = muddy or dull |
| MFCCs (13) | Timbre fingerprint; use for similarity between sounds, not for judging quality |
| Zero crossing rate | Texture; high = noisy/bright/percussive |
| RMS | Average energy |
| Crest factor | Peak-to-RMS. Very low = over-compressed or over-limited |
| Integrated LUFS (EBU R128) | Perceived loudness over the whole file |
| True peak (dBTP) | Inter-sample peak; keep headroom for lossy encodes |
| LRA | Loudness range; low = flat dynamics |
| Phase correlation | +1 = mono compatible; around 0 = very wide/decorrelated; negative = cancellation |
| Stereo width (M/S ratio) | How much energy is in Side vs Mid |
| L/R balance | Should be near centre unless intentional |
| Mono compatibility | Per-frame; check dips against time-series |
| Chromagram / key | Pitch class content; key is estimated (Krumhansl-Schmuckler) with a confidence score |
| Tonnetz | Harmonic relationships; use for chord/key movement |
| BPM, beat positions | With confidence; stability coefficient 0 = free, 1 = locked |
| HPSS ratio | Harmonic vs percussive balance |
| Attack sharpness, onset density | How punchy and busy the material is |
| Section boundaries | Labels show which features triggered (energy / spectral / texture) |

## Frequency bands (7 producer-standard)

| Band | Range | Typical issue to look for |
|---|---|---|
| Sub-bass | 20-60 Hz | Rumble, excess unusable energy; check mono below ~120 Hz |
| Bass | 60-250 Hz | Weight and punch; kick/bass masking |
| Low-mid | 250-500 Hz | Mud/boxiness |
| Mid | 500 Hz-2 kHz | Body, vocal and instrument presence, honk |
| Upper-mid | 2-4 kHz | Aggression, intelligibility, ear fatigue |
| Presence | 4-6 kHz | Definition, vocal clarity |
| Brilliance | 6-20 kHz | Air, sparkle, harshness, sibilance |

Compare band energy against the reference or genre expectation; a band 3 dB or more away from the reference deserves a note.

## Confidence thresholds

| Measure | Reliable | Be cautious |
|---|---|---|
| Section boundary confidence | >= 0.75 | < 0.75: treat as a suggestion |
| Tempo stability | > 0.9 = locked, metronomic | < 0.7 = drift or rubato; BPM mean may mislead |
| Key confidence | High and clearly ahead of the runner-up | Close runner-up (relative major/minor ambiguity) |
| Tempo estimate | Matches beat grid | Half/double-time errors are common; sanity-check |

## Streaming loudness targets

| Platform | Target | Note |
|---|---|---|
| Spotify | -14 LUFS | Reports gain applied; "turned UP" or "DOWN" |
| YouTube | -14 LUFS | Same |
| Apple Music | -16 LUFS | Same |

If a track is louder than the target, it is turned down, so extra limiting costs dynamics for no gain.

## Compare output - order to read it

1. Integrated loudness delta (level-match before judging anything else).
2. Dynamics (crest factor, LRA).
3. Per-band energy shifts: list the largest.
4. Stereo width and phase correlation gaps.
5. Key and tempo match or mismatch, with confidence.
