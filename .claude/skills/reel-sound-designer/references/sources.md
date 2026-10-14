# Where sounds come from

## What each environment can reach

| Environment | Reaches | Sound sites |
|---|---|---|
| claude.ai sandbox | GitHub, PyPI, npm | blocked; an organisation owner can add domains to the org network allowlist |
| Claude Code cloud session (claude.ai/code) | GitHub (git and raw), PyPI, npm by default | blocked until the hosts are added under the environment's Network access, Allowed domains (see below) |
| Claude Code on the user's own machine | everything | open |

Hosts to allow for full sourcing: `freesound.org`, `cdn.freesound.org` (Freesound API and previews), `bigsoundbank.com`, `api.elevenlabs.io` (generation), `huggingface.co` and `cdn-lfs.huggingface.co` (Stable Audio Open weights). Check reachability with `curl -s -m 10 -o /dev/null -w "%{http_code}" <url>`; `000` or a proxy 403 means blocked. Never imply a download from a blocked host happened.

Freesound needs the user's own API key (`FREESOUND_API_KEY`, free) for search and HQ previews, and an OAuth2 token for originals. `scripts/freesound_fetch.py` filters to CC0 and writes the sidecars.

## Skill and tool catalogue: claude-code-templates

`github.com/davila7/claude-code-templates` (also browsable at aitmpl.com) is a large catalogue of Claude Code skills, agents, MCP configs and hooks. **Check it first when the skill needs a new capability**, before writing one from scratch. Inspect without the API: `git clone --depth 1 --filter=blob:none --no-checkout <repo>` then `git ls-tree -r --name-only HEAD | grep -iE 'audio|sound|music|sfx'`, and `git checkout HEAD -- <path>` for the files you want. Audio-relevant items, October 2026:

| Path under `cli-tool/components/` | What it is | Verdict for reels |
|---|---|---|
| `mcps/audio/elevenlabs.json` | official ElevenLabs MCP (`uvx elevenlabs-mcp`): TTS, voice design, **sound-effect generation**, audio isolation | **Use.** Same API as `scripts/elevenlabs_sfx.py`; commercial on a paid plan |
| `skills/ai-research/multimodal-audiocraft` | Meta AudioGen and MusicGen: text-to-sound and text-to-music | drafts only: weights are CC BY-NC 4.0 (the skill says "MIT", which is the code) |
| `skills/media/speech` | OpenAI TTS for narration and voiceover | optional: source for a degraded station announcement |
| `agents/ffmpeg-clip-team/audio-quality-controller.md`, `audio-mixer.md` | ffmpeg loudness, EQ and compression recipes | podcast targets; this skill's own build and checks already cover it |
| `skills/creative-design/game-development/game-audio` | layering (attack, body, tail, sweetener), priority and ducking principles | general; matches `craft.md` |
| `skills/video/remotion` (`references/audio.md`) | audio in Remotion video compositions | only if the reel is built in Remotion |

No dedicated cinematic sound-design or SFX-library skill exists there yet; this skill remains the one to extend. See `generation.md` for the generation routes and their licences.

## Built in

- **Synthesis** (`scripts/synth.py`): original sounds, no licence questions. Strong for: whooshes, swishes, risers, reverse swells, impacts, sub drops, ticks, data scans, pads, heartbeat, metal ting, freewheel, rope zip, hull hiss. Acceptable fallbacks: wind, waves.
- **Freesound CC0 via API** (`scripts/freesound_fetch.py "query" ...`): search, download and sidecar in one step when freesound.org is reachable and the user has given an API key.
- **AI generation** (`scripts/elevenlabs_sfx.py`, Stable Audio Open): designed one-shots and textures from a prompt. Licences differ: read `generation.md`.
- **CC0 recordings via GitHub** (`scripts/fetch_cc0.py`): wind, boat, underwater, storm, leaves, brown noise (all traced to CC0 uploads on Freesound), plus waves, birds-tree, stream-water, rain (credited upstream as CC0 by a YouTube channel, thinner provenance). They come from the Noisekun ambient-sound project, which also hosts CC BY, CC BY-SA and commercially licensed files; the fetch script deliberately skips those.

## Cannot be synthesised convincingly: ask the user to supply

Seagulls and other birds by species, rigging and halyard slap on aluminium masts (the synthetic ting covers single hits only), start horn and gun, coach-boat outboard, crowds and clapping, voices and breathing, gym plates and chalk, splashes, sail flogging, trolley wheels on a slipway.

When one of these is needed and missing, leave it out, say which moment wanted it, and suggest a source:

| Source | Licence | Notes |
|---|---|---|
| Signature Sounds (signaturesounds.org) | CC0 (as listed on the site) | designed packs: eerie build-ups, suspense drones and stingers, cinematic impacts. First stop for cinematic/horror briefs |
| Sonniss GDC Game Audio Bundle | royalty-free licence, not CC0 | professional libraries (horror, electrical, impacts). Commercial use believed allowed without credit, but have the user check the licence file in the bundle before posting; never describe it as CC0 |
| BigSoundBank (bigsoundbank.com) | CC0 | thousands of sounds, good seaside and harbour recordings, no account needed |
| Freesound (freesound.org) | per sound: filter to CC0 | biggest library; free account to download; check every licence |
| Pixabay sound effects | Pixabay licence | free for commercial use, no attribution |
| Mixkit sound effects | Mixkit licence | free, no attribution; check each is marked free for commercial use |
| Own recordings | own | phone on a lanyard in the boat park beats any library: encourage it |

Avoid CC BY-NC (non-commercial) sounds: a personal-brand athlete account that courts sponsors is arguably commercial. CC BY is fine if the credit goes in the post caption or profile.

## User library convention

Ask the user to name files plainly so `rec:<name>` finds them: `seagulls-harbour.wav`, `halyard-slap-1.wav`, `start-horn.wav`. Licences go in a `licences.json` next to them:

```json
{"seagulls-harbour.wav": {"licence": "CC0", "author": "BigSoundBank", "source": "https://bigsoundbank.com/..."}}
```

or a sidecar `seagulls-harbour.json` with the same fields. Anything without a licence record is flagged in the credits file as "confirm before posting".

## Instagram and copyright claims

Even public-domain sounds can be wrongly matched by automated copyright systems, because the same CC0 file is used in many videos; BigSoundBank itself warns that TikTok may incorrectly claim its sounds. Keep the credits file with each reel so a claim can be disputed quickly. Synthesised sounds avoid this entirely, which is one more reason to keep the designed layer synthetic.
