# Status: hiking intro (Welsh mountains), v3

Intro to a hiking reel for James. It's more cinematic than usual, and the tone is gloomy and misty. The picture is the same 7.06 s recording as `platform_fog_hook` (`ScreenRecording_10-13-2026_21-20-55_1.mov`): it pushes through fog onto a night station platform, the lights flicker and white out, then it cuts to black at 6.85. Every timing below is from that project's `brightness.json` / `analysis.json` (pts times).

## Sound idea

The station is where the journey starts, and the Welsh weather is already in the air. Real mountain wind blows through the fog from frame 1 and rain falls on the canopy. On the cut to black a real gust blasts in and carries on into the first mountain shot.

## Changes from platform v2

- **Removed:** both structural groans. They're a horror creature cue, the wrong story for a hike.
- **Added:** `mountain_wind` (a real gust with a hollow hill-pass moan) under the fog; `rain_canopy` (real rain, high-passed, in the station's reverb); `gust_end` on the 6.85 slam, 8 s long.
- **Fog push** is now under the wind at −19 dB, not leading.
- **Target is −18 LUFS** (was −16), to leave room for music on a hiking reel.
- **Kept:** the gated tube (the platform's hero sound), thunder hits, arcs, the screech (now heard as the train) and the silence gaps.

## Outputs (`out/`, git-ignored; rebuild below)

`hiking_intro_wales_v3_sfx.wav` (−18.0 LUFS, −4.2 dBTP), `_preview.mp4`, `_stems.zip`, `_cues.md`, `_credits.txt`, and `_wind_handoff.wav`. The handoff is the rest of the end gust (about 10 s, level-matched, 1.5 s fade): place it at 00:07:04 to carry the wind under the first mountain shot.

## Rebuild

```bash
# from the repo root
python3 .claude/skills/reel-sound-designer/scripts/fetch_cc0.py wind brown-noise storm underwater boat
(cd projects/platform_fog_hook && python3 gen_custom.py && python3 gen_v2.py)
cd projects/hiking_intro_wales && python3 gen_hike.py
python3 ../../.claude/skills/reel-sound-designer/scripts/build_mix.py soundmap_v3.json --out out --stems
```

## Still synthetic or improvised (swap when the network is open)

The fluorescent tube, the rail screech core and the arcs are still synthesised. The wind and rain are real but generic. They aren't a Welsh recording. Wishlist, in impact order:

1. Upland wind on an exposed ridge or col (Freesound CC0: "mountain wind", "ridge wind", "wind gusts moor").
2. Real fluorescent flicker.
3. A raven call or distant sheep for one beat over the black or the first mountain shot (Freesound CC0: "raven call", "sheep distant"). Don't synthesise these.
4. Rain on a metal or glass canopy.

`../platform_fog_hook/source_v3.sh` already fetches the platform items.

## Open questions

- What is the first shot after the cut to black? The gust lands on it. If the next shot is calm, shorten `gust_end` or fade the handoff faster.
- Music: what BPM, and where does it come in? The reveal (2.02) and the slam (6.85) should land on downbeats.
- Voiceover over the intro?
