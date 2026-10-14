---
name: reel-sound-designer
description: Expert sound designer for Instagram reels and short-form video. Watches the cut, matches sound to each shot (wind and water for open-sea footage, hull hiss for speed, halyard tings in the dinghy park, freewheel clicks on the bike, data blips over graphs) and designs transitions (whooshes on cuts, risers into drops, reverse swells, sub hits under titles), then renders a separate, frame-accurate sound-design track (48 kHz WAV) plus stems, a timecoded cue sheet and a licence file to drop into CapCut, Premiere or Resolve. Use this skill whenever the user wants sound effects, SFX, foley, ambience, a soundscape, sound design, risers, whooshes, hits or "audio" for a reel, short, TikTok, edit, promo or montage, wants sounds matched to clips, or runs a reel pipeline needing an audio layer, even if they never say "sound design". Cinematic, eerie, horror or trailer briefs need real recorded libraries, and the skill covers getting them in first.
---

# Reel sound designer

Make a reel feel like you are there. Picture tells people what happened; sound tells them what it felt like. The job is to hand back one audio file that starts at 0:00, is exactly the reel's length, and makes every cut, gust and stat land.

This is a sound-design layer, not a music track. The user adds music and any voiceover in their editor, so leave room for both.

## What you hand back

Always, in `/mnt/user-data/outputs/`:

1. `<title>_sfx.wav`: the full sound-design track, 48 kHz 24-bit stereo, exact reel length, normalised to −18 LUFS (leaves headroom for music and voice).
2. `<title>_cues.md`: timecoded cue sheet saying what lands where and why.
3. `<title>_credits.txt`: licence line for every recorded sound used.
4. `stems/` (zipped) when the reel has more than a handful of cues or the user wants to rebalance: ambience, transitions, impacts, fx, pad.

Present the WAV first. In the reply, a few lines: the sound idea in one sentence, anything you could not source and what you used instead, and any timing you guessed.

## Decide the quality tier first

Before anything else, read the brief for the tier it needs. Getting this wrong wastes a full render: an all-synthesised cinematic track was rejected as "simple whooshes", and the user had to ask for real libraries afterwards.

| Brief sounds like | Tier | What it needs |
|---|---|---|
| clean, minimal, data overlays, quick social cut | **Synth OK** | built-in generators + CC0 beds are enough |
| cinematic, eerie, horror, thriller, trailer, epic, "make it feel like a film", "high quality" | **Library required** | real designed SFX (layered booms, tails, drones, risers, stingers) and real foley for anything on screen |

For a **library required** brief, do this in the first reply, before rendering anything final:

1. Analyse the video (step 1) so the list is specific to the edit.
2. Send a short, moment-by-moment shopping list built from `references/sourcing_brief.md`: what to download, where (CC0 first), and how to name it. Name the hero sound (the one thing the edit is about).
3. Offer a synth timing draft at the same time if useful, but label it plainly as a **temp/placement draft**, not the delivery.

Synthesis then drops to glue: gating, sweeteners, sub weight and anything a library cannot time to the frame.

## Network reality (do not promise what the environment cannot do)

What is reachable depends on where you run: the claude.ai sandbox and a default Claude Code cloud session reach only GitHub, PyPI and npm; Claude Code on the user's own machine reaches everything. `references/sources.md` has the table and the exact hosts to allow (Freesound, BigSoundBank, ElevenLabs, Hugging Face). Check with `curl -s -m 10 -o /dev/null -w "%{http_code}" <url>` before planning a fetch. If a host is blocked, say which one and how the user can allow it, carry on with what works, and never imply you downloaded from it. Freesound originals also need the user's API key and login.

GitHub mostly holds game packs (Kenney-style UI zaps, footsteps, generic impacts) with mixed licences: a step sideways, not a source of cinematic sound. For new **skills and tools** (not sounds), check `github.com/davila7/claude-code-templates` first; what it has for audio is listed in `references/sources.md`. Inspect repos with `git clone --depth 1 --filter=blob:none --no-checkout` and `git ls-tree`, not the rate-limited API.

## Workflow

### 1. Get the picture

Best input is the exported reel itself (even a rough cut). Run:

```bash
python scripts/analyse_video.py /mnt/user-data/uploads/<reel>.mp4 --out /home/claude/work
```

This finds the cuts, saves a frame from the middle of every shot, a contact sheet, a **dense sheet** (6 frames a second), a per-frame **brightness curve** (`brightness.json`) and **light events** (flashes, blackouts, flicker dips). **View both sheets.** The cut detector misses things that happen inside a shot (a light flickering, a white flash, a slow push), and those are often the best sync points: use the light events list for them. Take every sync time from `analysis.json` or `brightness.json` (real presentation times). Never compute times as frame number ÷ fps yourself: phone screen recordings are variable frame rate and that drifted 4 frames early on the first eerie reel. You cannot match sound to clips you have not looked at. For shaky on-water footage the detector can over-trigger: raise `--threshold` to 0.4–0.45. For dissolves, lower it to 0.2. Sanity-check the cut list against what you see.

If there is no video, work from whatever exists: a shot list with timings, an edit decision list, a music BPM, or the user's description. Ask for the two things that change the design most if they are missing: total length, and where the cuts are.

Also find out (from the conversation, or ask once): is there voiceover or talking to camera, and where? Is there a music track and its BPM? These drive ducking and hit placement.

### 2. Read each shot like a sound designer

For every shot, answer three questions before choosing sounds:

- **Where are we?** Gives the ambience bed (open sea, harbour, gym, road, studio/data screen).
- **What moves?** Gives the spot effects (boat, sheet, body, bike, graphic, text).
- **What should the viewer feel?** Gives the designed layer (tension, release, speed, calm, precision).

`references/sound_vocabulary.md` maps sailing, training and data shots to concrete sounds and generators. Read it for any sailing/athlete reel.

### 3. Write the sound map

The sound map is a JSON file describing every cue. Schema and examples: `references/soundmap_schema.md`. Key ideas:

- `at` is the sync point. Whooshes are anchored at their **peak**, risers and reverse swells at their **end**, hits at their **start**: so for all of them, `at` = the cut.
- `src` is `synth:<generator>`, `rec:<name>` (a recording in the library) or `file:<path>`.
- Every cue gets a `note` saying why it is there. If you cannot say why, cut it.

Design principles (expanded in `references/craft.md`, read it before your first map):

- **Fewer, better sounds.** Pick the 3–5 moments that matter (the hook, the big cut, the reveal, the ending) and design those properly. Not every cut needs a whoosh. A reel with a transition on every cut sounds like a template.
- **Beds carry the reality, sweeteners carry the energy.** Continuous ambience under the on-water shots, then designed sounds on top only where the edit has intent.
- **Lead the picture.** Bring the next scene's ambience in 0.2–0.5 s before the cut (J-cut). It makes cuts feel smooth and intentional.
- **Silence is a sound.** Drop everything for 3–8 frames before the biggest hit. The contrast is what makes it big.
- **Vary.** Never use the same whoosh twice in a reel: change `dur`, `seed`, `low`/`high`, pan direction.
- **Match the motion.** Pan whooshes in the direction things move on screen; brighter and shorter for fast moves, darker and longer for slow ones.
- **Design for phones.** Most people hear this on a phone speaker, which cannot reproduce below about 150 Hz. Every low hit must have mid-range body or saturation (the generators already do this) so it still reads. Check with the phone test in step 5.
- **Hook the first second.** Reels are judged in the first 1–2 s. Something should be happening in the audio from frame 1: a hit, a gust, a ting, not a 1 s fade-in.

### 4. Source the sounds

If the user has uploaded a library (files or zips), bring it in first:

```bash
python scripts/intake_library.py /mnt/user-data/uploads --licences /mnt/user-data/uploads/licences.csv
```

It converts everything to 48 kHz WAV in `/home/claude/sfx-library` with plain names for `rec:<n>`, writes licence sidecars, and makes `catalogue.md` and `waveforms.png`. **Read the catalogue and look at the waveforms**, shortlist two or three candidates per moment, then audition them in a quick test render before committing. Pick by attack, tail length and brightness against the picture, not by file name.

Then, for each cue, in this order of preference:

1. **The user's own library** for things that must sound real and cannot be synthesised: seagulls, rigging slap, coach-boat engine, start horn, crowd, voices, gym plates. Look in `/mnt/user-data/uploads/` and any folder they name. Use `file:<path>` or `rec:<name>`.
2. **Freesound CC0 via API** when freesound.org is reachable and the user has given `FREESOUND_API_KEY`: `python scripts/freesound_fetch.py "fluorescent flicker" "rail screech" --per-query 4`, then `intake_library.py` on the folder. Use the search terms in `references/sourcing_brief.md`.
3. **AI generation** for designed one-shots the libraries lack: `python scripts/elevenlabs_sfx.py "<prompt>" --name <slug> --dur 3 --variations 3` (needs `ELEVENLABS_API_KEY`, paid plan for commercial use). Read `references/generation.md` first: AudioGen and MusicGen weights are non-commercial and are for drafts only.
4. **CC0 recordings fetched from GitHub** for natural beds: `python scripts/fetch_cc0.py wind waves boat underwater` (lists what each is good for). The sandbox can reach GitHub but not Freesound or other SFX sites.
5. **Synthesis** for glue and anything the library cannot time to the frame (on a library-required brief, never as the main designed layer): whooshes, risers, hits, sub drops, ticks, data scans, pads, plus physical-ish sounds the engine models well (halyard ting, freewheel, rope zip, hull hiss, procedural wind/waves as fallbacks). `python scripts/synth.py list`, audition any with `python scripts/synth.py whoosh --dur 1.2 --seed 7 --out /tmp/w.wav`.

If a realistic sound is needed and nothing real is available, **do not fake it badly**: a synthesised seagull is worse than no seagull. Leave the gap, say so in the reply, and name a specific free source (see `references/sources.md`). Then the user can upload it and you re-render.

### 5. Render and check

```bash
python scripts/build_mix.py /home/claude/work/soundmap.json --out /mnt/user-data/outputs --stems
```

Then check before handing over:

- **Look at it.** `ffmpeg -i <wav> -lavfi showspectrumpic=s=1000x400:legend=1 spec.png` and view it. Every cue should be visible where you intended; whoosh peaks and riser ends should sit on the cut lines from `analysis.json`.
- **Phone test.** Render a high-passed copy (`-af highpass=f=180`) and its spectrogram: the hits must still be visible as clear vertical events.
- **Mux a preview** so timing can be judged by eye and ear together: `ffmpeg -i reel.mp4 -i <title>_sfx.wav -map 0:v -map 1:a -c:v copy -shortest preview.mp4`. Present it alongside the WAV when a video was supplied.
- **Loop check.** The build fades the last 30 ms (`end_fade`) so the reel loops without a click; make sure the final hit still lands before it.
- **Credits.** Any file you make yourself (custom numpy sounds) needs a sidecar `<name>.json` with `{"licence": "original", "author": "synthesised for this reel"}` or it is flagged as unlicensed.
- Read the `note:` lines the build prints (clipped starts, loudness held back) and fix or report them.

### 6. Iterate

Feedback will be things like "the whoosh at 4s is too much", "more wind", "the drop doesn't hit". Edit the sound map, not the audio, and re-render. Keep the map file as the source of truth and present it too, so the next session can pick up from it.

## Brand: ILCA 7 athlete-engineer reels

These reels sit under a minimal brand (navy, red, light grey, clean typography, no cartoon sailing graphics). The sound should match:

- **Real first.** Wind, water and boat sounds carry the sailing; designed sounds frame it. Never let synths bury the water.
- **Precise, not epic.** Clean ticks and blips for data and the engineering side; tight, controlled hits. Avoid trailer "braams", comedy boings, cartoon splashes, record scratches and stock "whoosh-ding" UI clichés.
- **Earned intensity.** Hard sailing, gym and cycling are where risers, heartbeat pulses and big hits belong; recovery, dawn and harbour shots stay calm and open.
- **Consistent signature.** Reuse the same family of sounds (same tick pitch, same impact character, same pad key) across reels so the brand sounds recognisable. Record the chosen signature (generator settings) in the cue sheet so it can be repeated.

## Character: cinematic and eerie hooks

- **Real textures first, designed layers second.** Real tube buzz, room tone, rail screech and arcs carry the world; library booms, drones and stingers carry the dread. Synth only glues.
- **The picture drives the sound.** If light flickers, gate the hum and room tone to `brightness.json` (`gate` in the sound map) so sound and light fail together. This was the strongest idea in the first eerie reel.
- **Dynamics are the scare.** Choke everything 3–8 frames before the reveal and the final cut to black; let one hit ring into the silence.
- **One hero sound.** Name the single sound the edit is about (a failing fluorescent tube, a distant train) and build around it.

For other brands, ask for or infer the brand's character and write the equivalent four lines before designing.

## Reference files

- `references/craft.md`: timing, layering, levels, mixing rules, loudness for social platforms. Read before writing the first sound map.
- `references/sound_vocabulary.md`: shot-to-sound mapping for sailing, training and data content, with generator settings.
- `references/soundmap_schema.md`: every sound map field, with a worked example.
- `references/generation.md`: AI sound generation (ElevenLabs, Stable Audio Open, AudioGen): licences, prompt recipes, QC.
- `references/sourcing_brief.md`: the download list template for library-required briefs (per-moment sounds, search terms, naming).
- `references/sources.md`: what each environment can reach, where real recordings come from, licences, Instagram claim issues, the user's library layout, and the claude-code-templates catalogue.

## Changelog

- **v2 (Oct 2026):** quality-tier check and sourcing brief for cinematic briefs; network limits stated plainly; `intake_library.py` for user-uploaded libraries; light events, dense sheet and brightness curve in `analyse_video.py`; `gate` and `end_fade` in the sound map; pts-only timing; phone body-layer and choke techniques; credits for self-made files.
- **v3 (Oct 2026):** `freesound_fetch.py` (CC0-only Freesound API search and download with sidecars), `elevenlabs_sfx.py` (text-to-SFX generation with licence sidecars), `references/generation.md` (generation licence matrix: AudioGen/MusicGen weights are non-commercial), claude-code-templates catalogue in `sources.md`; `intake_library.py` now reads `<name>.json` sidecars; library paths default to `$SFX_LIBRARY` or `./sfx-library` instead of `/home/claude`.
