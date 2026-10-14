# Sound map schema

One JSON file per reel. Keep it in the outputs: it is the editable source of the track.

## Top level

| Field | Type | Default | Meaning |
|---|---|---|---|
| `title` | str | "reel" | used in file names |
| `duration` | float s | required | exact reel length (from analysis.json) |
| `fps` | float | 30 | for cue sheet timecodes |
| `target_lufs` | float | −18 | integrated loudness of the delivered track |
| `true_peak` | float dB | −1.0 | ceiling; gain is held back to stay under it |
| `end_fade` | float s | 0.03 | fade on the last frames of every layer so the reel loops without a click |
| `duck` | list of `[start, end, dB]` | [] | lowers `ambience`, `bed` and `pad` layers (e.g. under voiceover), 0.25 s ramps |
| `cues` | list | required | see below |

## Cue fields

| Field | Meaning |
|---|---|
| `id` | short unique name; also seeds the generator, so the render is repeatable. Change the id or set `params.seed` to get a different variation |
| `layer` | stem name: `ambience`, `transitions`, `impacts`, `fx`, `pad` (any name works) |
| `src` | `synth:<generator>`, `rec:<name>` (looked up in /home/claude/sfx-library, uploads, --library dirs) or `file:<path>` |
| `at` | sync time in seconds (usually a cut time from analysis.json) |
| `anchor` | `start` / `peak` / `end`. Defaults: whoosh & swish → `peak`, riser & reverse_swell → `end`, everything else → `start` |
| `end` | for beds: stop time. Sets the length; recordings loop with crossfades if short |
| `params` | generator kwargs (`dur`, `seed`, `peak`, `low`, `high`, `pan_from`, `pan_to`, `strength`, `root`, `bpm` …) |
| `gain_db` | level before final normalisation (see craft.md) |
| `fade_in`, `fade_out` | seconds |
| `offset` | seconds into a recording to start from (skip a bad intro) |
| `hp`, `lp` | high-/low-pass cutoff in Hz |
| `pan` | −1 left to 1 right (collapses to mono first; whooshes pan themselves via params) |
| `pitch` | semitones (also changes length) |
| `reverse` | true to reverse |
| `reverb` | `{"decay": 1.2, "mix": 0.25}` |
| `process` | `tape_stop` or `stutter`, applied to the source |
| `loop` | false to stop a recording at its natural end |
| `gate` | picture-driven envelope, e.g. `{"curve": "brightness.json", "ref": 53, "max": 1.6}`: the cue follows the brightness curve from analyse_video (hum and room tone that fail with flickering lights). `ref` is the "normal" brightness (default: median); `floor`, `smooth` optional |
| `note` | why this sound is here; copied to the cue sheet |

## Worked example (15 s reel, 5 shots, cuts at 2.4, 5.1, 8.0, 11.2)

```json
{
  "title": "upwind grind", "duration": 15.0, "fps": 30,
  "duck": [[8.0, 11.2, -8]],
  "cues": [
    {"id": "hook-ting", "layer": "fx", "src": "synth:metal_ting", "at": 0.05, "gain_db": -14,
     "note": "hook: halyard in the boat park, frame 2"},
    {"id": "park", "layer": "ambience", "src": "rec:wind", "at": 0, "end": 2.6, "gain_db": -18,
     "hp": 120, "fade_out": 0.4, "note": "boat park bed"},
    {"id": "sea", "layer": "ambience", "src": "rec:waves", "at": 2.1, "end": 8.3, "gain_db": -18,
     "fade_in": 0.3, "fade_out": 0.5, "note": "J-cut: sea arrives 0.3 s before the launch shot"},
    {"id": "gusts", "layer": "ambience", "src": "rec:wind", "offset": 30, "at": 2.1, "end": 8.3,
     "gain_db": -15, "hp": 150, "fade_in": 0.3, "fade_out": 0.5, "note": "upwind wind, louder"},
    {"id": "cut1", "layer": "transitions", "src": "synth:whoosh", "at": 2.4, "gain_db": -11,
     "params": {"dur": 1.0, "pan_from": 0.7, "pan_to": -0.7}, "note": "boat moves right to left"},
    {"id": "hike", "layer": "fx", "src": "synth:heartbeat", "at": 5.1, "end": 8.0, "gain_db": -16,
     "params": {"bpm": 78}, "fade_in": 0.8, "note": "strain while hiking"},
    {"id": "build", "layer": "transitions", "src": "synth:riser", "at": 8.0, "gain_db": -12,
     "params": {"dur": 2.5}, "note": "build into the data section"},
    {"id": "drop", "layer": "impacts", "src": "synth:impact", "at": 8.0, "gain_db": -8,
     "note": "the one big hit"},
    {"id": "polar", "layer": "fx", "src": "synth:data_scan", "at": 8.2, "gain_db": -18,
     "params": {"dur": 2.0}, "note": "polar plot draws on"},
    {"id": "glue", "layer": "pad", "src": "synth:pad", "at": 8.0, "end": 15.0, "gain_db": -24,
     "params": {"root": "D"}, "fade_out": 1.2, "note": "brand pad, D minor"},
    {"id": "cut4", "layer": "transitions", "src": "synth:reverse_swell", "at": 11.2, "gain_db": -13,
     "note": "inhale into the final shot"},
    {"id": "end-sea", "layer": "ambience", "src": "rec:waves", "offset": 40, "at": 11.0, "end": 15.0,
     "gain_db": -20, "fade_in": 0.4, "note": "release: open water, calm"}
  ]
}
```

Note the gap before the 8.0 s drop: the riser chokes 30 ms early and the beds duck, giving a tiny silence before the hit. Ambience overlaps the cuts so they crossfade.
