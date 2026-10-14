# Generating sound with AI models

A third route between "synthesise it in numpy" and "find a recording": text-to-audio models. They give designed, recorded-sounding one-shots and textures with no searching. Licences vary a lot and decide what can ship in a reel, so check the table first.

## Licence matrix (checked October 2026)

| Generator | How to run | Licence of the output | Use in a delivered reel? |
|---|---|---|---|
| **ElevenLabs Sound Effects** | API: `scripts/elevenlabs_sfx.py`, or the official `elevenlabs-mcp` server | paid plan: commercial use; free tier: attribution and non-commercial | **Yes, on a paid plan.** Best quality-for-effort for one-shots |
| **Stable Audio Open 1.0** (Stability AI) | `diffusers` `StableAudioPipeline`, weights gated on Hugging Face; GPU strongly advised; up to 47 s | Stability AI Community Licence: free commercial use under US$1M annual revenue | **Yes, if under the revenue threshold.** Good for drones, risers and textures |
| **Meta AudioGen / MusicGen** (AudioCraft) | `pip install audiocraft` | code MIT, but **model weights CC BY-NC 4.0** | **No.** Temp/placement drafts only. The claude-code-templates AudioCraft skill lists "MIT"; that is the code, not the weights |
| Synthesis (`scripts/synth.py`, custom numpy) | built in | original | Yes |

Record the generator, prompt and plan in the sidecar `.json` (the scripts do this) so the credits file shows where each sound came from.

## Where generation beats a library

- **A specific event with no stock match:** "a fluorescent tube arcing then dying with a pop".
- **Variations:** five versions of a crackle so the strobe never repeats.
- **Tonal stingers in a key:** a drone or stinger on A / B-flat to sit with the reel's pad.
- **Optional world detail:** a distant, garbled station chime or announcement. For a voiced announcement use a TTS model (the claude-code-templates `speech` skill, ElevenLabs voices), then degrade it: band-pass 400–3500 Hz, long reverb, partly reversed.

Where it does not: real-world foley the viewer knows well (rain, crowds, specific birds). A real recording still wins, so use Freesound CC0 or BigSoundBank.

## Prompt recipes (eerie platform reel)

Describe the source, the space, the character and the envelope. Keep it to one sound per prompt.

| Moment | Prompt | dur |
|---|---|---|
| hero tube (gated later) | `old fluorescent tube light buzzing at 50 Hz in an empty underground station, ballast hum, irregular starter clicks, flickering, close mic` | 6 |
| reveal / end hit | `massive cinematic trailer boom, deep sub impact, metallic body, very long dark reverb tail fading to silence` | 5 |
| white flash arc | `violent electrical arc short circuit, crackling sparks, transformer pop, sizzle tail` | 1.5 |
| rail screech | `distant train wheels screeching on steel rails in a tunnel, metallic squeal bending upward, cavernous reverb` | 3 |
| room tone | `empty underground train platform at night, low air handling rumble, distant tunnel wind, no voices` | 10 |
| drone / riser | `dark horror tension drone slowly rising in pitch and intensity, low strings and metal resonance` | 6 |
| chime (optional) | `distant station announcement chime, three notes, heavy reverb, slightly detuned and degraded` | 3 |

Generate two or three variations per moment, run `intake_library.py` on the output folder, shortlist by attack and tail in `catalogue.md`, then audition in a test render. Keep the sound map timings; swap `src` only.

## Mastering and QC

The ffmpeg patterns in the claude-code-templates `audio-quality-controller` agent are podcast-oriented (−16 LUFS, −1.5 dBTP, LRA 7–12). For reels keep this skill's targets: −18 LUFS for an SFX layer under music, −16 LUFS when SFX is the whole track, true peak −1 dBTP or lower, and the phone test (high-pass at 180 Hz). Quick measurement:

```bash
ffmpeg -i mix.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -
```
