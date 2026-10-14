#!/usr/bin/env python3
"""Generate designed sound effects from a text prompt with the ElevenLabs Sound Effects API.

    export ELEVENLABS_API_KEY=...
    python elevenlabs_sfx.py "failing fluorescent tube, 50 Hz buzz, starter clicks, flickering" \
        --name tube-flicker --dur 6 --variations 3 --dest sfx-library/generated

- Writes 48 kHz WAVs (<name>-1.wav, <name>-2.wav ...) plus a licence sidecar each, so
  build_mix.py and intake_library.py pick them up like any other recording.
- --influence 0..1: higher follows the prompt more literally, lower is more varied.
- Licence: generated audio may be used commercially on a paid ElevenLabs plan; the free
  tier needs attribution and is not for commercial use. The sidecar says so: confirm
  the plan before posting.

Best for: designed one-shots that libraries lack or cannot time (a specific arc, a
stinger in a key, a garbled announcement chime). Keep the brightness gate and the
sound map timings: generate the sound, the mix still places it to the frame.
Needs network access to api.elevenlabs.io.
"""
import argparse, json, os, subprocess, sys, urllib.request

URL = 'https://api.elevenlabs.io/v1/sound-generation'

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('prompt'); ap.add_argument('--name', required=True)
    ap.add_argument('--dur', type=float, default=None, help='0.5-30 s; omit to let the model choose')
    ap.add_argument('--influence', type=float, default=0.4)
    ap.add_argument('--variations', type=int, default=2)
    ap.add_argument('--dest', default=os.path.join(os.environ.get('SFX_LIBRARY', 'sfx-library'), 'generated'))
    a = ap.parse_args()
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key: sys.exit('Set ELEVENLABS_API_KEY.')
    os.makedirs(a.dest, exist_ok=True)
    body = {'text': a.prompt, 'prompt_influence': a.influence}
    if a.dur: body['duration_seconds'] = a.dur
    for i in range(1, a.variations + 1):
        req = urllib.request.Request(URL, json.dumps(body).encode(), method='POST',
                                     headers={'xi-api-key': key, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r: mp3 = r.read()
        except Exception as e:
            print(f'FAILED variation {i}: {e}'); continue
        base = os.path.join(a.dest, f'{a.name}-{i}')
        open(base + '.mp3', 'wb').write(mp3)
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', base + '.mp3', '-ar', '48000', '-ac', '2',
                        '-c:a', 'pcm_s24le', base + '.wav'], check=True)
        os.remove(base + '.mp3')
        json.dump({'licence': 'ElevenLabs generated: commercial use on a paid plan (free tier: '
                              'attribution, non-commercial). Confirm plan before posting.',
                   'author': 'ElevenLabs Sound Effects', 'source': f'prompt: {a.prompt}'},
                  open(base + '.json', 'w'), indent=1)
        print('wrote', base + '.wav')
