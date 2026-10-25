# Credits and licences

RAY combines four production skills (each keeps its own `CREDITS.md`/licence notes inside `modules/`) with new material written for RAY (`SKILL.md`, `core/`, `playbooks/`, `connectors/`, `scripts/ray.py`, `templates/`).

## Modules

| Module | Origin | Third-party material inside |
|---|---|---|
| `modules/read` | claude vidreader | Approach adapted from MaximRomanMd/video-reader and s8zvp68zyn-ctrl/claude-video-reader (both MIT) |
| `modules/direct` | AI Video Buddy (AI Director) | `library/visual-skills` by Serge Shima (CC BY 4.0); `library/higgsfield` by O-Side Media (MIT); fonts in `modules/direct/templates/remotion-starter` (SIL OFL 1.1). See `modules/direct/CREDITS.md` and `modules/direct/LICENSES/` |
| `modules/produce` | master-brand-video-pipeline | Orchestrates Remotion (Remotion License), HyperFrames (Apache-2.0), OpenMontage (AGPL-3.0), herk-edit-kit (MIT + use permission), Pireel (AGPL-3.0), Voicebox (MIT), VoiceStudio (AGPL-3.0). See `modules/produce/CREDITS.md` |
| `modules/audio` | master-ai-audio-director | Built around audio-analyzer-rs, dsp-synth-expert (MIT) and Claude-Transcription-Plugin; see `modules/audio/references/setup.md` |

## External services

Higgsfield, voice, avatar, music and other generation services are used through the person's own accounts and connectors, under their terms. RAY does not bundle their code.

Keep the attribution files in `modules/direct/LICENSES/` when sharing RAY.
