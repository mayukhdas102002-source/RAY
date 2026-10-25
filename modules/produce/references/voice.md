# Voice: brand voiceover with Voicebox and VoiceStudio

Both are desktop apps with a local FastAPI backend, running on the user's computer (reach them from `device_bash`, never from the cloud container). `scripts/voice.py` drives either one.

## Which one

| Need | Pick |
|---|---|
| Commercial brand VO, English + 9 major languages, NVIDIA/AMD/Intel/CPU on Windows | **Voicebox**, engine `qwen` (Qwen3-TTS 1.7B, Apache-2.0 weights), `instruct` for delivery |
| 23 languages / long reads / expressive tags | Voicebox `chatterbox` (23 langs), `tada` 3B (700 s+ coherent), `chatterbox_turbo` (only engine that honours `[laugh] [sigh] [whispering]…`; English) |
| 48 kHz light engine | Voicebox `luxtts` (English) |
| Word timestamps for captions | **VoiceStudio** `/v1/audio/transcriptions` (WhisperX), even if Voicebox spoke the line |
| Fit a line to an exact length | VoiceStudio `duration` field (`voice.py generate --fit-duration` with `target_vo_seconds`) |
| Hundreds of languages, dubbing a finished video | VoiceStudio (dubbing pipeline: separation → ASR → translate → per-segment TTS → QC → SRT/VTT/ASS + stems) |
| Commercial work on VoiceStudio | engines `voxcpm2` (48 kHz, design) or `cosyvoice` (Apache-2.0). **Not** `omnivoice` (CC-BY-NC weights, the default). Check `indextts2`'s licence first. |
| No brand voice yet, just a scratch read | `npx hyperframes tts script.txt --voice af_heart -o vo.wav` (Kokoro, local) or OpenMontage Piper |

## Cloning the brand voice (once per brand)

Consent first: written permission from the person whose voice it is, stored with the brand kit (`voice.consent_on_file: true`).

Reference audio: clean, dry, one speaker, no music, consistent level, delivered **in the brand's energy** (a flat reference gives a flat clone).
- Voicebox: 2–30 s accepted, **10–30 s** recommended; `reference_text` must match exactly; add several samples (different registers) for robustness.
- VoiceStudio/OmniVoice: **3–10 s** is the sweet spot; uses ≤20 s; a transcript with a >20 s clip is rejected (trim clip and text together); empty transcript costs an ASR pass.

```bash
python scripts/voice.py clone --provider voicebox --name "Homely VO" --audio brand/voice/ref_20s.wav --ref-text "exact words…" --language en
python scripts/voice.py clone --provider voicestudio --name "Homely VO" --audio brand/voice/ref_8s.wav --ref-text "exact words…"
python scripts/voice.py list --provider voicebox
```
Store the profile name/id, engine, model size and a **pinned seed** in `brand.json → voice`. VoiceStudio can lock a liked take: `POST /profiles/{id}/lock` (Form `history_id`, `seed`).

## Generating VO

```bash
python scripts/voice.py generate --text "Home loans, minus the runaround." --brand brand/brand.json --out vo/sample.wav   # sample → Gate 4a
python scripts/voice.py generate --scenes scenes.json --brand brand/brand.json --out vo/                                  # one WAV per scene
python scripts/voice.py generate --scenes scenes.json --brand brand/brand.json --only S03,S05                             # redo lines
python scripts/transcribe_words.py vo/ --script scenes.json                                                               # vo/S01.words.json …
```
- One file per scene keeps timeline offsets exact and makes pickups cheap.
- Lexicon (`brand.json → voice.lexicon`) respells words for the TTS only; captions keep the real spelling (`--script` alignment restores it).
- Script hygiene: pauses as punctuation/line breaks; no ElevenLabs-style tags (most engines read them aloud); VoiceStudio supports `[pause 400ms]` and inline pronunciation `[[Nuh-VAD-uh]]`; numbers written the way they should be said.
- Voicebox `normalize` is on by default (fine; the mix re-levels). VoiceStudio defaults to the `broadcast` mastering preset; `voice.py` sends `raw` so the mix stage owns processing.
- Re-transcribe every final VO against the script: missing or mangled words are the most common TTS failure.

## API cheat sheet

**Voicebox** `http://127.0.0.1:17493` (Docker `:17600`), JSON, no auth, Swagger `/docs`.
| Call | Body / notes |
|---|---|
| `GET /health` | GPU/backends |
| `GET /profiles` · `POST /profiles` | `{name, language, voice_type: cloned\|preset\|designed, default_engine, preset_engine, preset_voice_id, design_prompt}` |
| `POST /profiles/{id}/samples` | multipart `file` + `reference_text` |
| `POST /generate/stream` | `{profile_id, text, language, seed, model_size: 1.7B\|0.6B\|1B\|3B, instruct, engine, normalize, max_chunk_chars, crossfade_ms, effects_chain}` → WAV bytes, synchronous; **400 if the model isn't downloaded** |
| `POST /generate` → `GET /history/{id}` (poll status) → `GET /audio/{id}` | Async path; also triggers model download. `GET /generate/{id}/status` is SSE. |
| `POST /v1/audio/speech` | OpenAI-compatible `{model, input, voice: profile name/id, response_format: wav…, speed, instructions}` (newer builds) |
| `POST /transcribe` | multipart `file` (+`language`, `model`) → `{text, duration}` only (no word times) |
| Stories | `/stories`, `/stories/{id}/items` (`generation_id`, `start_time_ms`, `track`), `/stories/{id}/export-audio?format=wav\|mp3\|m4b` |
Rules: preset profiles accept only their preset engine; cloned profiles accept `qwen|luxtts|chatterbox|chatterbox_turbo|tada|omnivoice`; `instruct` only on Qwen; output 24 kHz mono (LuxTTS 48 kHz); jobs queue serially.

**VoiceStudio** `http://127.0.0.1:3900`, multipart forms, loopback needs no auth (Docker/LAN: `Authorization: Bearer $OMNIVOICE_API_KEY`), live contract at `/openapi.json`.
| Call | Fields |
|---|---|
| `GET /health`, `GET /profiles`, `GET /engines/tts` | |
| `POST /profiles` | `name`, `kind=clone\|design`, `ref_audio` (file), `ref_text`, `language` (default Auto), `seed`, `instruct`, `vd_states` (design) |
| `POST /generate` | `text`, `profile_id`, `engine`, `language`, `seed`, `duration` (overrides speed), `speed`, `num_step` (16; 32 = quality), `guidance_scale`, `denoise`, `effect_preset` (broadcast default; raw), `wav_bits 16\|24\|32`, `max_chunk_chars`, `crossfade_ms`, `pronounce`, `stream` → WAV + headers `X-Audio-Id`, `X-Audio-Duration`, `X-Seed`, `X-OmniVoice-Dropped-Chunks`. 503 = busy (`Retry-After: 30`); 403 = licence not accepted. |
| `POST /v1/audio/speech` | OpenAI-compatible (default format **mp3**; check status before saving) |
| `POST /v1/audio/transcriptions` | `file`, `model=whisper-1`, `response_format=verbose_json`, `timestamp_granularities[]=word` → `{words:[{word,start,end}]}`; also `srt`/`vtt`. 409 = no ASR model installed. |
| `POST /convert` | re-voice audio with a profile (`audio`, `profile_id`, `match_duration`) |
| Dubbing / long-form | `/dub/upload` … `/dub/srt\|vtt\|ass/{job}`, `/dub/export-stems/{job}`; `/audiobook`, `/longform/render`, `/batch/enqueue` |
Only one TTS engine stays resident; the first call after start is slow (load + compile). AudioSeal watermarking may be on per user setting.

## MCP (optional, for chatting with the apps directly)

- Voicebox: `voicebox_speak`, `voicebox_transcribe`, `voicebox_list_profiles`, `voicebox_list_captures` at `http://127.0.0.1:17493/mcp` (underscore names since 0.6).
- VoiceStudio: `generate_speech`, `clone_voice`, `design_voice`, `describe_voice`, `transcribe`, `list_voices`… at `http://localhost:3900/mcp/`; set `OMNIVOICE_MCP_OUTPUT_MODE=files` so audio doesn't enter the chat context.

## Ethics and disclosure

Never clone without consent; never put a synthetic voice over footage of a real person talking; mark AI voice in platform disclosures where required; keep the consent record and the profile's reference clip with the brand kit.
