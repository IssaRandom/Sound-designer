#!/usr/bin/env python3
"""Search Freesound for CC0 sounds and download them with licence sidecars.

    export FREESOUND_API_KEY=...          # free: https://freesound.org/apiv2/apply
    python freesound_fetch.py "fluorescent flicker" "neon buzz" --per-query 4 --dest sfx-library/freesound
    python freesound_fetch.py "rail screech" --list        # show candidates, download nothing

- Filters to CC0 only (license:"Creative Commons 0"), so nothing with BY, BY-NC or
  Sampling+ conditions gets into a reel.
- With just an API key it downloads the HQ preview (ogg, about 192 kbps): fine for
  auditioning and usually fine for layering. Set FREESOUND_OAUTH_TOKEN (an OAuth2
  access token from the user's own login) to get the original file instead.
- Writes <slug>.json next to each file (licence, author, source) so build_mix.py
  credits it, and shortlist.md with every candidate per query.
- Then run intake_library.py on the folder to convert, catalogue and view waveforms.

Needs network access to freesound.org and cdn.freesound.org.
"""
import argparse, json, os, re, sys, urllib.parse, urllib.request

API = 'https://freesound.org/apiv2'
FIELDS = 'id,name,username,license,url,duration,samplerate,channels,avg_rating,num_downloads,tags,previews'

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:50] or 'sound'

def get(url, headers=None):
    req = urllib.request.Request(url, headers={'User-Agent': 'reel-sound-designer', **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def search(query, key, n, min_dur, max_dur, sort):
    q = {'query': query, 'filter': f'license:"Creative Commons 0" duration:[{min_dur} TO {max_dur}]',
         'fields': FIELDS, 'page_size': n, 'sort': sort, 'token': key}
    return json.loads(get(f'{API}/search/text/?' + urllib.parse.urlencode(q)))['results']

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('queries', nargs='+')
    ap.add_argument('--dest', default=os.path.join(os.environ.get('SFX_LIBRARY', 'sfx-library'), 'freesound'))
    ap.add_argument('--per-query', type=int, default=4)
    ap.add_argument('--min-dur', type=float, default=0.3)
    ap.add_argument('--max-dur', type=float, default=60)
    ap.add_argument('--sort', default='score', help='score, rating_desc, downloads_desc, duration_asc ...')
    ap.add_argument('--list', action='store_true', help='print candidates only')
    a = ap.parse_args()
    key = os.environ.get('FREESOUND_API_KEY')
    if not key: sys.exit('Set FREESOUND_API_KEY (free at https://freesound.org/apiv2/apply).')
    oauth = os.environ.get('FREESOUND_OAUTH_TOKEN')
    os.makedirs(a.dest, exist_ok=True)
    md = ['# Freesound shortlist (CC0 only)\n']
    for q in a.queries:
        try:
            res = search(q, key, a.per_query, a.min_dur, a.max_dur, a.sort)
        except Exception as e:
            print(f'FAILED search "{q}": {e}'); continue
        md.append(f'\n## {q}\n\n| file | dur | rating | downloads | author | link |\n|---|---|---|---|---|---|')
        for s in res:
            if 'publicdomain/zero' not in s['license']:      # belt and braces on the filter
                continue
            name = f"{slug(q)}--{slug(os.path.splitext(s['name'])[0])}-{s['id']}"
            md.append(f"| {name} | {s['duration']:.1f}s | {s.get('avg_rating', 0):.1f} | {s.get('num_downloads', 0)} "
                      f"| {s['username']} | {s['url']} |")
            print(f"{q[:24]:24s} {s['duration']:6.1f}s  {s['username'][:18]:18s} {s['name'][:50]}")
            if a.list: continue
            try:
                if oauth:
                    data = get(f"{API}/sounds/{s['id']}/download/", {'Authorization': f'Bearer {oauth}'})
                    ext = os.path.splitext(s['name'])[1].lower() or '.wav'; quality = 'original'
                else:
                    data = get(s['previews']['preview-hq-ogg']); ext = '.ogg'; quality = 'HQ preview'
            except Exception as e:
                print(f"  FAILED download {s['id']}: {e}"); continue
            open(os.path.join(a.dest, name + ext), 'wb').write(data)
            json.dump({'licence': 'CC0 1.0', 'author': s['username'], 'source': s['url'],
                       'via': f'Freesound API ({quality})', 'query': q},
                      open(os.path.join(a.dest, name + '.json'), 'w'), indent=1)
    open(os.path.join(a.dest, 'shortlist.md'), 'w').write('\n'.join(md) + '\n')
    print(f"shortlist: {os.path.join(a.dest, 'shortlist.md')}")
