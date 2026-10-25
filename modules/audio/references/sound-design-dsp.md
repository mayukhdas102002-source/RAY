# Sound Design and DSP Reference

Condensed from the dsp-synth-expert knowledge base. For deep dives, the full source repo (liorfrenkel/dsp-synth-expert, MIT) has about 30 files on filters, oscillators, synthesis architectures, effects, psychoacoustics and genre recipes. Answer from knowledge first; verify synth-specific parameters when a specific synth is named.

## Pre-design questions
Synth/DAW platform; genre and reference; constraints; existing patches to start from. Skip any already answered.

## Ten sound design principles

1. **Movement over perfection**: micro-drift, filter breathing, subtle imperfection.
2. **Transient obsession**: the first 50-100 ms defines character; layer pitch envelopes and filter attacks.
3. **Harmonic layering**: separate sub / body / air zones.
4. **Saturation as texture**: tube warmth, subtle bit-crush, Chebyshev waveshaping.
5. **Frequency intelligence**: high-pass aggressively (300-600 Hz for non-bass parts); design in the mix, not in solo.
6. **"Talking" quality**: formant filters, vowel morphing.
7. **Spatial design**: mono fundamentals, widened harmonics (M/S processing).
8. **Negative space and dynamics**: natural decay, velocity response, reverb trails.
9. **Timbral surprise**: evolution at 5-10 seconds; delayed LFO or a secondary envelope stage.
10. **Cultural context**: organic/synthetic hybrids, vintage digital revival (DX7, PPG, SP-1200), melodic techno minimalism, deconstructed club production.

## Response format for any patch

- Platform-agnostic principle, then platform implementation.
- Signal chain: Osc -> Mixer -> Filter -> Amp -> FX -> Bus role.
- Every parameter with units (Hz, dB, %, ms, semitones, ratio).
- Modulation matrix: source -> destination -> amount.
- Layering plan (sub / body / top) and mix notes (EQ cuts, sidechain, stereo).

## Filters

**Biquad (RBJ cookbook)**. With sample rate Fs, cutoff f0, quality Q:

- w0 = 2*pi*f0/Fs, alpha = sin(w0)/(2*Q), cos(w0)
- Low-pass: b0 = (1-cos w0)/2, b1 = 1-cos w0, b2 = (1-cos w0)/2, a0 = 1+alpha, a1 = -2 cos w0, a2 = 1-alpha
- High-pass: b0 = (1+cos w0)/2, b1 = -(1+cos w0), b2 = (1+cos w0)/2, same a0, a1, a2
- Band-pass (constant 0 dB peak): b0 = alpha, b1 = 0, b2 = -alpha
- Normalize all coefficients by a0. Difference equation: y[n] = b0 x[n] + b1 x[n-1] + b2 x[n-2] - a1 y[n-1] - a2 y[n-2]
- Butterworth response: Q = 0.707

**Moog ladder**: four cascaded one-pole low-pass stages with global feedback; 24 dB/oct; resonance reduces passband gain; self-oscillation near feedback gain 4; add tanh saturation per stage for warmth.

**State-variable**: simultaneous LP/BP/HP outputs; good for modulation and morphing.

## Oscillators and aliasing

- Naive saw/square alias badly. Use **PolyBLEP** (cheap, good), **BLIT/BLEP** (higher quality), or band-limited **wavetables** with mipmaps.
- Wavetable playback: interpolate with linear (cheap), cubic (better), or sinc (best); oversample 2-4x for FM and heavy waveshaping.
- Phase accumulator: phase += f/Fs, wrap at 1.0.

## Synthesis architectures

| Type | Key ideas |
|---|---|
| Subtractive | Rich oscillators -> filter -> amp; envelopes and LFO for motion |
| FM (DX7) | Operators in algorithms; carrier/modulator ratios set harmonic structure (integer ratios = harmonic, non-integer = bell/metallic); modulator level (index) sets brightness; 32 algorithms |
| Additive | Sum of partials with individual envelopes; precise but costly |
| Granular | Short grains (5-100 ms) with position/pitch/density randomization; textures, pads |
| Physical modeling | Karplus-Strong: noise burst into a delay line with a low-pass in the feedback loop; delay length sets pitch |
| Modulation | Envelopes, LFOs, velocity, keytracking, macros; keep modulation slow for organic motion |

## Effects

- **Compression**: gain computer with threshold, ratio, knee; attack/release smoothing; sidechain filter. Use for glue (low ratio), control (medium) or ducking (sidechain).
- **Parametric EQ**: peaking biquad; Q about 0.7-1.5 broad, above 3 surgical.
- **Reverb**: Schroeder (parallel combs into series allpass) or Freeverb; pre-delay 10-40 ms for clarity; high-pass the reverb return at 200-400 Hz and low-pass at 6-10 kHz.
- **Chorus / flanger**: modulated short delay (chorus 15-30 ms, flanger 1-10 ms) with LFO 0.1-3 Hz.
- **Distortion**: soft clip (tanh), wavefold, bit-crush; oversample to avoid aliasing; filter before and after.

## Genre recipes (starting points)

| Sound | Core recipe |
|---|---|
| 70s Moog bass | Saw + square oscillators, 24 dB ladder low-pass, short filter envelope with moderate resonance, mono, slight detune |
| 80s DX7 electric piano | FM with 1:1 carrier/modulator plus a high-ratio bell operator; fast modulator decay for the tine attack; velocity to modulation index |
| 90s acid (TB-303) | Saw or square, resonant diode-ladder low-pass, accent adds filter envelope amount and level, slide = portamento with legato |
| Reese bass | Two or three detuned saws, slow phasing, low-pass, then saturation and a stereo-safe widener above 200 Hz; keep sub mono |
| Trap 808 | Sine with a pitch envelope (quick drop of about 12 semitones over 20-50 ms), long amp decay, saturation so it translates on small speakers, tune to the key |
| Dubstep growl | Saw/FM source, formant or comb filter modulated by a tempo-synced LFO, distortion, resampling and layering |
| Techno rumble | Kick tail reverb, low-pass at about 150-300 Hz, ducking against the next kick, mono |
| Ambient granular pad | Long samples, grain size 50-200 ms, high density, slow position drift, large reverb, high-pass about 200 Hz |

## Measure-to-design links

Use the audio analyzer on a rendered patch or a reference sample:

- Low centroid + low rolloff -> add harmonics (saturation, filter opening, brighter oscillator).
- High HPSS percussive ratio + sharp attack -> transient-focused; keep amp attack at 0-5 ms.
- Low spectral flatness -> tonal; high -> noisy; match to the intended character.
- Narrow stereo width -> add M/S widening of harmonics, not of the sub.
