# Sound designer

Sound design for James's Instagram reels (sailing/athlete brand and one-off cinematic hooks), built with the `reel-sound-designer` skill.

## Layout

- `.claude/skills/reel-sound-designer/`: the skill (SKILL.md, scripts, references). Source of truth; `dist/reel-sound-designer.skill` is the same thing zipped for upload to claude.ai. Re-zip it after editing the skill: `cd .claude/skills && zip -qr ../../dist/reel-sound-designer.skill reel-sound-designer -x '*__pycache__*'`.
- `projects/<reel>/`: one folder per reel: `status.md` (handoff notes, open questions), sound map, generator scripts, `brightness.json` / `analysis.json`, cue sheet and credits.
- `sfx-library/` (git-ignored): downloaded and generated sounds with licence sidecars. Override with `$SFX_LIBRARY`.

Needs Python 3 with numpy and scipy (`pip install scipy`), plus ffmpeg.

## Sourcing skills and tools

**Look in `github.com/davila7/claude-code-templates` first** (catalogue at aitmpl.com) when a new capability is needed: skills, agents, MCP servers and hooks. Inspect with a blobless clone, not the rate-limited API:

```bash
git clone --depth 1 --filter=blob:none --no-checkout https://github.com/davila7/claude-code-templates cct
cd cct && git ls-tree -r --name-only HEAD | grep -iE 'audio|sound|music|sfx'
git checkout HEAD -- <path>
```

What it holds for audio, and the verdict for each item, is in `.claude/skills/reel-sound-designer/references/sources.md`. Check the licence of any model a skill uses; a skill's own "license" field is usually about its code, not the model weights.

## Rules that hold across reels

- Licences: CC0 or original by default. Never CC BY-NC (James's reels are arguably commercial); no CC BY-SA. AI generation only where the output licence allows commercial use (see `references/generation.md`).
- Timing comes from presentation timestamps (`analysis.json`, `brightness.json`), never frame index ÷ fps: phone screen recordings are variable frame rate.
- Edit the sound map, not the audio, and re-render.
- Cloud sessions reach only GitHub, PyPI and npm by default. Freesound, BigSoundBank, ElevenLabs and Hugging Face need adding under the environment's Network access, Allowed domains (hosts are listed in `sources.md`).
