#!/usr/bin/env bash
# v3 sourcing for the platform fog hook: the handoff shopping list, in impact order.
# Needs freesound.org / cdn.freesound.org (FREESOUND_API_KEY) and, for generation,
# api.elevenlabs.io (ELEVENLABS_API_KEY, paid plan for commercial use).
# Run from the repo root. Then: intake_library.py, read catalogue.md, shortlist 2-3 per moment.
set -u
S=.claude/skills/reel-sound-designer/scripts
LIB=${SFX_LIBRARY:-sfx-library}

if [ -n "${FREESOUND_API_KEY:-}" ]; then
  python3 $S/freesound_fetch.py --per-query 4 --dest "$LIB/freesound" \
    "fluorescent flicker" "fluorescent buzz" "tube light starter" \
    "cinematic boom" "trailer hit" \
    "rail screech" "train brakes squeal" \
    "electric arc" "short circuit spark" \
    "underground station ambience" "empty platform night" \
    "dark drone" "riser tension" \
    "station chime"
else
  echo "skip Freesound: set FREESOUND_API_KEY"
fi

if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
  G="python3 $S/elevenlabs_sfx.py --dest $LIB/generated --variations 3"
  $G "old fluorescent tube light buzzing at 50 Hz in an empty underground station, ballast hum, irregular starter clicks, flickering, close mic" --name tube --dur 6
  $G "massive cinematic trailer boom, deep sub impact, metallic body, very long dark reverb tail fading to silence" --name boom --dur 5
  $G "distant train wheels screeching on steel rails in a tunnel, metallic squeal bending upward, cavernous reverb" --name screech --dur 3
  $G "violent electrical arc short circuit, crackling sparks, transformer pop, sizzle tail" --name arc --dur 1.5
  $G "empty underground train platform at night, low air handling rumble, distant tunnel wind, no voices" --name room --dur 10 --variations 2
  $G "dark horror tension drone slowly rising in pitch and intensity, low strings and metal resonance" --name riser --dur 6 --variations 2
else
  echo "skip ElevenLabs: set ELEVENLABS_API_KEY"
fi

python3 $S/intake_library.py "$LIB/freesound" "$LIB/generated" --dest "$LIB/v3" 2>/dev/null \
  && echo "now read $LIB/v3/catalogue.md"
