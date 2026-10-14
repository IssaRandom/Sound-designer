#!/usr/bin/env python3
"""Find the cuts in a reel and grab a frame from each shot so the shots can be
looked at and matched to sounds.

    python analyse_video.py reel.mp4 --out work/ [--threshold 0.3] [--min-shot 0.25]

Writes work/analysis.json (duration, fps, shots with start/end/frame path,
camera-audio loudness per shot, a per-frame brightness curve and light events:
flashes, blackouts and flicker dips), work/frames/shot_XX.jpg, a one-frame-per-shot
contact_sheet.jpg and a dense sheet (6 frames a second) that shows motion and
flicker the shot frames miss. Then VIEW both sheets before writing the sound map.

Light events matter: the scene detector finds cuts, not a light flickering or a
white flash inside a shot, and those are often the best sync points in the reel.
"""
import argparse, json, os, re, subprocess

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def probe(path):
    p = run(['ffprobe', '-v', 'error', '-show_entries',
             'format=duration:stream=codec_type,r_frame_rate,width,height',
             '-of', 'json', path])
    d = json.loads(p.stdout)
    v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    num, den = map(int, v['r_frame_rate'].split('/'))
    has_audio = any(s['codec_type'] == 'audio' for s in d['streams'])
    return float(d['format']['duration']), num / den, v['width'], v['height'], has_audio

def cuts(path, thr):
    p = run(['ffmpeg', '-i', path, '-vf', f"select='gt(scene,{thr})',showinfo",
             '-an', '-f', 'null', '-'])
    return [float(m) for m in re.findall(r'pts_time:([\d.]+)', p.stderr)]

def shot_loudness(path, a, b):
    p = run(['ffmpeg', '-ss', f'{a}', '-t', f'{max(b - a, 0.1)}', '-i', path, '-vn',
             '-af', 'volumedetect', '-f', 'null', '-'])
    m = re.search(r'mean_volume: ([-\d.]+) dB', p.stderr)
    return float(m.group(1)) if m else None

def brightness(path):
    """Per-frame mean luma, [[t, Y], ...] on real presentation times. Drives `gate`.
    Always use pts times: screen recordings are variable frame rate, so
    frame_index / fps drifts (it put sync points 4 frames early on one reel)."""
    p = run(['ffmpeg', '-i', path, '-vf',
             'scale=160:-2,signalstats,metadata=print:key=lavfi.signalstats.YAVG', '-an', '-f', 'null', '-'])
    ts = [float(t) for t in re.findall(r'pts_time:([\d.]+)', p.stderr)]
    ys = [float(y) for y in re.findall(r'YAVG=([\d.]+)', p.stderr)]
    return [[round(t, 4), round(y, 1)] for t, y in zip(ts, ys)]

def light_events(curve, jump=25):
    """Frames where brightness jumps by more than `jump` (0-255): flash / dark / recover."""
    ev, prev = [], None
    ys = sorted(y for _, y in curve); ref = ys[len(ys) // 2] if ys else 0
    for t, y in curve:
        if prev is not None and abs(y - prev) > jump:
            kind = 'flash' if y > ref * 1.8 else 'dark' if y < prev else 'recover'
            if ev and ev[-1]['kind'] == kind and t - ev[-1]['t'] < 0.07:
                ev[-1]['to'] = y          # same event spread over consecutive frames
            else:
                ev.append({'t': t, 'kind': kind, 'from': prev, 'to': y})
        prev = y
    return ev

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('--out', default='work')
    ap.add_argument('--threshold', type=float, default=0.3,
                    help='lower (0.2) for soft cuts/dissolves, higher (0.45) for shaky water footage')
    ap.add_argument('--min-shot', type=float, default=0.25)
    a = ap.parse_args()
    os.makedirs(f'{a.out}/frames', exist_ok=True)
    dur, fps, w, h, has_audio = probe(a.video)
    cs = [c for c in cuts(a.video, a.threshold) if 0.1 < c < dur - 0.1]
    bounds = [0.0]
    for c in cs:
        if c - bounds[-1] >= a.min_shot: bounds.append(c)
    bounds.append(dur)
    shots = []
    for i, (s, e) in enumerate(zip(bounds[:-1], bounds[1:])):
        fp = f'{a.out}/frames/shot_{i:02d}.jpg'
        run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{(s + e) / 2}', '-i', a.video,
             '-frames:v', '1', '-vf', 'scale=360:-2', fp])
        shots.append({'shot': i, 'start': round(s, 3), 'end': round(e, 3),
                      'len': round(e - s, 3), 'frame': fp,
                      'camera_audio_db': shot_loudness(a.video, s, e) if has_audio else None})
    # contact sheet for a single look at the whole reel
    run(['ffmpeg', '-y', '-loglevel', 'error', '-pattern_type', 'glob', '-i',
         f'{a.out}/frames/shot_*.jpg', '-vf', 'scale=180:-2,tile=6x' +
         str(max(1, -(-len(shots) // 6))), '-frames:v', '1', f'{a.out}/contact_sheet.jpg'])
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', a.video, '-vf',
         'fps=6,scale=150:-2,tile=9x' + str(max(1, -(-int(dur * 6 + 1) // 9))), '-frames:v', '1',
         f'{a.out}/dense_sheet.jpg'])
    curve = brightness(a.video); events = light_events(curve)
    json.dump(curve, open(f'{a.out}/brightness.json', 'w'))
    res = {'video': a.video, 'duration': round(dur, 3), 'fps': round(fps, 3),
           'size': [w, h], 'has_camera_audio': has_audio, 'cuts': bounds[1:-1], 'shots': shots,
           'contact_sheet': f'{a.out}/contact_sheet.jpg', 'dense_sheet': f'{a.out}/dense_sheet.jpg',
           'brightness': f'{a.out}/brightness.json', 'light_events': events}
    json.dump(res, open(f'{a.out}/analysis.json', 'w'), indent=2)
    print(f'{dur:.2f}s @ {fps:.2f}fps, {len(shots)} shots, cuts at:',
          ', '.join(f'{c:.2f}' for c in bounds[1:-1]))
    print(f'{len(events)} light events (flash/dark/recover):',
          ', '.join(f"{e['kind']}@{e['t']:.2f}" for e in events[:40]))
    print(f'frames in {a.out}/frames, sheets {a.out}/contact_sheet.jpg and dense_sheet.jpg')
