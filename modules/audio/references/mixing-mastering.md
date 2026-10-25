# Mixing and Mastering Reference

Starting points only. Always confirm against measurements and the reference.

## Diagnostic playbook (measurement -> action)

| Finding | Likely cause | Action (starting values) |
|---|---|---|
| Low-mid (250-500 Hz) high vs reference | Mud from guitars/keys/pads/vocal bus | Broad cut 2-3 dB around 250-400 Hz, Q 1.0-1.5, on offending buses first |
| Bass band heavy, kick unclear | Kick/bass masking | Sidechain bass to kick (3-6 dB reduction, attack 1-5 ms, release 80-150 ms), or EQ carve opposite notches |
| Sub-bass energy above 60 Hz target, wide | Stereo sub | High-pass sides below 100-120 Hz or use mono bass below 120 Hz |
| Upper-mid harsh (2-4 kHz) | Over-bright lead/vocal, distortion | Dynamic EQ cut 2-4 dB at 3 kHz, Q 2; check saturation stage |
| Sibilant brilliance (6-10 kHz) | Vocal esses | De-esser centred 6-8 kHz, 3-6 dB max reduction |
| Dull, low centroid and rolloff | Lack of highs/air | High shelf +1.5-3 dB at 10-12 kHz, or harmonic excite; fix source if noisy |
| Low crest factor, low LRA | Over-compression/limiting | Reduce limiter gain by 1-3 dB; slower attack/release on bus compression |
| Phase correlation dips negative | Out-of-phase stereo widener, mic phase | Check mono sum, flip polarity on offending track, reduce widening |
| Mono compatibility drop | Wide reverbs/chorus on important elements | Keep fundamentals mono; widen harmonics only |
| True peak > -1 dBTP | Inter-sample overs | Set limiter ceiling to -1.0 dBTP (-2.0 for conservative lossy delivery) |
| Louder than platform target | Over-limiting for no gain | Back off to target LUFS to preserve punch |

## Priority order for fixes

1. Balance and arrangement (levels, masking).
2. Low end (sub, kick/bass relationship, mono below ~120 Hz).
3. Tone (mud, harshness, air).
4. Dynamics (bus compression, transients).
5. Stereo image.
6. Loudness and ceiling.

## Mix bus chain (typical)

1. Corrective EQ (HPF 20-30 Hz, targeted cuts).
2. Glue compression: ratio 1.5-2:1, attack 10-30 ms, release auto or 100-300 ms, 1-2 dB gain reduction.
3. Colour: subtle saturation/tape.
4. Stereo tools: mid/side EQ if needed.

## Mastering chain (typical)

1. Gain staging with 3-6 dB of headroom into the chain.
2. Corrective EQ (linear phase if surgical).
3. Optional multiband compression for problem bands only.
4. Stereo width adjustments (never at the expense of mono compatibility).
5. Limiter: ceiling -1.0 dBTP, gain to reach the LUFS target; stop when transients degrade.
6. Final analysis: LUFS, dBTP, LRA, phase, band balance, A/B at matched loudness.

## Loudness targets by destination

| Destination | Target |
|---|---|
| Spotify, YouTube | -14 LUFS integrated, -1 dBTP |
| Apple Music | -16 LUFS integrated, -1 dBTP |
| Podcast (stereo) | around -16 LUFS; mono around -19 LUFS; -1 dBTP |
| Broadcast (EBU R128) | -23 LUFS, +/-0.5 LU, -1 dBTP |
| Club / DJ master | Louder is fine; keep true peak under 0 dBTP and preserve transients |

Confirm current platform specs with the user or the platform's documentation before final delivery.

## Delivery checklist

- Integrated LUFS and true peak within target.
- Mono-sum check: no major level or tonal loss.
- Phase correlation positive for most of the track.
- No clipping or inter-sample overs.
- Start/end trimmed, fades applied, metadata and artwork set.
- Archive: 24-bit WAV master plus platform-specific encodes.
- Re-analysis report saved with the files.

## Psychoacoustics reminders

- Equal-loudness (Fletcher-Munson): bass and treble sound weaker at low listening levels; mix and judge at moderate level and level-match when comparing.
- Masking: sounds in the same critical band mask each other; separate by EQ, panning, time (sidechain) or timbre.
- Stereo perception: low frequencies localize poorly, so keep them centred; widen with harmonics and high frequencies.
- Louder tends to be heard as better; always level-match A/B.
