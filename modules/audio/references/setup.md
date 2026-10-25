# Setup

## 1. Audio analyzer MCP (the "ears")

Source: https://github.com/JuzzyDee/audio-analyzer-rs

- **Claude Desktop (easiest)**: download the `.mcpb` bundle for your OS from the GitHub Releases page and open it.
- **Homebrew (macOS)**:
  ```
  brew tap JuzzyDee/tap
  brew install audio-analyzer
  claude mcp add --scope user audio-analyzer -- $(which audio-analyzer-mcp)
  ```
- **Manual**: download the `mcp-server` binary from Releases and run `claude mcp add --scope user audio-analyzer -- /path/to/mcp-server`
- **From source** (needs Rust):
  ```
  git clone https://github.com/JuzzyDee/audio-analyzer-rs.git
  cd audio-analyzer-rs
  cargo build --release
  claude mcp add --scope user audio-analyzer -- target/release/mcp-server
  ```
- **CLI**: `cargo run --bin cli -- song.mp3` and `cargo run --bin cli -- compare mix_v1.mp3 mix_v2.mp3`

## 2. Transcription tooling (the "hands")

Source: https://github.com/danielrosehill/Claude-Transcription-Plugin

- Required: `ffmpeg`, Python 3 with `uv`.
- Optional API keys: Gemini (transcription), Auphonic / ElevenLabs / Dolby.io (noise removal), AssemblyAI (diarization).
- Optional local: Whisper, DeepFilterNet, Silero VAD.
- For the full plugin experience install the repo as a Claude Code plugin.

## 3. DSP knowledge (the "brain")

Source: https://github.com/liorfrenkel/dsp-synth-expert (MIT). This skill carries a condensed version in `references/sound-design-dsp.md`. For synth-specific parameter files (for example Surge XT parameters and factory presets), run Claude Code with `claude --plugin-dir /path/to/dsp-synth-expert`.

## 4. Install (RAY module)

Copy the `master-ai-audio-director` folder into your skills directory (for example `~/.claude/skills/`), or upload it as a skill in Claude settings. The folder must contain `SKILL.md` at its top level.

## Fallbacks without the MCP

- `ffmpeg -i in.wav -af ebur128=peak=true -f null -` for LUFS, LRA and true peak.
- `ffmpeg -i in.wav -af astats -f null -` for RMS, peak and crest factor.
- Python: `librosa` (spectral features, tempo, chroma), `pyloudnorm` (LUFS).
