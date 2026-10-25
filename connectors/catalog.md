# Connector catalog: MCP servers Ray's modules know

Local or self-hosted servers whose tools were verified from their source (October 2026). For any other connector, read its tool schemas at run time and follow `connectors/README.md`.

| Server | Add it | Tools Ray uses | Module notes |
|---|---|---|---|
| **Voicebox** (local voice studio) | `claude mcp add voicebox --transport http --url http://127.0.0.1:17493/mcp --header "X-Voicebox-Client-Id: claude"` | `voicebox_speak`, `voicebox_transcribe`, `voicebox_list_profiles`, `voicebox_list_captures` | Scripted batch work is better through `ray tool voice` (per-scene files, seeds, manifest). `modules/produce/references/voice.md` |
| **VoiceStudio** (local voice studio) | MCP at `http://localhost:3900/mcp/` (keep the trailing slash); stdio shim `python -m backend.mcp_shim` | `generate_speech`, `clone_voice`, `design_voice`, `describe_voice`, `transcribe`, `list_voices`, `list_personalities`, `list_languages`, `check_health` | Set `OMNIVOICE_MCP_OUTPUT_MODE=files` and `OMNIVOICE_MCP_BASE_PATH` so audio files don't flood the chat. Non-commercial default engine: choose `voxcpm2`/`cosyvoice` for paid work. |
| **audio-analyzer** (`audio-analyzer-rs`) | `.mcpb` bundle for Claude Desktop, or `claude mcp add --scope user audio-analyzer -- <path>/mcp-server` | `audio_info`, `spectral_features`, `harmonic_analysis`, `rhythm_analysis`, `full_analysis`, `compare` | The Audio module's "ears". `modules/audio/references/setup.md` |
| **Pireel** (hosted editor) | `claude plugin marketplace add pireel/pireel-agent && claude plugin install pireel@pireel-marketplace`, or `claude mcp add --transport http pireel https://pireel.com/api/studio/mcp`; OAuth login | `get_state`, `import_media`, `add_clips`, `remove_silence`, `set_captions`, `set_clip_framing`, `add_transition`, `compose_component`, `export`… | Credits on charged tools; editor tab must be open. `modules/produce/references/pireel.md` |
| **Higgsfield** (hosted generation) | Custom connector `https://mcp.higgsfield.ai/mcp` | `models_explore`, `balance`, `generate_image`, `generate_video` (`get_cost`), `media_upload_widget`, `media_import_url`, `list_voices`, `get_workflow_instructions`… | `connectors/higgsfield.md` |
| **Remotion** | `@remotion/mcp`, WebMCP in Remotion Studio | Studio/docs helpers | Ray drives Remotion via CLI/scripts; the MCP is optional. `modules/produce/references/remotion.md` |
| **HyperFrames** | Claude Code plugin `hyperframes@hyperframes` (skills, not MCP) | `/hyperframes` router and workflows | `modules/produce/references/hyperframes.md` |

## Cloud services commonly attached (capability-based)

Ray treats these by capability; tool names vary by provider, so always read the schemas:

- **Storage** (Drive, Dropbox, Box, OneDrive/SharePoint): search and download source footage, logos, fonts and decks into the project; upload deliverables only when asked.
- **Design** (Figma, Canva): pull brand tokens, assets and frames; create companion statics only when asked.
- **Communication** (Slack, Teams, Gmail/Outlook): draft review requests with links and timestamps; send only on explicit request.
- **Docs/notes** (Notion, Google Docs, Confluence): read briefs and brand guidelines; write the client write-up there if that's where the person works.
- **Generation** (video, image, voice, music, avatar platforms): follow the Higgsfield pattern — schema → quote → sample → approval → batch → ledger.
- **Publishing/scheduling**: prepare uploads and copy; publish only on explicit request, with AI-content labels set where required.
