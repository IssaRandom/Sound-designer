"""Welsh-mountain layers for the hiking intro: real CC0 wind and rain, reshaped.
Reuses the platform sounds from ../platform_fog_hook/custom (run gen_v2.py and
gen_custom.py there first). Run fetch_cc0.py wind storm first."""
import os, sys, json, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, '.claude', 'skills', 'reel-sound-designer', 'scripts'))
import synth as S
from scipy import signal
SR = S.SR; OUT = os.path.join(HERE, 'custom', '')
LIB = os.path.join(os.environ.get('SFX_LIBRARY', os.path.join(ROOT, 'sfx-library')), 'cc0', '')
os.makedirs(OUT, exist_ok=True)
CREDIT = {'storm': ('Borys Kozielski', 'https://freesound.org/people/Borys_Kozielski/sounds/316831/'),
          'wind': ('Felix Blume', 'https://freesound.org/people/felix.blume/sounds/217506/')}

def rec(name, start, dur):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', LIB + name + '.ogg',
                          '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def save(fn, x, srcs):
    S.write_wav(OUT + fn + '.wav', np.clip(x, -1, 1))
    a = '; '.join(f'{CREDIT[s][0]} ({CREDIT[s][1]})' for s in srcs)
    json.dump({'licence': 'CC0 1.0 (derived)', 'author': a, 'source': 'reshaped from Noisekun CC0 recordings'},
              open(OUT + fn + '.json', 'w'))

def resample_pitch(x, semis):
    rr = 2 ** (semis / 12); idx = np.arange(0, len(x) - 1, rr)
    return np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(x.shape[1])], 1)
def bp(x, lo, hi): return signal.sosfilt(signal.butter(2, [lo, hi], 'bp', fs=SR, output='sos'), x, axis=0)
def hp(x, f): return signal.sosfilt(signal.butter(2, f, 'hp', fs=SR, output='sos'), x, axis=0)
def lp(x, f): return signal.sosfilt(signal.butter(2, f, 'lp', fs=SR, output='sos'), x, axis=0)
def peak(x, f, q, g):
    b, a = signal.iirpeak(f, q, fs=SR); return x + g * signal.lfilter(b, a, x, axis=0)

# 1. Mountain wind through the fog: the real gust at 46-53 s, slowed a touch, wide and dark.
#    A peak at 380 Hz and 760 Hz gives it a hollow, hill-pass moan without synth tone.
w = resample_pitch(rec('wind', 46.0, 3.0), -3)[:int(2.2 * SR)]
w = peak(peak(lp(hp(w, 40), 3000), 380, 6, 1.5), 760, 8, .8)
n = len(w); e = (np.linspace(.55, 1, n) ** 1.5)[:, None]
save('mountain_wind', S.reverb(S.norm(w * e, .85), 2.2, .25), ['wind'])

# 2. Rain on the station canopy: steady rain from the calm part of the storm, high-passed
#    so it reads as drops on a roof, with the station's long reverb. Gloomy Welsh weather.
r = hp(rec('storm', 64, 6.0), 900)
r = lp(r, 9000)
save('rain_canopy', S.reverb(S.norm(r, .8), 2.8, .45), ['storm'])

# 3. Summit wind: the strongest real gust (8-10 s in the recording) hits on the cut to black,
#    then the same continuous take settles into exposed mountain-top wind for 14 s, to run
#    under the summit shot. One unspliced take, so the reel and the handoff join seamlessly.
#    A thin whistle (the same wind, resonant at 1.8 kHz) gives the ridge edge on a phone.
g = rec('wind', 7.6, 14.5)
body = peak(lp(hp(g, 35), 5000), 420, 5, 1.0)
whistle = signal.lfilter(*signal.iirpeak(1800, 14, fs=SR), bp(g, 1200, 3000), axis=0)
x = S.norm(body, .9) + S.norm(whistle, .9) * .18
t = np.arange(len(x)) / SR
env = np.minimum(1, t / .06) * (0.75 + 0.25 * np.exp(-t / 1.5))
save('summit_wind', S.reverb(S.norm(x * env[:, None], .9), 2.0, .2), ['wind'])
print('ok')
