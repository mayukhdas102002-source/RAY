# Setup: installing and checking the toolchain

Install only what the chosen route needs. Run `python scripts/doctor.py --tools-dir <toolchain folder>` before and after.

## Layout on the user's machine

```
AI Production/
├── master-brand-video-pipeline/   ← this skill
├── RAY/                           ← this skill (modules/direct, read, produce, audio)
├── _toolchain/                    ← clones (set env BVP_TOOLS to this path)
│   ├── OpenMontage/
│   ├── herk-edit-kit/
│   └── pireel/
├── _brands/<brand>/brand.json (+ fonts/, logo/)   ← reusable brand kits
└── <Client> - <Project>/          ← one folder per video (new_project.py)
```

Remotion and HyperFrames install per project through npm/npx; they don't need clones.

## Base requirements

| Need | Version | Windows | macOS | Linux |
|---|---|---|---|---|
| Node.js | **22+** (HyperFrames, herk, OpenMontage's HF path; Remotion v5 will require 22) | `winget install OpenJS.NodeJS.LTS` | `brew install node@22` | nvm / NodeSource |
| FFmpeg + ffprobe | **7+** recommended (herk's cutters use `-/filter_complex`; Remotion bundles its own) | `winget install Gyan.FFmpeg` | `brew install ffmpeg` | static build (Ubuntu 22.04 apt ships 4.4) |
| Python | 3.10+ (3.12 for Voicebox from source; OpenMontage pins 3.10) | `winget install Python.Python.3.12` | `brew install python@3.12` | distro / pyenv |
| Git | any | `winget install Git.Git` | Xcode CLT | apt |
| uv | optional (OpenMontage, VoiceStudio, HF caption scripts) | `pip install uv` | same | same |
| pnpm | Pireel OSS only | `corepack enable` | same | same |
| Chrome | Remotion and HyperFrames download a headless shell; or point at one: `--browser-executable` (Remotion), `HYPERFRAMES_BROWSER_PATH` (HF) | | | |

## Remotion (per project)

```bash
cd "<project>/remotion" && npm install          # starter pinned to remotion 4.0.537, React 19.2.3
npx remotion studio                             # http://localhost:3000/<CompId>
npx remotion versions                           # all @remotion/* must be the same exact version
npx remotion add @remotion/transitions          # add packages at the matching version (never npm i @remotion/x@latest)
npx remotion skills add                         # optional: Remotion's official agent skills into the project
npx remotion browser ensure                     # pre-download Chrome Headless Shell
```
New blank project instead of the starter: `npx create-video@latest --yes --blank --no-tailwind .` (empty folder only).
**Licence:** free for individuals, non-profits and for-profit teams of up to 3 people; a Company License (remotion.pro/license) otherwise. Same features either way.

## HyperFrames (per project)

```bash
npx hyperframes doctor            # Node, FFmpeg, Chrome, memory, /dev/shm, whisper-cpp, Kokoro
npx hyperframes browser ensure
npx hyperframes skills update     # optional: HeyGen's agent skills (router /hyperframes + workflows)
# Claude Code plugin alternative:
#   claude plugin marketplace add heygen-com/hyperframes && claude plugin install hyperframes@hyperframes
```
Optional local extras the doctor lists: `pip install kokoro-onnx soundfile` (TTS), whisper.cpp (transcription), `npx hyperframes models install parakeet` (fast English ASR). Never run `npx skills add … --all` inside a HyperFrames checkout (it deletes the repo's skills folder).

## OpenMontage (clone once)

```bash
cd "<AI Production>/_toolchain"
git clone https://github.com/calesthio/OpenMontage.git && cd OpenMontage
make setup        # venv + requirements + remotion-composer npm install + piper-tts + hyperframes warm + .env
```
Windows without make:
```powershell
py -3.10 -m venv .venv; .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd remotion-composer; npm install; cd ..        # if ERR_INVALID_ARG_TYPE: npx --yes npm install
python -m pip install piper-tts; copy .env.example .env
```
Keys go in `OpenMontage/.env` (all optional; zero-key path = Piper TTS + archives + Remotion/HyperFrames/FFmpeg). GPU local video: `make install-gpu`, `VIDEO_GEN_LOCAL_ENABLED=true`. Copy the brand playbook: `brand/tokens/openmontage-style.yaml` → `OpenMontage/styles/<brand>.yaml`.

## herk-edit-kit (clone once)

```bash
git clone https://github.com/nateherkai/herk-edit-kit.git && cd herk-edit-kit
npm ci && npm run setup && npm test        # setup checks node/ffmpeg/ffprobe and creates .env
npm run demo && cd video-projects/demo && npx hyperframes lint && npx hyperframes preview
```
`.env`: `ELEVENLABS_API_KEY` (Scribe + SFX), `OPENAI_API_KEY` or `GROQ_API_KEY` (Whisper alternatives), `KIE_API_KEY` (generation), `GEMINI_API_KEY` (capture descriptions). Pinned to `hyperframes@0.7.109`; run its scripts from inside each project folder.

## Pireel

Local editor (manual finishing):
```bash
git clone https://github.com/pireel/pireel.git && cd pireel
corepack enable && pnpm install && pnpm dev       # opens the Vite URL; assets stored in .local-assets/
```
Agent control is the hosted service (OAuth, credits for transcription/generation):
```bash
claude plugin marketplace add pireel/pireel-agent && claude plugin install pireel@pireel-marketplace
claude mcp login plugin:pireel:pireel
```
The OSS shell has no MCP server: agent-driven editing means pireel.com.

## Voicebox (desktop app)

- Windows: installer from https://voicebox.sh (`Voicebox_<ver>_x64-setup.exe` / `.msi`). NVIDIA: Settings → GPU → **Install CUDA backend** (~3 GB). AMD: ROCm (0.6), others DirectML; CPU works (slower; Kokoro/LuxTTS are fast on CPU).
- API: `http://127.0.0.1:17493` (Docker: `127.0.0.1:17600`, CPU/ROCm only). Swagger at `/docs`. No auth on loopback.
- MCP (optional): `claude mcp add voicebox --transport http --url http://127.0.0.1:17493/mcp --header "X-Voicebox-Client-Id: claude-code"`.
- First use of each engine downloads weights (Qwen 1.7B ≈ 3.5 GB). Generate once in the app to cache before scripting.

## VoiceStudio (desktop app)

- Windows PowerShell: `irm https://voicestudio.sh/install | iex`, or the release `VoiceStudio-Electron-<ver>-win-x64.exe` (unsigned: SmartScreen warns; verify `SHA256SUMS.txt`). First launch bootstraps Python, FFmpeg, PyTorch (~10 GB disk).
- GPU on Windows is **NVIDIA/CUDA only** (others run on CPU). OmniVoice wants ≥6 GB VRAM.
- API: `http://127.0.0.1:3900`; `GET /openapi.json` for the live contract. Docker callers need `OMNIVOICE_API_KEY`.
- **Accept model licences once in Model Catalogue** or API calls return 403. Install an ASR model for transcription (else 409).
- MCP: `http://localhost:3900/mcp/` (trailing slash), set `OMNIVOICE_MCP_OUTPUT_MODE=files` + `OMNIVOICE_MCP_BASE_PATH` so audio never floods context.

## Versions this skill was written against (2026-10)

remotion 4.0.537 · hyperframes 0.8.178 (herk pins 0.7.109) · OpenMontage main (Remotion 4.0.484 inside) · herk-edit-kit 2.0.0 · pireel 0.1.0 / pireel-agent 0.7.13 · Voicebox 0.5.0 release (0.6.0 on main) · VoiceStudio 0.5.6 release (0.5.7 on main). Check `npx remotion versions`, `npx hyperframes --version` and each app's About box; when a CLI flag here disagrees with `--help`, trust `--help`.
