# Status: platform fog hook, eerie reel sound design

Handoff from claude.ai to Claude Code, 14 October 2026.

## Session 2 (Claude Code cloud, 14 October 2026)

- The project is now a repo: the skill lives in `.claude/skills/reel-sound-designer/`, and the reel lives in `projects/platform_fog_hook/`. The paths in `gen_v2.py` and `gen_custom.py` are fixed (relative to the repo, with the library at `$SFX_LIBRARY` or `./sfx-library`). `gen_custom.py` is cut down to the three `body_*` layers it is still needed for.
- **v2 rebuilt from scratch here and matches the delivery:** −16.0 LUFS, −1.9 dBTP, 37 cues. Rebuild it with the commands below, run from this folder.
- **Still blocked:** this cloud environment reaches only GitHub, PyPI and npm. Freesound, BigSoundBank, ElevenLabs and Hugging Face return a proxy 403, so no new sounds were sourced. Add the hosts under the environment's Network access, Allowed domains, or run on James's machine.
- New tools for next steps 1 and 6: `freesound_fetch.py`, which searches and downloads CC0 sounds only and writes licence sidecars, and `elevenlabs_sfx.py`, which generates sound effects from a text prompt. `source_v3.sh` in this folder runs the whole shopping list through both: set `FREESOUND_API_KEY` and/or `ELEVENLABS_API_KEY` first.
- Skills from `davila7/claude-code-templates` were reviewed. The useful ones are the ElevenLabs MCP (sound-effect generation) and the AudioCraft skill. AudioCraft's AudioGen/MusicGen weights are **CC BY-NC**, so use them for drafts only. There is no dedicated cinematic SFX skill there. The details are in the skill's `references/sources.md` and `references/generation.md`.
- Still missing from the handoff bundle: the source `.mov` and the v2 WAV/preview. Commit the `.mov` (it is git-ignored, so use `git add -f`) or upload it, to mux previews here.

## Goal

A cinematic, eerie sound design for a 7.06 s Instagram reel hook: a camera pushes through fog onto an empty night train platform, and the lights flicker, white out and die. James wants higher-level sounds than the built-in synthesis can give, sourced from real open libraries.

## Where it stands

- **v2 delivered** (`platform_fog_hook_v2_sfx.wav`, preview mp4, stems). It's built from real CC0 recordings (Noisekun mirror of Freesound uploads), reshaped into designed layers, plus synthesis only where no CC0 source was reachable.
- **v1 rejected** as "simple whooshes": all synthesis. It also had a timing bug (see Decisions).
- **Blocker in claude.ai:** the sandbox reaches only GitHub, PyPI and npm. Freesound, BigSoundBank, Pixabay, Signature Sounds and Sonniss are blocked. **Claude Code on James's machine has no such limit**, which is why the work moved here.

## The edit (source of truth for timings)

Source is `ScreenRecording_10-13-2026_21-20-55_1.mov`: an HEVC iPhone screen recording, 1206×2622, nominally 60 fps but **variable frame rate**, 7.063 s long. It shows a video player, so the player bar is visible; James may export a clean version.

All times below come from real presentation timestamps (`brightness.json` and `analysis.json`).

| Time (s) | Picture | Sound role |
|---|---|---|
| 0.00–1.93 | camera pushes through dense fog; brightest at 1.90 | hook boom on frame 1, fog air, drone, unseen groan |
| 1.93–2.02 | (silence gap) | choke everything: 5 frames of near-silence |
| **2.02** | **hard cut to dark platform (reveal)** | **biggest hit**; tube hum starts |
| 2.20, 2.40, 2.60 | flicker dips | crackles |
| 3.32 (peak 3.40) | white flash 1 | reverse suck in, arc, hit |
| 3.48, 3.69, 3.88, 4.08 | strobe blackouts; recover 4.18 | crackles |
| 4.77 (peak 4.80–4.87) | white flash 2 | arc, swish, hit pitched down |
| 4.97, 5.17, 5.37, 5.57 | dim flicker; recover 5.63 | crackles |
| 5.40–6.80 | held shot, slow push | reversed thunder build, rail screech, riser |
| **6.85** | **cut to black** | tube dies with a crackle; **final slam** |

## Sound design decisions (and why)

- **Hero sound: a failing 50 Hz fluorescent tube.** The edit is about the power failing, so the hum is gated frame by frame to picture brightness (the `gate` field in the sound map, using `brightness.json`, ref 54). Sound and light fail together. This was the strongest idea in v1 and is kept.
- **Silence is the scare.** Everything chokes 5 frames before the reveal and 4 frames before the cut to black. Only the tube runs into the final hit, because it's the thing that "dies".
- **Trailer-hit structure:** a transient crack, a sub boom, a saturated mid body and a real thunder tail. A separate mid-range "body" layer makes the hits read on a phone speaker. Phone-filtered levels (high-pass 180 Hz) are about −16 dB for the hook, reveal and end, and about −27 dB for the bed.
- **Loudness:** −16 LUFS integrated, true peak −1.9 dBTP, with a 30 ms end fade so the reel loops without a click.
- **Timing bug fixed:** v1 computed times as frame index ÷ 60, which drifted up to about 4 frames early on this VFR recording. Always use pts times.
- **Licences:** CC0 or original only. CC BY-SA was rejected, because share-alike would attach conditions to the reel. CC BY-NC is never used, as James's reels are arguably commercial. Sonniss is royalty-free but **not CC0**, so check its bundle licence before using it.

## Files in this bundle

| File | What it is |
|---|---|
| `status.md` | this file |
| `reel-sound-designer.skill` | updated skill v2: quality-tier check, `intake_library.py`, light events, `gate`, `end_fade`, pts timing. Unzip into `~/.claude/skills/` (or the project's `.claude/skills/`) |
| `soundmap_v2.json` | the v2 cue list, 37 cues. Paths are relative (`file:custom/...`): run from the project folder |
| `gen_v2.py` | builds the `custom/` sources from the CC0 recordings. Paths are hard-coded to the sandbox (`/home/claude/...`, `/tmp/reel-sound-designer/scripts`): **update `LIB`, `OUT` and the `sys.path` line** |
| `gen_custom.py` | v1 generator; still needed for `body_hook`, `body_reveal` and `body_end` (phone body layers). Same path fix needed |
| `brightness.json` | per-frame brightness on pts times; drives the tube gate |
| `analysis.json` | cuts, shots and light events from `analyse_video.py` |
| `platform_fog_hook_v2_cues.md`, `..._credits.txt` | cue sheet and licence record for v2 |

Also bring over from the claude.ai outputs: `platform_fog_hook_v2_sfx.wav`, `..._preview.mp4`, `..._stems.zip` and the source `.mov`.

## To rebuild v2 locally

```bash
# from projects/platform_fog_hook/
SFX_LIBRARY=../../sfx-library python3 ../../.claude/skills/reel-sound-designer/scripts/fetch_cc0.py wind brown-noise storm underwater boat
python3 gen_custom.py   # body_* phone layers
python3 gen_v2.py       # writes custom/*.wav and licence sidecars
python3 ../../.claude/skills/reel-sound-designer/scripts/build_mix.py soundmap_v2.json --out out --stems
ffmpeg -i source.mov -i out/platform_fog_hook_v2_sfx.wav -map 0:v -map 1:a -c:v copy -tag:v hvc1 \
  -c:a aac -b:a 256k -shortest -movflags +faststart out/preview.mp4
```

Needs Python with numpy and scipy, plus ffmpeg.

## Unresolved: next steps for Claude Code (in priority order)

1. **Source real libraries now that the network is open.** Use Freesound (filter to CC0; originals need James's API key and login), BigSoundBank (CC0), Signature Sounds (CC0 designed packs) and optionally Sonniss GDC (check its licence). Shopping list, in impact order:
   1. **Real fluorescent tube flicker and buzz.** This is the hero sound and is still synthesised (`tube.wav`); keep the brightness gate on it.
   2. **One or two library cinematic booms or trailer hits with long tails,** for the reveal (2.02) and the end (6.85).
   3. Real rail screech or train brakes, to replace the synth core of `screech.wav`.
   4. An electrical arc or short-circuit spark, for 3.32 and 4.77.
   5. Empty station or underground platform room tone at night, to replace `station_room.wav`.
   6. A dark tension drone and a deep riser.
   7. Optional: a distant, garbled station announcement chime.
2. Run `intake_library.py` on the downloads, read `catalogue.md`, shortlist 2–3 per moment and test-render. **Keep the timings above.**
3. Re-check phone translation (hits clearly above the bed) and loudness, and keep the silence gaps.
4. If James exports a clean version without the player UI, re-run `analyse_video.py` on it. Re-time only if the light events move.
5. Ask whether music goes on top. If so, get its BPM, put the reveal and final hits on downbeats, and consider lowering the SFX target to −18 LUFS.
6. Update the skill's `sources.md` once local sourcing works, for example a Freesound API fetch script that writes licence sidecars automatically.

## Open questions for James

- Is this reel for his own channel or for Tarot Tom? It's currently treated as its own cinematic look, not the ILCA athlete brand.
- Will there be music or voiceover over the hook?
