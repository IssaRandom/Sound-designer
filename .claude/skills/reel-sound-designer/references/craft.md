# Sound design craft for short-form video

## Timing

At 30 fps one frame is 33 ms; at 25 fps, 40 ms. People notice audio that is 2 or more frames late against a hard visual event, and forgive audio that is slightly early. When in doubt, land a frame early.

| Sound | Sync point | Rule of thumb |
|---|---|---|
| Whoosh | peak on the cut, or 1 frame before | 0.6–1.2 s long; peak at about 55% of its length |
| Swish | peak on the cut | 0.25–0.45 s; for cuts under 0.8 s apart, or text pops |
| Riser | ends on the cut / drop | 1.5–4 s. Short risers feel urgent, long ones cinematic. Never longer than the shot it sits under plus one |
| Reverse swell | ends on the cut | 0.8–2 s; softer, more "inhale" than a riser |
| Impact / sub drop | starts on the cut | layer both for the one biggest moment only |
| Tick / blip | on the frame the graphic appears | every number, line, or overlay element that pops on |
| Ambience change | 0.2–0.5 s before the cut (J-cut) | crossfade 0.3–0.8 s; or carry out after the cut (L-cut) for continuity |

If music is supplied with a BPM, put big hits on downbeats: beat length = 60 / BPM s; bar = 4 beats. Nudge the hit to the nearest beat if it is within 2 frames of the cut; otherwise the cut wins.

## Layering a designed moment

A great transition is usually three layers, not one sound:

1. **Body**: the main event (whoosh, impact).
2. **Air/sweetener**: high, short detail (swish, tick, a little reverse swell).
3. **Weight**: sub drop or low thump, saturated so it survives a phone speaker.

Keep each layer quieter than you think; the stack does the work. Save the full three-layer treatment for the 1–3 biggest moments.

## Levels (starting points, gain_db in the sound map)

| Layer | gain_db | Notes |
|---|---|---|
| Ambience bed | −20 to −14 | quieter under talking or text-heavy shots |
| Hull hiss / close water | −20 to −15 | bright, tires ears fast: short spans only |
| Whoosh / swish | −14 to −8 | |
| Riser | −14 to −10 | |
| Impact | −10 to −6 | |
| Sub drop | −12 to −8 | |
| Tick / data scan | −22 to −16 | precise, not loud |
| Pad | −26 to −20 | felt more than heard |

The build normalises the whole track to the target loudness afterwards, so these set the balance between sounds, not the final level.

## Frequency space

- High-pass beds at 80–150 Hz so they do not fight the music's bass.
- If there is voiceover, keep beds out of 1–4 kHz with `lp` ~ 3000 or duck them (`duck` in the sound map, −6 to −10 dB).
- One thing at a time owns the low end. Do not stack a sub drop on a pad note on a bass-heavy music drop; pick one.

## Loudness for social

- The SFX track is delivered at −18 LUFS integrated, true peak below −1 dBTP, so music and voice can sit on top.
- Around −14 LUFS integrated for the final, mixed reel is the commonly used target for social platforms. Instagram does not, as far as I know, publish an official loudness spec, so treat −14 as a convention, not a requirement, and say so if asked.
- The build applies gain only (no limiter) so stems always sum exactly to the mix. If a loud hit stops the track reaching target, it reports it; reduce that hit rather than squash everything.

## Things that make reels sound cheap

- A whoosh on every cut. Same whoosh repeated.
- Ambience that starts and stops exactly on the cuts (no J/L-cuts).
- Effects that do not match scale: a huge cinematic impact on a small hand gesture.
- Sounds for things not on screen, unless it is deliberate off-screen world-building (a distant halyard ting in the dinghy park is good; random seagulls in a gym are not).
- Long fade-ins at the start. The first frame should already sound like somewhere.
- Everything at the same level, no dynamics, no moment of quiet before the biggest hit.

## Techniques that worked

- **Gate beds to the picture.** For flickering lights, gate the hum and room tone with `gate` on `brightness.json`. Add a short arc or crackle on each `dark` light event and a bigger one on each `flash`.
- **A mid-range body on every big hit.** Library booms and synthetic subs can vanish on phones. Measure the phone-filtered level (high-pass 180 Hz, RMS per 0.1 s): the hook, reveal and final hit should stand 5–10 dB above their surroundings. If not, layer a saturated 100–400 Hz body hit.
- **Choke before the reveal and the cut to black.** End risers, drones and beds 3–8 frames early; keep only the hero sound (for example the hum) running into the hit if it is the thing that "dies" on the cut.
- **Name the hero sound** in the cue sheet so revisions keep it on top.
