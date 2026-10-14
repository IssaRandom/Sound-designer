#!/usr/bin/env python3
"""Render a sound map (JSON) into a sound-design track that lines up with the reel.

    python build_mix.py soundmap.json --out out/ [--library library/] [--stems]

Outputs (all 48 kHz 24-bit WAV, starting at 0:00, exactly the reel's length):
    <title>_sfx.wav       full sound-design track, loudness-normalised
    stems/<layer>.wav     one file per layer (same gain as the mix, so they sum to it)
    <title>_cues.md       timecoded cue sheet (where every sound lands and why)
    <title>_credits.txt   licence/attribution for any recorded sounds used

Sound map schema: see references/soundmap_schema.md
"""
import argparse, json, os, re, subprocess, sys, glob
import numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(__file__))
import synth as S

SR = S.SR
SM_DIR = '.'
END_ANCHORED = {'riser', 'reverse_swell'}       # these finish on the hit
PEAK_ANCHORED = {'whoosh', 'swish'}             # these peak on the hit


def tc(t, fps):
    f = int(round(t * fps)); s, fr = divmod(f, int(round(fps)))
    return f'{s // 60:02d}:{s % 60:02d}:{fr:02d}'

def find_rec(name, libdirs):
    for d in libdirs:
        for p in glob.glob(os.path.join(d, '**', name + '.*'), recursive=True):
            if not p.endswith('.json'): return p
        p = os.path.join(d, name)
        if os.path.isfile(p): return p
    raise FileNotFoundError(f'recording "{name}" not found in {libdirs}. '
                            'Run fetch_cc0.py, or ask the user to upload it, or use a synth fallback.')

def load_credit(path):
    j = os.path.splitext(path)[0] + '.json'
    if os.path.exists(j): return json.load(open(j))
    side = os.path.join(os.path.dirname(path), 'licences.json')
    if os.path.exists(side):
        return json.load(open(side)).get(os.path.basename(path))
    return None

def loop_to(x, n, xf=0.5):
    """Loop a recording to n samples with equal-power crossfades."""
    if len(x) >= n: return x[:n]
    k = int(min(xf * SR, len(x) // 4)); out = x.copy()
    fi = np.sin(np.linspace(0, np.pi / 2, k))[:, None]; fo = np.cos(np.linspace(0, np.pi / 2, k))[:, None]
    while len(out) < n:
        out = np.concatenate([out[:-k], out[-k:] * fo + x[:k] * fi, x[k:]])
    return out[:n]

def pitch(x, semis):
    if not semis: return x
    r = 2 ** (semis / 12); idx = np.arange(0, len(x) - 1, r)
    return np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], 1)

def filt(x, hp=None, lp=None):
    if hp: x = signal.sosfilt(signal.butter(2, hp, 'hp', fs=SR, output='sos'), x, axis=0)
    if lp: x = signal.sosfilt(signal.butter(2, lp, 'lp', fs=SR, output='sos'), x, axis=0)
    return x

def fades(x, fi, fo):
    n = len(x); e = np.ones(n)
    a, b = int(fi * SR), int(fo * SR)
    if a: e[:min(a, n)] = np.sin(np.linspace(0, np.pi / 2, min(a, n))) ** 2
    if b: e[-min(b, n):] *= np.cos(np.linspace(0, np.pi / 2, min(b, n))) ** 2
    return x * e[:, None]

def gate_env(g, n, start, sm_dir):
    """Multiply a cue by a picture-driven envelope (e.g. brightness, so a hum
    flickers with the lights). g = {"curve": path, "ref": 53, "max": 1.6, "smooth": 0.008}."""
    path = g.get('curve', 'brightness.json')
    if not os.path.isabs(path): path = os.path.join(sm_dir, path)
    cv = np.array(json.load(open(path)), float)
    ref = g.get('ref') or float(np.median(cv[:, 1]))
    t = start + np.arange(n) / SR
    e = np.clip(np.interp(t, cv[:, 0], cv[:, 1]) / ref, g.get('floor', 0.0), g.get('max', 1.6))
    k = max(1, int(g.get('smooth', 0.008) * SR))
    return np.convolve(e, np.ones(k) / k, 'same')

def render_cue(c, libdirs, credits):
    src = c['src']; kind, name = src.split(':', 1); p = dict(c.get('params', {}))
    span = (c['end'] - c['at']) if 'end' in c else None
    if kind == 'synth':
        gen = S.GENERATORS[name]
        if span and 'dur' not in p: p['dur'] = span
        import zlib; p.setdefault('seed', zlib.crc32(c.get('id', src).encode()) % 10000)  # stable across runs
        x = gen(**p)
    else:
        path = find_rec(name, libdirs) if kind == 'rec' else name
        x = S.read_audio(path)
        off = int(c.get('offset', 0) * SR); x = x[off:]
        if span: x = loop_to(x, int(span * SR)) if c.get('loop', True) else x[:int(span * SR)]
        cr = load_credit(path); credits.append((os.path.basename(path), cr))
    x = np.asarray(x, np.float32)
    if x.ndim == 1: x = S.stereo(x)
    if c.get('reverse'): x = x[::-1]
    x = pitch(x, c.get('pitch', 0))
    proc = c.get('process')
    if proc == 'tape_stop': x = S.tape_stop(x, dur=c.get('process_dur', 0.6))
    elif proc == 'stutter': x = S.stutter(x)
    x = filt(x, c.get('hp'), c.get('lp'))
    if c.get('reverb'): x = S.reverb(x, c['reverb'].get('decay', 1.2), c['reverb'].get('mix', .25))
    if 'pan' in c and c['pan']:
        m = x.mean(1); x = S.stereo(m, c['pan'])
    x = fades(S.norm(x, 0.9), c.get('fade_in', 0), c.get('fade_out', 0))
    x *= 10 ** (c.get('gain_db', -12) / 20)
    # where does it start on the timeline?
    anchor = c.get('anchor') or ('end' if name in END_ANCHORED else
                                 'peak' if name in PEAK_ANCHORED else 'start')
    if anchor == 'end': start = c['at'] - len(x) / SR
    elif anchor == 'peak': start = c['at'] - p.get('peak', 0.55 if name == 'whoosh' else 0.6) * len(x) / SR
    else: start = c['at']
    if c.get('gate'): x = x * gate_env(c['gate'], len(x), start, SM_DIR)[:, None]
    return x, start, anchor

def loudness(path):
    p = subprocess.run(['ffmpeg', '-nostats', '-i', path, '-af', 'ebur128=peak=true',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = re.findall(r'I:\s+([-\d.]+) LUFS', p); TP = re.findall(r'Peak:\s+([-\d.]+) dBFS', p)
    return (float(I[-1]) if I else None), (float(TP[-1]) if TP else None)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('soundmap'); ap.add_argument('--out', default='out')
    ap.add_argument('--library', action='append', default=[])
    ap.add_argument('--stems', action='store_true')
    a = ap.parse_args()
    sm = json.load(open(a.soundmap))
    SM_DIR = os.path.dirname(os.path.abspath(a.soundmap))
    here = os.path.dirname(os.path.abspath(__file__))
    libdirs = a.library + [os.environ.get('SFX_LIBRARY', 'sfx-library'), '/home/claude/sfx-library', '/mnt/user-data/uploads',
                           os.path.join(here, '..', 'library')]
    dur, fps = sm['duration'], sm.get('fps', 30)
    N = int(round(dur * SR)); title = sm.get('title', 'reel').replace(' ', '_')
    layers, credits, rows, warn = {}, [], [], []
    for c in sorted(sm['cues'], key=lambda c: c['at']):
        x, start, anchor = render_cue(c, libdirs, credits)
        s = int(round(start * SR))
        if s < 0: warn.append(f"{c.get('id')}: starts {start:.2f}s, trimmed at 0:00"); x = x[-s:]; s = 0
        L = layers.setdefault(c.get('layer', 'fx'), np.zeros((N, 2), np.float32))
        e = min(N, s + len(x))
        if e > s: L[s:e] += x[:e - s]
        rows.append((c, start, start + len(x) / SR, anchor))
    # ducking (e.g. under voiceover) applies to beds only
    for d0, d1, db in sm.get('duck', []):
        g = np.ones(N); i0, i1 = int(d0 * SR), int(d1 * SR); k = int(0.25 * SR)
        g[i0:i1] = 10 ** (db / 20)
        g = np.convolve(g, np.ones(k) / k, 'same')
        for name in ('ambience', 'bed', 'pad'):
            if name in layers: layers[name] *= g[:, None]
    # short fade on the last frames so the reel loops on Instagram without a click
    ef = int(sm.get('end_fade', 0.03) * SR)
    if ef:
        g_end = np.ones(N); g_end[-ef:] = np.linspace(1, 0, ef)
        for k in layers: layers[k] *= g_end[:, None]
    mix = sum(layers.values())
    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, '_tmp.wav'); S.write_wav(tmp, np.clip(mix, -1, 1))
    I, _ = loudness(tmp)
    target, ceiling = sm.get('target_lufs', -18), sm.get('true_peak', -1.0)
    gain_db = (target - I) if I is not None and I > -70 else 0
    pk = 20 * np.log10(np.abs(mix).max() + 1e-9)
    if pk + gain_db > ceiling - 0.5:   # keep stems summing exactly: gain only, no limiter
        warn.append(f'loudness target {target} LUFS would clip; held back to peak {ceiling - 0.5} dBFS')
        gain_db = ceiling - 0.5 - pk
    g = 10 ** (gain_db / 20)
    out = os.path.join(a.out, f'{title}_sfx.wav'); S.write_wav(out, mix * g); os.remove(tmp)
    I2, TP2 = loudness(out)
    if a.stems:
        os.makedirs(os.path.join(a.out, 'stems'), exist_ok=True)
        for k, v in layers.items(): S.write_wav(os.path.join(a.out, 'stems', f'{k}.wav'), v * g)
    with open(os.path.join(a.out, f'{title}_cues.md'), 'w') as f:
        f.write(f'# {sm.get("title", "Reel")} — sound design cue sheet\n\n')
        f.write(f'Length {dur:.2f}s at {fps} fps. Drop `{title}_sfx.wav` on its own track at 00:00:00.\n'
                f'Track loudness {I2} LUFS integrated, true peak {TP2} dBTP.\n\n')
        f.write('Timecodes are mm:ss:ff.\n\n| Starts | Lands | Layer | Sound | Gain | Why |\n|---|---|---|---|---|---|\n')
        for c, st, en, anc in rows:
            land = c['at']
            f.write(f"| {tc(max(st, 0), fps)} | {tc(land, fps)} ({anc}) | {c.get('layer', 'fx')} | "
                    f"{c['src'].split(':')[0]}:{os.path.basename(c['src'].split(':', 1)[1])} | {c.get('gain_db', -12)} dB | {c.get('note', '')} |\n")
        if warn: f.write('\n**Notes**\n\n' + '\n'.join(f'- {w}' for w in warn) + '\n')
    with open(os.path.join(a.out, f'{title}_credits.txt'), 'w') as f:
        seen = set()
        f.write('Synthesised sounds (synth: cues, and files with licence "original"): made for this reel, no licence needed.\n\n')
        for fn, cr in credits:
            if fn in seen: continue
            seen.add(fn)
            f.write(f'{fn}: ' + (f"{cr.get('licence')} — {cr.get('author', '?')} — {cr.get('source', '')}"
                                 if cr else 'NO LICENCE RECORD: confirm before posting') + '\n')
    print(f'wrote {out}  ({I2} LUFS, TP {TP2} dBTP, {len(rows)} cues, layers: {", ".join(layers)})')
    for w in warn: print('note:', w)
