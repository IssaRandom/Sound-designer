"""v2 sound sources: real CC0 recordings (Noisekun/Freesound) reshaped into designed
layers, plus synthesis only where nothing recorded is reachable (mains hum, arcs)."""
import os, sys, json, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, '.claude', 'skills', 'reel-sound-designer', 'scripts'))
import synth as S
from scipy import signal
SR = S.SR; OUT = os.path.join(HERE, 'custom', '')
LIB = os.path.join(os.environ.get('SFX_LIBRARY', os.path.join(ROOT, 'sfx-library')), 'cc0', '')
os.makedirs(OUT, exist_ok=True)
r = np.random.default_rng(7)
CREDIT = {'storm': ('Borys Kozielski', 'https://freesound.org/people/Borys_Kozielski/sounds/316831/'),
          'wind': ('Felix Blume', 'https://freesound.org/people/felix.blume/sounds/217506/'),
          'underwater': ('Tim Verberne', 'https://freesound.org/people/Tim_Verberne/sounds/482167/'),
          'boat': ('Falcet', 'https://freesound.org/people/Falcet/sounds/439365/'),
          'brown-noise': ('George Dyer', 'https://freesound.org/people/georgedyer/sounds/171552/')}

def rec(name, start, dur):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', LIB + name + '.ogg',
                          '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def save(fn, x, srcs):
    S.write_wav(OUT + fn + '.wav', np.clip(x, -1, 1))
    if srcs:
        a = '; '.join(f'{CREDIT[s][0]} ({CREDIT[s][1]})' for s in srcs)
        cr = {'licence': 'CC0 1.0 (derived)', 'author': a, 'source': 'reshaped from Noisekun CC0 recordings'}
    else:
        cr = {'licence': 'original', 'author': 'synthesised for this reel', 'source': 'gen_v2.py'}
    json.dump(cr, open(OUT + fn + '.json', 'w'))

def resample_pitch(x, semis):
    rr = 2 ** (semis / 12); idx = np.arange(0, len(x) - 1, rr)
    return np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(x.shape[1])], 1)

def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], 'bp', fs=SR, output='sos'), x, axis=0)
def lp(x, f): return signal.sosfilt(signal.butter(2, f, 'lp', fs=SR, output='sos'), x, axis=0)
def hp(x, f): return signal.sosfilt(signal.butter(2, f, 'hp', fs=SR, output='sos'), x, axis=0)
def env_ad(n, a, d):
    t = np.arange(n) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d))[:, None]

def comb(x, f, fb=0.985):
    """Feedback comb tuned to f: turns real air into a singing tone."""
    D = int(SR / f); y = np.zeros_like(x)
    for i in range(len(x)):
        y[i] = x[i] + (fb * y[i - D] if i >= D else 0)
    return y

# --- 1. Trailer hits: transient + real thunder body + sub, three weights ----------
def trailer_hit(thunder_at, semis, dur, sub_f, crack_gain, seed, tail_mix=.45):
    rr = np.random.default_rng(seed); n = int(dur * SR)
    th = rec('storm', thunder_at, dur * 2 ** (-semis / 12) + .2)
    th = resample_pitch(th, semis)[:n]; th = np.pad(th, ((0, n - len(th)), (0, 0)))
    th = lp(hp(th, 30), 3500) * (env_ad(n, .004, .32) * .85 + env_ad(n, .004, dur * .5) * .15)
    t = np.arange(n) / SR
    f = sub_f * (1 + 1.5 * np.exp(-t / .05))
    sub = S.stereo(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (dur * .3)))
    crack = S.stereo(S.tv_band(S.white(n, rr), [2500, 900], q=.8) * np.exp(-t / .03)) * crack_gain
    body = S.stereo(S.saturate(np.sin(2 * np.pi * np.cumsum(sub_f * 3 * (1 + np.exp(-t / .04))) / SR)
                               * np.exp(-t / .25), 3)) * .5
    front = S.norm(S.saturate(sub * 1.0 + crack * 1.3 + body, 1.4), .95)
    x = front + S.norm(th, .9) * .45
    return S.reverb(S.norm(x, .95), 3.2, tail_mix * .6)
save('hit_reveal', trailer_hit(10.46, -5, 3.0, 42, .5, 1), ['storm'])
save('hit_end', trailer_hit(45.96, -7, 3.2, 36, .6, 2, .5), ['storm'])
save('hit_hook', trailer_hit(50.82, -9, 2.6, 34, .25, 3, .4), ['storm'])
save('hit_flash', trailer_hit(12.08, -3, 1.8, 55, .8, 4, .35), ['storm'])

# --- 2. Real-air drones: wind and brown noise through tuned combs (A, B-flat, E-flat) ----
w = lp(rec('wind', 20, 8.5), 2000)
dr = sum(comb(w[:, c:c + 1].ravel(), f, .992)[:, None] * g for c, (f, g) in enumerate([(55, 1.0), (58.27, .8)]))
dr = np.concatenate([dr, comb(w[:, 1], 77.78, .99)[:, None] * .6], 1)[:, :2]
dr = S.saturate(S.norm(hp(dr, 35), .8) * 1.3, 1.8)
save('drone_air', S.reverb(S.widen(S.norm(dr[:, 0], .8), r, .7), 2.5, .4), ['wind'])

# --- 3. Fog push: real underwater pressure + wind, slowed ---------------------------
uw = resample_pitch(rec('underwater', 12, 3.0), -4)[:int(2.1 * SR)]
wd = resample_pitch(rec('wind', 50, 3.0), -6)[:int(2.1 * SR)]
fog = S.norm(lp(uw, 1800), .8) * .8 + S.norm(bp(wd, 120, 3000), .8) * .7
n = len(fog); e = np.linspace(.4, 1, n)[:, None]
save('fog_push', S.reverb(fog * e, 1.8, .3), ['underwater', 'wind'])

# --- 4. Reverse swells made from real thunder tails --------------------------------
def rev_swell(at, dur, semis, seed):
    x = resample_pitch(rec('storm', at, dur * 1.6), semis)[:int(dur * SR)]
    x = S.reverb(lp(x, 5000), 3.0, .6)[:int(dur * SR)][::-1]
    t = np.linspace(0, 1, len(x))[:, None]
    return S.norm(x * t ** 1.6, .9)
save('suck_reveal', rev_swell(11.2, 1.5, -3, 1), ['storm'])
save('suck_flash', rev_swell(46.6, .7, 0, 2), ['storm'])
save('suck_end', rev_swell(51.2, 1.4, -5, 3), ['storm'])

# --- 5. Station room tone: brown noise + wind in a long, dark space -----------------
N5 = int(5.2 * SR); room = S.norm(lp(rec('brown-noise', 3, 5.2), 600), .7)[:N5] + S.norm(bp(resample_pitch(rec('wind', 70, 8), -8), 80, 900), .7)[:N5] * .6
save('station_room', S.reverb(room, 3.5, .5), ['brown-noise', 'wind'])

# --- 6. Structural groans: real hull creaks pitched down an octave ------------------
cr = rec('boat', 4, 9)
cr = resample_pitch(bp(cr, 250, 4000), -12)
save('groan', S.reverb(S.norm(cr, .8), 3.5, .55), ['boat'])

# --- 7. Fluorescent tube (synth: no CC0 hum recording reachable) ---------------------
def tube(dur, seed):
    rr = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    jit = 1 + 0.002 * S.norm(lp(S.white(n, rr)[:, None], 3).ravel(), 1)
    ph = 2 * np.pi * np.cumsum(100 * jit) / SR
    x = sum(a * np.sin(k * ph + rr.uniform(0, 6)) for k, a in [(1, 1), (2, .6), (3, .5), (5, .3), (7, .2), (9, .14), (13, .08), (17, .05)])
    rattle = (np.sin(ph) > .92) * rr.uniform(.3, 1, n) * .25          # ballast buzz edges
    hiss = S.tv_band(S.white(n, rr), [5000], q=.9) * .06
    return S.stereo(S.saturate((x * .55 + rattle) * 1.0, 2.8) + hiss, 0)
save('tube', S.norm(tube(5.2, 3), .8), [])

# --- 8. Arcs and flicker crackles: synth arc + real rain sizzle ---------------------
rain = hp(rec('storm', 30, 4), 2500)
def arc(dur, seed, big):
    rr = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    imp = (rr.random(n) < (.03 if big else .01)) * rr.uniform(-1, 1, n)
    crack = signal.lfilter([1, -.8], [1], imp)
    sz = S.norm(rain[rr.integers(0, len(rain) - n):][:n, 0], 1) * (1.4 if big else .8)
    buzz = S.saturate(np.sin(2 * np.pi * 100 * t) * 4, 4) * .5
    gate = (lp((rr.random(n) > .5).astype(float)[:, None], 60).ravel() > .5)
    x = (crack + sz * gate + buzz * gate) * (np.minimum(1, t / .004) * np.exp(-t / (dur * .35)))
    return S.reverb(S.widen(S.norm(x, .9), rr, .5), 1.4 if big else .8, .3 if big else .15)
for i, (d, big) in enumerate([(.5, 1), (.6, 1)]): save(f'arc{i}', arc(d, 30 + i, big), ['storm'])
for i in range(5): save(f'crackle{i}', arc(.09 + .02 * (i % 3), 50 + i, 0), ['storm'])

# --- 9. Distant rail screech: synth bowed metal through real wind --------------------
def screech(dur, seed):
    rr = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    bend = 1 + .07 * (t / dur) ** 2; vib = 1 + .01 * np.sin(2 * np.pi * 6 * t) * (t / dur)
    x = sum(a * np.sin(2 * np.pi * np.cumsum(f * bend * vib) / SR) for f, a in [(1180, 1), (1747, .55), (2410, .35), (3130, .2)])
    rough = 1 + .5 * S.norm(lp(S.white(n, rr)[:, None], 40).ravel(), 1)
    air = bp(rec('wind', 30, dur)[:n, 0], 900, 3500)
    x = (S.norm(x * rough, 1) * .7 + S.norm(air, 1) * .3) * (t / dur) ** 1.8
    return S.reverb(S.stereo(S.norm(x, .8), .35), 3.0, .5)
save('screech', screech(1.3, 9), ['wind'])
print('ok')
