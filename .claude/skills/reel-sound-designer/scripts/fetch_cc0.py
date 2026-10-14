#!/usr/bin/env python3
"""Fetch CC0 field recordings that are reachable from the sandbox (GitHub only).

    python fetch_cc0.py [--dest $SFX_LIBRARY/cc0] [names...]     # default: all below

Only files whose upstream licence is CC0 are listed. Noisekun also ships CC BY,
CC BY-SA and commercial-licence files (waterfall, rain-on-tent, white/pink noise,
washing machine, train): they are deliberately excluded.
Each file gets a sidecar .json with licence, author and source for the credits file.
"""
import argparse, json, os, subprocess, urllib.request

RAW = 'https://raw.githubusercontent.com/mateusfg7/Noisekun/main/.github/assets/sounds/'
CATALOGUE = {
    # name: (author, upstream source, what it is good for)
    'wind':        ('Felix Blume', 'https://freesound.org/people/felix.blume/sounds/217506/',
                    'real outdoor wind: exposed coast, open water, hiking out'),
    'boat':        ('Falcet', 'https://freesound.org/people/Falcet/sounds/439365/',
                    'boat on water, hull creak and slap: harbour, launching, drifting'),
    'underwater':  ('Tim Verberne', 'https://freesound.org/people/Tim_Verberne/sounds/482167/',
                    'muffled underwater: capsize, GoPro dunk, slow-motion dreamy moments'),
    'storm':       ('Borys Kozielski', 'https://freesound.org/people/Borys_Kozielski/sounds/316831/',
                    'thunder and rain: heavy-weather days, moody intros'),
    'leaves':      ('Stek59', 'https://freesound.org/people/Stek59/sounds/457318/',
                    'rustling leaves: shore-side, cycling through countryside'),
    'brown-noise': ('George Dyer', 'https://freesound.org/people/georgedyer/sounds/171552/',
                    'smooth low bed: underlay to glue cuts together'),
    # Credited upstream as CC0 by "SFX Producer" (YouTube). Provenance is thinner
    # than the Freesound ones; fine for reels but flag it in the credits.
    'waves':       ('SFX Producer (YouTube)', 'https://www.youtube.com/watch?v=SL9NdTMsIUk',
                    'shoreline waves: beach launch, coastline establishing shots'),
    'birds-tree':  ('SFX Producer (YouTube)', 'https://www.youtube.com/watch?v=J6OGbkl4Vrs',
                    'land birdsong (NOT seagulls): dawn rides, gardens'),
    'stream-water':('SFX Producer (YouTube)', 'https://www.youtube.com/watch?v=cN5sGvQ_m_c',
                    'running water: hose-down, rinse, close water movement'),
    'rain':        ('SFX Producer (YouTube)', 'https://www.youtube.com/watch?v=3oMcTXhXOpc',
                    'steady rain'),
}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('names', nargs='*'); ap.add_argument('--dest', default=None)
    a = ap.parse_args()
    # $SFX_LIBRARY, else ./sfx-library (in claude.ai the cwd is /home/claude; skills are read-only)
    dest = a.dest or os.path.join(os.environ.get('SFX_LIBRARY', 'sfx-library'), 'cc0')
    os.makedirs(dest, exist_ok=True)
    for n in a.names or CATALOGUE:
        author, src, use = CATALOGUE[n]
        ogg = os.path.join(dest, n + '.ogg')
        if not os.path.exists(ogg):
            try:
                urllib.request.urlretrieve(RAW + n + '.ogg', ogg)
            except Exception as e:
                print(f'FAILED {n}: {e}'); continue
        json.dump({'licence': 'CC0 1.0', 'author': author, 'source': src, 'use': use,
                   'via': 'github.com/mateusfg7/Noisekun'}, open(os.path.join(dest, n + '.json'), 'w'), indent=1)
        d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
                            'csv=p=0', ogg], capture_output=True, text=True).stdout.strip()
        print(f'{n:13s} {float(d):6.1f}s  {use}')
