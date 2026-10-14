"""Phone body layers (body_hook, body_reveal, body_end): mid-range hits so the big
moments still read on a phone speaker. The rest of the v1 generator (synth tube,
zaps, drone, screech) was superseded by gen_v2.py and has been dropped."""
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, '.claude', 'skills', 'reel-sound-designer', 'scripts'))
import synth as S
SR = S.SR
OUT = os.path.join(HERE, 'custom', '')
os.makedirs(OUT, exist_ok=True)

def body_hit(dur, f0, f1, seed, grit=0.4):
    rr = np.random.default_rng(seed); n = int(dur * SR); tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt / 0.08)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR)
    thud = S.tv_band(S.white(n, rr), [700, 250], q=1.1) * grit
    e = np.minimum(1, tt / 0.003) * np.exp(-tt / (dur * 0.22))
    x = S.saturate((tone + thud) * e * 1.5, 3.5)
    return S.reverb(S.widen(S.norm(x, .9), rr, .4), 2.6, .35)

for name, args in [('body_hook', (1.4, 320, 110, 31)), ('body_reveal', (1.6, 260, 85, 32, 0.6)),
                   ('body_end', (2.0, 300, 70, 33, 0.7))]:
    S.write_wav(OUT + name + '.wav', body_hit(*args))
    json.dump({'licence': 'original', 'author': 'synthesised for this reel', 'source': 'gen_custom.py'},
              open(OUT + name + '.json', 'w'))
print('bodies ok')
