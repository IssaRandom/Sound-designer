# Sourcing brief template (library-required briefs)

Send this, filled in for the actual edit, as soon as a brief is cinematic, eerie, horror, trailer or "high-end". Keep it to one screen.

## Structure

1. One line: why (synthesis cannot give layered, designed cinematic sound; the sandbox cannot reach the libraries; user downloads, Claude designs).
2. Where: Signature Sounds (CC0 designed packs) for booms, drones, risers, stingers; Freesound filtered to CC0 and BigSoundBank (CC0) for real-world foley and ambience; Sonniss GDC bundle with its licence caveat. Avoid CC BY-NC.
3. What: 5–8 numbered items tied to moments in the edit. Mark the **hero sound**.
4. How: plain file names (`fluoro-flicker.wav`), zip is fine, and a `licences.csv` (file,licence,author,source) or a note of site and licence per file.

## Per-moment shopping list patterns

| Moment in picture | Ask for | Freesound search terms |
|---|---|---|
| lights flicker / power failing | real fluorescent tube flicker and buzz, starter clicks | fluorescent flicker, neon buzz, tube light starter |
| empty interior / station / corridor | night room tone with long reverb | empty station night, underground platform ambience, hallway room tone |
| distant threat, held shot | rail screech, train brakes, metal stress | rail screech, train brakes squeal, metal creak |
| white flash / short circuit | electrical arc, spark, transformer pop | electric arc, spark short circuit, electrical zap |
| reveal / cut to black | 2–3 cinematic booms or trailer hits with long tails | cinematic boom, trailer hit, impact reverb tail |
| tension under everything | dark drone, low tension bed | dark drone, tension ambience, horror drone |
| build to a cut | deep riser, reverse swell | riser, tension build, reverse cymbal swell |
| optional world detail | distant garbled announcement chime, whisper | station chime, PA announcement distant |

For sailing and athlete reels the same structure applies; the vocabulary is in `sound_vocabulary.md`.

## After the upload

Run `scripts/intake_library.py`, read `catalogue.md`, view `waveforms.png`, shortlist per moment, test-render candidates and keep the existing sound map timings. Swap synth layers for real ones; keep synth only for gating, sub weight and frame-exact sweeteners.
