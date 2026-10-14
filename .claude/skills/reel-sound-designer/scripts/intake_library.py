#!/usr/bin/env python3
"""Bring a user's downloaded sound library into the session and catalogue it.

    python intake_library.py /mnt/user-data/uploads [more paths or .zip files] \
        [--licences licences.csv|.json] [--dest $SFX_LIBRARY, default ./sfx-library]

- Unzips archives, finds every wav/aif/flac/mp3/ogg/m4a.
- Converts to 48 kHz stereo WAV under --dest with a plain slug name
  (so `rec:<slug>` finds it) and keeps the folder name as a prefix when files
  share a name.
- Carries licence records into <slug>.json sidecars: from --licences
  (csv columns: file,licence,author,source  or the json licences.json format),
  from a <name>.json sidecar next to the file (as fetch scripts write),
  or from any licence/readme text found next to the files (recorded as
  "see <file>" for a human to confirm). Anything else is flagged.
- Writes catalogue.md (duration, peak, loudness, brightness, attack, tail) and
  waveforms.png so sounds can be shortlisted by eye before auditioning by ear.
"""
import argparse, csv, glob, json, os, re, subprocess, zipfile, tempfile
import numpy as np

AUDIO = ('.wav', '.aif', '.aiff', '.flac', '.mp3', '.ogg', '.m4a', '.opus')
SR = 48000

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60] or 'sound'

def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2',
                          '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)

def describe(x):
    m = x.mean(1); n = len(m)
    if n == 0: return None
    rms = 20 * np.log10(np.sqrt(np.mean(m ** 2)) + 1e-9)
    pk = 20 * np.log10(np.abs(m).max() + 1e-9)
    seg = m[:min(n, SR * 10)]
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))); f = np.fft.rfftfreq(len(seg), 1 / SR)
    cent = float((sp * f).sum() / (sp.sum() + 1e-9))
    env = np.convolve(np.abs(m), np.ones(480) / 480, 'same')
    ipk = int(env.argmax()); atk = ipk / SR
    after = np.where(env[ipk:] < env[ipk] * 0.03)[0]
    tail = (after[0] / SR) if len(after) else (n - ipk) / SR
    kind = ('one-shot' if n / SR < 6 and atk < 0.15 else 'riser/swell' if atk > 0.6 * n / SR
            else 'bed/loop' if n / SR > 8 else 'texture')
    return dict(dur=round(n / SR, 2), peak=round(float(pk), 1), rms=round(float(rms), 1), centroid=int(cent),
                attack=round(float(atk), 2), tail=round(float(tail), 2), kind=kind)

def load_licences(p):
    if not p: return {}
    if p.endswith('.json'): return {os.path.basename(k): v for k, v in json.load(open(p)).items()}
    out = {}
    for r in csv.DictReader(open(p)):
        out[os.path.basename(r['file'])] = {k: r[k] for k in ('licence', 'author', 'source') if r.get(k)}
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='+'); ap.add_argument('--dest', default=os.environ.get('SFX_LIBRARY', 'sfx-library'))
    ap.add_argument('--licences'); a = ap.parse_args()
    os.makedirs(a.dest, exist_ok=True); lic = load_licences(a.licences)
    work = tempfile.mkdtemp(); files = []
    for p in a.paths:
        if p.lower().endswith('.zip'):
            d = os.path.join(work, slug(os.path.basename(p))); zipfile.ZipFile(p).extractall(d); p = d
        if os.path.isdir(p):
            for q in glob.glob(os.path.join(p, '**', '*'), recursive=True):
                if q.lower().endswith('.zip'):
                    d = os.path.join(work, slug(os.path.basename(q))); zipfile.ZipFile(q).extractall(d)
                    files += [r for r in glob.glob(os.path.join(d, '**', '*'), recursive=True) if r.lower().endswith(AUDIO)]
                elif q.lower().endswith(AUDIO): files.append(q)
        elif p.lower().endswith(AUDIO): files.append(p)
    rows, used, waves = [], set(), []
    for f in sorted(set(files)):
        if '__MACOSX' in f: continue
        base = slug(os.path.splitext(os.path.basename(f))[0])
        name = base if base not in used else slug(os.path.basename(os.path.dirname(f))) + '-' + base
        used.add(name)
        x = decode(f); info = describe(x)
        if not info: print('skip (no audio):', f); continue
        out = os.path.join(a.dest, name + '.wav')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-ar', str(SR), '-ac', '2',
                        '-c:a', 'pcm_s24le', out], check=True)
        cr = lic.get(os.path.basename(f))
        side = os.path.splitext(f)[0] + '.json'      # sidecar from fetch scripts or the user
        if not cr and os.path.isfile(side):
            try: cr = json.load(open(side))
            except ValueError: cr = None
        if not cr:
            near = [g for g in glob.glob(os.path.join(os.path.dirname(f), '*'))
                    if re.search(r'licen|readme|credit|terms', os.path.basename(g), re.I)]
            if near: cr = {'licence': f'see {os.path.basename(near[0])} (confirm)', 'author': '?',
                           'source': os.path.relpath(near[0], work) if near[0].startswith(work) else near[0]}
        if cr: json.dump(cr, open(os.path.join(a.dest, name + '.json'), 'w'))
        rows.append((name, info, cr, f)); waves.append((name, x.mean(1)))
    with open(os.path.join(a.dest, 'catalogue.md'), 'w') as fh:
        fh.write('| rec name | kind | dur s | peak dB | rms dB | brightness Hz | attack s | tail s | licence |\n|---|---|---|---|---|---|---|---|---|\n')
        for n, i, cr, f in rows:
            fh.write(f"| {n} | {i['kind']} | {i['dur']} | {i['peak']} | {i['rms']} | {i['centroid']} | {i['attack']} | {i['tail']} | "
                     f"{(cr or {}).get('licence', 'NONE: ask user')} |\n")
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        k = len(waves); fig, ax = plt.subplots(k, 1, figsize=(9, max(1.0, 0.55 * k)), squeeze=False)
        for (n, w), axx in zip(waves, ax[:, 0]):
            step = max(1, len(w) // 4000); axx.plot(np.arange(0, len(w), step) / SR, w[::step], lw=.4)
            axx.set_yticks([]); axx.text(0.002, 0.5, n, transform=axx.transAxes, fontsize=7, va='center')
            axx.set_xlim(0, max(len(w) / SR, .1)); axx.tick_params(labelsize=6)
        fig.tight_layout(); fig.savefig(os.path.join(a.dest, 'waveforms.png'), dpi=110)
    except Exception as e:
        print('waveforms skipped:', e)
    print(f'{len(rows)} sounds into {a.dest}; catalogue.md and waveforms.png written')
    for n, i, cr, f in rows:
        print(f"  {n:40s} {i['kind']:11s} {i['dur']:6.2f}s  {(cr or {}).get('licence', 'NO LICENCE')}")
