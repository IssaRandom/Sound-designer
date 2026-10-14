#!/usr/bin/env python3
"""Procedural sound design engine for reels. numpy + scipy only.

Every generator returns a float32 stereo array of shape (n, 2) at SR.
Use as a module (build_mix.py imports it) or from the CLI to audition:

    python synth.py whoosh --dur 1.0 --seed 4 --out whoosh.wav
    python synth.py list
"""
import argparse, json, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000


# ---------- helpers ----------
def rng(seed):
    return np.random.default_rng(seed)

def t_axis(dur):
    return np.arange(int(dur * SR)) / SR

def white(n, r):
    return r.standard_normal(n)

def pink(n, r):
    X = np.fft.rfft(r.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR); f[0] = f[1]
    y = np.fft.irfft(X / np.sqrt(f), n)
    return y / (np.abs(y).max() + 1e-9)

def brown(n, r):
    y = np.cumsum(r.standard_normal(n))
    y = signal.sosfilt(signal.butter(1, 20, 'hp', fs=SR, output='sos'), y)
    return y / (np.abs(y).max() + 1e-9)

def norm(x, peak=0.9):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x

def stereo(x, pan=0.0):
    """Equal-power pan, pan in -1..1 (scalar or per-sample array)."""
    pan = np.clip(pan, -1, 1)
    a = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1).astype(np.float32)

def widen(mono, r, amount=0.5):
    """Decorrelated stereo from a mono source (for noise beds)."""
    d = int(SR * 0.011)
    side = np.concatenate([np.zeros(d), mono[:-d]]) - mono
    L, R = mono + amount * side, mono - amount * side
    return np.stack([L, R], 1).astype(np.float32)

def tv_band(x, centre_hz, q=1.2, nper=1024):
    """Time-varying band-pass via STFT masking. centre_hz: array over time."""
    f, tt, Z = signal.stft(x, SR, nperseg=nper)
    c = np.interp(tt, np.linspace(0, len(x) / SR, len(centre_hz)), centre_hz)
    lf = np.log2(np.maximum(f, 1))[:, None]
    lc = np.log2(np.maximum(c, 20))[None, :]
    Z *= np.exp(-0.5 * ((lf - lc) * q) ** 2)
    _, y = signal.istft(Z, SR, nperseg=nper)
    return y[:len(x)] if len(y) >= len(x) else np.pad(y, (0, len(x) - len(y)))

def reverb(x, decay=1.2, mix=0.25, seed=0, bright=6000):
    """Cheap algorithmic-feel reverb: convolve with decaying filtered noise."""
    r = rng(seed)
    n = int(decay * SR)
    ir = r.standard_normal(n) * np.exp(-6.9 * np.arange(n) / n)
    ir = signal.sosfilt(signal.butter(2, bright, 'lp', fs=SR, output='sos'), ir)
    ir /= np.sqrt((ir ** 2).sum())
    mono = x.ndim == 1
    xs = x[:, None] if mono else x
    out = []
    for ch in range(xs.shape[1]):
        wet = signal.fftconvolve(np.pad(xs[:, ch], (0, n)), np.roll(ir, ch * 37))
        wet = wet[:len(xs) + n]
        dry = np.pad(xs[:, ch], (0, n))
        out.append((1 - mix) * dry + mix * wet)
    y = np.stack(out, 1)
    return y[:, 0] if mono else y

def saturate(x, drive=2.0):
    """Adds harmonics so sub content still reads on phone speakers."""
    return np.tanh(drive * x) / np.tanh(drive)

def env_adsr(n, a, d, s, rel):
    a, d, rel = int(a * SR), int(d * SR), int(rel * SR)
    sus = max(n - a - d - rel, 0)
    e = np.concatenate([np.linspace(0, 1, a), np.linspace(1, s, d),
                        np.full(sus, s), np.linspace(s, 0, rel)])
    return np.pad(e, (0, max(n - len(e), 0)))[:n]


# ---------- transitions ----------
def whoosh(dur=0.9, peak=0.55, low=250, high=3500, pan_from=-0.7, pan_to=0.7,
           seed=0, air=0.5, **_):
    """Air pass-by. Loudest and brightest at `peak` (fraction of dur):
    put that moment on the cut."""
    r = rng(seed); n = int(dur * SR); t = np.linspace(0, 1, n)
    shape = np.where(t < peak, (t / peak) ** 2.2, ((1 - t) / (1 - peak)) ** 1.6)
    centre = low * (high / low) ** shape
    x = tv_band(pink(n, r), centre, q=1.0)
    x += air * tv_band(white(n, r), centre * 2.2, q=1.6)
    x *= shape ** 1.3
    pan = pan_from + (pan_to - pan_from) * t
    return stereo(norm(x), pan)

def swish(dur=0.35, seed=0, **k):
    """Short, tight whoosh for fast cuts and text."""
    return whoosh(dur=dur, peak=0.6, low=900, high=7000, air=0.8, seed=seed, **k)

def riser(dur=3.0, f0=110, f1=880, noise=0.6, tone=0.5, seed=0, choke=0.03, **_):
    """Tension build that ENDS at the cut/drop. Noise sweep + rising detuned tone."""
    r = rng(seed); n = int(dur * SR); t = np.linspace(0, 1, n)
    amp = t ** 2.5
    nz = tv_band(pink(n, r), 300 * (12000 / 300) ** (t ** 1.5), q=0.8)
    f = f0 * (f1 / f0) ** (t ** 1.7)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tn = sum(signal.sawtooth(ph * dt) for dt in (1.0, 1.006, 0.994)) / 3
    tn = signal.sosfilt(signal.butter(2, 4000, 'lp', fs=SR, output='sos'), tn)
    tn *= 1 + 0.3 * np.sin(2 * np.pi * (2 + 14 * t ** 2) * t * dur)  # accelerating flutter
    x = (noise * norm(nz) + tone * norm(tn)) * amp
    c = int(choke * SR)
    if c: x[-c:] *= np.linspace(1, 0, c)
    y = widen(norm(x), r, 0.3 + 0.5 * 1)
    return y * np.linspace(0.6, 1, n)[:, None]

def reverse_swell(dur=1.5, seed=0, **_):
    """Reversed reverb tail sucking into the cut. Ends at the cut."""
    hit = impact(dur=0.4, seed=seed, sub=0.3)
    tail = reverb(hit[:, 0], decay=dur, mix=1.0, seed=seed)
    y = tail[::-1][-int(dur * SR):]
    return stereo(norm(y * np.linspace(0, 1, len(y)) ** 1.5))

def tape_stop(src, dur=0.6, **_):
    """Slow a mono/stereo source to a halt (pitch + speed drop)."""
    n = int(dur * SR)
    speed = np.linspace(1, 0.02, n) ** 1.5
    pos = np.cumsum(speed); pos = pos[pos < len(src) - 1]
    s = src if src.ndim == 2 else src[:, None]
    y = np.stack([np.interp(pos, np.arange(len(s)), s[:, c]) for c in range(s.shape[1])], 1)
    return (y * np.linspace(1, 0, len(y))[:, None] ** 0.5).astype(np.float32)

def stutter(src, slice_s=0.06, repeats=6, **_):
    """Glitch repeat of the first slice of a source, shrinking each time."""
    out = []
    s = src if src.ndim == 2 else src[:, None]
    for i in range(repeats):
        seg = s[:max(int(slice_s * SR * (1 - i / (repeats + 2))), 64)]
        out.append(seg * np.hanning(len(seg))[:, None])
    return np.concatenate(out).astype(np.float32)


# ---------- hits ----------
def impact(dur=1.8, sub=1.0, body=0.6, click=0.5, f_hi=90, f_lo=38, seed=0,
           room=0.25, **_):
    """Cinematic hit: pitch-dropping sub + body thump + transient + room.
    Saturated so it still reads on phone speakers."""
    r = rng(seed); n = int(dur * SR); tt = np.arange(n) / SR
    f = f_lo + (f_hi - f_lo) * np.exp(-tt * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.2)
    b = signal.sosfilt(signal.butter(2, [120, 900], 'bp', fs=SR, output='sos'),
                       white(n, r)) * np.exp(-tt * 18)
    c = signal.sosfilt(signal.butter(2, 2500, 'hp', fs=SR, output='sos'),
                       white(n, r)) * np.exp(-tt * 120)
    x = sub * saturate(norm(s), 2.5) + body * norm(b) + click * norm(c)
    x = reverb(norm(x), decay=1.4, mix=room, seed=seed)[:n]
    return widen(norm(x), r, 0.25)

def sub_drop(dur=1.6, f0=75, f1=28, seed=0, **_):
    """Falling sub boom. Use under title reveals and the first frame after a riser."""
    tt = t_axis(dur)
    f = f1 + (f0 - f1) * np.exp(-tt * 3)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 1.8)
    x = saturate(x, 2.0) * env_adsr(len(x), 0.005, 0.05, 1, 0.2)
    return stereo(norm(x))

def tick(dur=0.08, freq=3200, seed=0, **_):
    """Precise UI/data blip. Engineer-side overlays, numbers, graphs."""
    tt = t_axis(dur)
    x = np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 70)
    x += 0.3 * np.sin(2 * np.pi * freq * 2.01 * tt) * np.exp(-tt * 120)
    return stereo(norm(x, 0.7))

def data_scan(dur=1.2, seed=0, **_):
    """Run of soft ticks rising in pitch: a graph drawing on, a stat counting up."""
    r = rng(seed); n = int(dur * SR); out = np.zeros(n)
    times = np.sort(r.uniform(0, dur * 0.95, int(10 * dur)))
    for i, t0 in enumerate(times):
        b = tick(freq=1800 + 2200 * t0 / dur, seed=i)[:, 0] * r.uniform(0.4, 1)
        s = int(t0 * SR); out[s:s + len(b)] += b[:n - s]
    return stereo(norm(out, 0.7), np.sin(np.linspace(0, 6, n)) * 0.4)

def metal_ting(dur=1.5, f=1450, seed=0, **_):
    """Halyard/shackle on a mast: inharmonic modal ring."""
    r = rng(seed); tt = t_axis(dur)
    ratios = [1, 2.76, 5.40, 8.93]; amps = [1, .5, .25, .12]
    x = sum(a * np.sin(2 * np.pi * f * k * tt + r.uniform(0, 6)) * np.exp(-tt * (3 + 4 * k))
            for k, a in zip(ratios, amps))
    x *= 1 - np.exp(-tt * 3000)
    return stereo(norm(reverb(x, 0.8, 0.15, seed)[:len(tt)], 0.6), r.uniform(-.5, .5))

def freewheel(dur=2.0, rate=14, seed=0, **_):
    """Bike freewheel clicking, slowing down. Cycling segments."""
    r = rng(seed); n = int(dur * SR); out = np.zeros(n); t0 = 0.0; k = 0
    while t0 < dur:
        cl = tick(dur=0.01, freq=5200 + r.uniform(-300, 300))[:, 0] * 0.5
        s = int(t0 * SR); out[s:s + len(cl)] += cl[:n - s]
        t0 += 1 / (rate * (1 - 0.6 * t0 / dur)); k += 1
    return stereo(norm(out, 0.5))

def rope_zip(dur=0.5, seed=0, **_):
    """Mainsheet running through a block: grainy rising friction burst."""
    r = rng(seed); n = int(dur * SR); t = np.linspace(0, 1, n)
    g = (r.random(n) < 0.02 + 0.2 * t).astype(float) * r.standard_normal(n)
    g = tv_band(g + 0.2 * white(n, r), 1500 + 2500 * t, q=1.2)
    return stereo(norm(g * np.sin(np.pi * t) ** 0.7, 0.7), 0.2)


# ---------- beds ----------
def wind(dur=10.0, strength=0.5, seed=0, **_):
    """Procedural wind bed with gusts. Fallback when no recorded wind is available."""
    r = rng(seed); n = int(dur * SR)
    lfo = signal.sosfiltfilt(signal.butter(1, 0.25, fs=SR, output='sos'), r.standard_normal(n))
    lfo = (lfo - lfo.min()) / (np.ptp(lfo) + 1e-9)
    centre = 300 + 900 * strength * lfo
    x = tv_band(pink(n, r), centre, q=0.9, nper=4096)
    x *= 0.35 + 0.65 * lfo
    return widen(norm(x, 0.8), r, 0.6)

def waves(dur=10.0, period=6.0, seed=0, **_):
    """Procedural shore/hull wash. Recorded waves beat this; use as fallback."""
    r = rng(seed); n = int(dur * SR); tt = np.arange(n) / SR
    x = signal.sosfilt(signal.butter(2, [80, 2500], 'bp', fs=SR, output='sos'), pink(n, r))
    p = period * (1 + 0.2 * np.sin(tt / 7))
    sw = (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(1 / p) / SR)) ** 2.5
    return widen(norm(x * (0.15 + 0.85 * sw), 0.8), r, 0.7)

def hull_hiss(dur=4.0, speed=0.6, seed=0, **_):
    """Water rushing past the hull at speed: bright, close, steady."""
    r = rng(seed); n = int(dur * SR)
    x = signal.sosfilt(signal.butter(2, [600 + 1500 * speed, 9000], 'bp', fs=SR, output='sos'), pink(n, r))
    x *= 0.8 + 0.2 * np.abs(signal.sosfiltfilt(signal.butter(1, 3, fs=SR, output='sos'), r.standard_normal(n))) * 3
    return widen(norm(x, 0.8), r, 0.5)

NOTES = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8,
         'A': 9, 'A#': 10, 'B': 11}

def pad(dur=8.0, root='D', minor=True, octave=3, cutoff=1400, seed=0, **_):
    """Soft detuned synth pad. Atmosphere under a sequence, not music."""
    r = rng(seed); n = int(dur * SR); tt = np.arange(n) / SR
    base = 440 * 2 ** ((NOTES[root] - 9) / 12 + (octave - 4))
    chord = [0, 3 if minor else 4, 7, 12, 14]
    x = np.zeros(n)
    for iv in chord:
        f = base * 2 ** (iv / 12)
        for dt in (-0.07, 0.0, 0.08):
            x += signal.sawtooth(2 * np.pi * f * (1 + dt / 100) * tt + r.uniform(0, 6))
    sweep = cutoff * (1 + 0.4 * np.sin(2 * np.pi * tt / max(dur, 4)))
    x = tv_band(x, sweep * 0.5, q=0.5, nper=4096)
    x *= env_adsr(n, min(2.0, dur / 3), 0.5, 0.85, min(2.5, dur / 3))
    return reverb(widen(norm(x, 0.7), r, 0.8), 2.5, 0.35, seed)[:n].astype(np.float32)

def heartbeat(dur=4.0, bpm=62, seed=0, **_):
    """Low lub-dub pulse for pre-start nerves / focus moments."""
    n = int(dur * SR); out = np.zeros(n); beat = 60 / bpm; t0 = 0
    while t0 < dur:
        for off, g in ((0, 1), (0.22, 0.6)):
            h = sub_drop(dur=0.25, f0=70, f1=40)[:, 0] * g
            s = int((t0 + off) * SR)
            if s < n: out[s:s + len(h)] += h[:n - s]
        t0 += beat
    return stereo(norm(out, 0.8))


GENERATORS = {k: v for k, v in globals().items()
              if callable(v) and k in (
                  'whoosh swish riser reverse_swell impact sub_drop tick data_scan '
                  'metal_ting freewheel rope_zip wind waves hull_hiss pad heartbeat').split()}

def write_wav(path, x, sr=SR):
    """48 kHz 24-bit PCM WAV: opens cleanly in CapCut, Premiere, Resolve, Final Cut."""
    import subprocess, tempfile, os
    x = np.clip(np.asarray(x, np.float32), -1, 1)
    fd, tmp = tempfile.mkstemp(suffix='.wav'); os.close(fd)
    wavfile.write(tmp, sr, x)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'pcm_s24le', path], check=True)
    os.remove(tmp)

def read_audio(path):
    """Decode any format ffmpeg reads to float32 stereo at SR."""
    import subprocess
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le',
                          '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('kind'); ap.add_argument('--out', default=None)
    ap.add_argument('--params', default='{}', help='JSON of generator kwargs')
    a, rest = ap.parse_known_args()
    if a.kind == 'list':
        for k, f in GENERATORS.items():
            print(f'{k:14s} {(f.__doc__ or "").strip().splitlines()[0]}')
        sys.exit()
    kw = json.loads(a.params)
    for i in range(0, len(rest), 2):  # --dur 1.2 style extras
        kw[rest[i].lstrip('-')] = json.loads(rest[i + 1]) if rest[i + 1][0] in '0123456789-[{' else rest[i + 1]
    y = GENERATORS[a.kind](**kw)
    write_wav(a.out or f'{a.kind}.wav', norm(y, 0.89))
    print(a.out or f'{a.kind}.wav', f'{len(y)/SR:.2f}s')
