# Credits and licences

This skill orchestrates the projects below. It does not bundle their code; workflows and rules are paraphrased from their documentation and agent skills (researched 2026-10-20). Respect each project's licence when you install and use it.

| Project | Repository | Licence | Notes |
|---|---|---|---|
| Remotion | https://github.com/remotion-dev/remotion | Remotion License (source-available) | Free for individuals, non-profits and companies of up to 3 people; Company License required otherwise (remotion.pro/license). Rules in `references/remotion.md` paraphrase Remotion's official agent skills. |
| HyperFrames | https://github.com/heygen-com/hyperframes | Apache-2.0 | `templates/hyperframes-brand/hyperframes.json` follows its schema. Contract and lint rules paraphrased from its docs and skills. GSAP is vendored per project from npm by `hf_build.py` (GSAP's own licence applies). |
| OpenMontage | https://github.com/calesthio/OpenMontage | AGPL-3.0 | `templates/openmontage/local_voice_tts.py` implements OpenMontage's `BaseTool` interface; once copied into an OpenMontage checkout it is part of that AGPL work. |
| herk-edit-kit | https://github.com/nateherkai/herk-edit-kit | MIT + pipeline-use permission (+ Apache-2.0 HF skills) | Its AIS brand assets and example projects are not licensed for reuse. |
| Pireel | https://github.com/pireel/pireel (agent: https://github.com/pireel/pireel-agent) | AGPL-3.0 (agent plugin Apache-2.0) | Hosted features are a paid service. |
| Voicebox | https://github.com/jamiepine/voicebox | MIT | Model weights carry their own licences (OmniVoice: CC-BY-NC). |
| VoiceStudio | https://github.com/debpalash/voicestudio | AGPL-3.0 (commercial licence available) | Default OmniVoice weights are CC-BY-NC; models must be accepted in-app. |

Sibling skills referenced: Direct module (AI Director), Read module (vidreader), Audio module (in the same AI Production folder).

Everything in `scripts/` and `templates/` (except where noted above) was written for this skill.
