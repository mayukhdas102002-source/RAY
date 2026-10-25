# Speech and Transcription Pipeline

Condensed from danielrosehill/Claude-Transcription-Plugin. Pipeline:

audio -> preprocess -> transcribe -> post-process -> combine -> export

## Defaults and choices

Default to cloud processing (Gemini for transcription, Auphonic for cleanup) when API keys exist; otherwise use local tools. Ask the user before sending recordings to any third-party service.

## 1. Preprocess

| Task | Options |
|---|---|
| Noise removal | Auphonic (default), ElevenLabs, Dolby.io, or local DeepFilterNet |
| Silence trimming | Silero VAD or ffmpeg `silenceremove` |
| Normalization | Mono, 16 kHz resample, compression for upload size |
| Speaker samples | Extract short clean clips per speaker to help label diarization |

Example ffmpeg normalization:

```
ffmpeg -i input.wav -ac 1 -ar 16000 -c:a pcm_s16le speech_16k.wav
```

Check the cleanup result with the analyzer: loudness, noise floor (low band and brilliance energy during gaps), crest factor.

## 2. Transcribe

| Engine | When |
|---|---|
| Gemini API | Default; raw or cleaned variants |
| AssemblyAI | Timestamps and speaker diarization |
| Local Whisper | Offline/private |

For long recordings, chunk by silence boundaries and keep timestamps continuous.

## 3. Post-process

- Remove filler words (um, uh, repeated starts) unless a verbatim transcript is requested.
- Add section headers and logical paragraphs.
- Generate variants on request: summary, blog post, meeting notes (decisions, actions, owners), show notes with chapter timestamps.
- Preserve speaker labels and timestamps in the verbatim version.

## 4. Combine and export

- Combine selected variants into one document (Markdown, or Typst -> PDF).
- Deliver via file save, email, Google Drive or clipboard as the user prefers.

## Working rules

- Always keep the original audio and the raw transcript; derive cleaned versions from them.
- Tell the user which variants were produced and where they are saved.
- Flag low-confidence passages (crosstalk, noise) instead of guessing.
