# Shot-to-sound vocabulary

`synth:` = generator in scripts/synth.py. `rec:` = CC0 recording from fetch_cc0.py. `own:` = must come from the user's library (cannot be convincingly synthesised).

## On the water (ILCA)

| Shot | Bed | Spot / sweetener | Settings / tips |
|---|---|---|---|
| Wide establishing, open water | `rec:wind` (hp 120) + `rec:waves` low | maybe a distant `own:` seagull once | real wind beats synth; `synth:wind strength 0.4` as fallback |
| Close, boat at speed, planing, downwind | `synth:hull_hiss speed 0.7` over `rec:wind` | whoosh as the boat passes camera, panned with it | keep hiss spans short (≤4 s), it tires the ear |
| Upwind, hiking hard | `rec:wind` louder, gustier | `synth:heartbeat bpm 70–85` very low for strain; `own:` breathing if they have it | this is earned intensity: a slow riser across a long hike sequence works |
| Tack or gybe | bed continues | `synth:whoosh` peaked on the boom crossing, panned the boom's direction; `synth:rope_zip` on the sheet | boom cross is the sync point, not the cut |
| Gust hitting | wind swell: automate a second `rec:wind` with fade_in 0.5 | short `synth:reverse_swell` into the gust | |
| Capsize / dunk / underwater GoPro | `rec:underwater` | `synth:impact` (body 0.8, sub 0.4) on the splash frame, then cut to underwater | `own:` splash if available; do not synthesise a splash |
| Start sequence, pre-start | `rec:wind` thin | `synth:heartbeat`, `synth:riser` ending on the gun | horn/gun must be `own:`; never fake a horn |
| Slow motion | same bed, `pitch: -5`, `lp: 2500`, reverb | | the "underwater-ish" muffled feel signals slow-mo |
| Drone shot | wind only, soft | `synth:pad` underneath | drones are quiet moments; no hits |

## Shore and boat park

| Shot | Bed | Spot |
|---|---|---|
| Dinghy park, rigging | `rec:wind` low | `synth:metal_ting` (vary `f` 1100–1900 and seed) every 2–4 s, sparse, panned around; `own:` rigging slap |
| Harbour, launching | `rec:boat` + `rec:waves` low | `own:` seagulls, `own:` trolley on slipway |
| Packing up, dusk | `rec:waves` very low | `synth:pad` minor, slow |

## Training

| Shot | Bed | Spot |
|---|---|---|
| Gym | room tone: `rec:brown-noise` lp 400, very low | `synth:impact` (sub 0.6, click 0.8, room 0.1) small, on bar touching down; `own:` plates/chalk |
| Cycling road | `synth:wind strength 0.3` (air rush) + `rec:leaves` if countryside | `synth:freewheel` on coasting shots; `synth:swish` on passing cars |
| Indoor trainer / ergo | low `rec:brown-noise` | `synth:heartbeat`, `synth:data_scan` on power numbers |
| Recovery, stretching | near silence, `synth:pad` soft | nothing else: contrast with the hard sections |

## Data and the engineer side

| Shot | Sound | Settings |
|---|---|---|
| Graph line drawing on, track overlay | `synth:data_scan` matched to draw duration | gain −18; keep the same tick pitch across reels as the brand signature |
| Single number or label popping on | `synth:tick` | freq 2800–3600; one per element, never more than ~6 per second |
| Polar plot, boat-speed comparison, app screen | `synth:pad` very low + ticks | real app footage only: sound accompanies it, never replaces it |
| Title card / logo | `synth:reverse_swell` into `synth:sub_drop` | the one big moment: use silence before it |

## Story beats

| Beat | Treatment |
|---|---|
| Hook (first 1–2 s) | something immediate: gust, ting, impact on the first frame |
| Build | riser or heartbeat across 2–4 s of fast cuts |
| Drop / reveal | 3–8 frames of silence, then impact + sub drop |
| Release | open bed (wind, waves), pad, fewer sounds |
| Ending | let the bed breathe out 0.5–1 s beyond the last cut, or hard stop on a hit for a loop-friendly reel |

## Loopable reels

Reels autoplay on loop. For a seamless loop, make the last 0.3 s of audio match the first: end on the same bed at the same level, no fade out, and no hit on frame 1 (put the hook hit 2–4 frames in instead).
