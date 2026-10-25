# Assets: footage, generated media, stock, music, SFX

## Preference order for any picture

1. Real footage of the thing named (client shoots, product, people with releases).
2. Real screen recordings: zoomed, visible cursor, no cookie/consent dialogs clicked on camera.
3. Animated UI mocks built in Remotion/HyperFrames, labelled as examples.
4. AI video (Higgsfield via Direct module (AI Director), or OpenMontage `video_selector`: Kling, Veo, Seedance, Runway, MiniMax, Wan/LTX local…) with concrete, physical prompts.
5. Stock (Pexels, Pixabay, Unsplash, archives via OpenMontage) — check licence terms per item.
6. Stills: only as keyframes for AI video, brand photography, or deliberate image scenes. A still with a Ken Burns push is not B-roll.

## Generated media rules

- **Sample before batch.** One shot at the cheapest viable model/setting, show it, then batch (Gate 4b).
- Announce each paid call: tool · provider · model · why · sample/batch · estimated cost; log in `DECISIONS.md`.
- No text, logos or signage in prompts; leave screens blank and composite UI in Remotion/HyperFrames (Direct module (AI Director) rule 4).
- Generate long, use the cleanest seconds: AI video often jumps angle around 2.5–3 s; keep the first continuous part.
- Continuity: paste the same character/set/look tokens into every prompt; pass the previous frame or reference sheet for consecutive shots of the same person.
- Inspect corners and backgrounds for gibberish text and fake logos; regenerate rather than paint over.
- Save prompt, model, seed, task id and the chosen output: `ledger.py add <file> --source generated --provider … --model … --prompt-file prompts/S04.txt --seed … --task-id … --cost … --scene S04 --use 0.4-3.1`.
- Kling-type 24 fps output into a 30/60 fps film: conform once (`ffmpeg -i in.mp4 -r 30 -c:v libx264 -crf 16 -g 30 -keyint_min 30 out.mp4`), don't let the renderer guess.
- Turn on platform AI-content labels for any video with AI-generated people, places or voices.

## Footage hygiene

- `raw/` is read-only. Conform copies for compositions: dense keyframes, constant frame rate, `+faststart`:
  `ffmpeg -i raw/in.mov -c:v libx264 -crf 16 -r 30 -g 30 -keyint_min 30 -sc_threshold 0 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart assets/video/in.mp4`
- Small stock (640×360): scale to cover + light sharpen before use (`scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,unsharp=3:3:0.6`).
- Build vertical crops from the native-resolution source, not a proxy. Prefer native vertical shoots for 9:16; `reframe.py --mode crop --x <focus>` per shot otherwise.
- One use per B-roll scene per reel (`ledger.py check` flags duplicates).

## Music and SFX

- Sources in order: user `music_library/` → licensed library → generated (Suno/ElevenLabs/Lyria via OpenMontage; Suno via herk `kie.mjs music`) → none. Record licence and URL.
- Edit music to the cut (herk `music-grid.mjs` + `splice-music.mjs` for beat-accurate edits; 12 ms crossfades) rather than looping.
- SFX: ElevenLabs sound generation (`herk sfx.mjs`, OpenMontage), Freesound (licence per file), or the Remotion SFX list (`https://remotion.media/*.wav`).

## Ledger

`assets/ledger.json` via `scripts/ledger.py`: id, file, sha256, source, provider, model, prompt, seed, task id, licence, URL, scene, used interval, cost, AI flag. `ledger.py check` before delivery: missing/changed files, unlicensed stock/music, duplicate scene use, total spend, AI disclosure reminder.
