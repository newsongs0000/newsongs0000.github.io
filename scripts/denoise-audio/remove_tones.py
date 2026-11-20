#!/usr/bin/env python3
"""Remove steady whine tones from MP3 files with cascaded notch filters (ffmpeg `bandreject`), then re-encode.

Why notches and not a denoiser: a steady tone is a single narrow line in the spectrum. Cascaded band-reject filters
remove it by 25-50 dB and leave the rest of the audio alone, while a broadband denoiser (afftdn) would dull the
music. Find the tones first with find_tones.py. Verify the result with verify_denoise.py.

The filters are IIR, so they add no delay: the output has the same length as the input, and lyric timings stay
valid. ID3 tags (and cover art, if a file has any) are copied. Encoding is LAME VBR (-q:a 2 by default).
Re-encoding can overshoot a peak that was just below full scale; when the decoded result exceeds 0.999 the file is
encoded again with a small gain reduction (typically 0.1-0.2 dB) so that nothing clips.

Usage:
  python3 scripts/denoise-audio/remove_tones.py --out-dir DIR FILE.mp3 [FILE.mp3 ...]
  python3 scripts/denoise-audio/remove_tones.py --in-place FILE.mp3 [FILE.mp3 ...]
  python3 scripts/denoise-audio/remove_tones.py --out-dir DIR --tone 6440:200:4 --tone 15613:400:4 FILE.mp3

--tone HZ[:WIDTH[:STAGES]]  centre frequency, -3 dB width in Hz (default 200) and number of cascaded notches
                            (default 4). May be repeated. Without --tone the two tones found in
                            assets/Handel/MessiahChinese are removed: 6440 Hz (200 Hz wide) and 15613 Hz (400 Hz wide).
                            A wider/more notches cover a tone that drifts more, at the price of more music being cut.
--print-filter              print the ffmpeg filter chain and exit
"""
import argparse
import math
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

DEFAULT_TONES = ['6440:200:4', '15613:400:4']


def parse_tone(spec):
    parts = spec.split(':')
    hz = float(parts[0])
    width = float(parts[1]) if len(parts) > 1 else 200.0
    stages = int(parts[2]) if len(parts) > 2 else 4
    return hz, width, stages


def filter_chain(tones):
    notches = []
    for hz, width, stages in tones:
        notches += [f'bandreject=f={hz:g}:width_type=h:w={width:g}'] * stages
    return ','.join(notches)


def decoded_peak(path):
    """Largest absolute sample of the decoded file (float, so overshoots above 1.0 are visible)."""
    import numpy as np
    proc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-vn', '-f', 'f32le', '-'],
                            stdout=subprocess.PIPE)
    peak = 0.0
    while True:
        buf = proc.stdout.read(1 << 24)
        if not buf:
            break
        peak = max(peak, float(np.abs(np.frombuffer(buf[:len(buf) // 4 * 4], dtype=np.float32)).max()))
    proc.wait()
    return peak


def encode(src, tmp, chain, quality):
    subprocess.run(
        ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', src,
         '-map', '0:a', '-map', '0:v?', '-c:v', 'copy',          # audio (+ cover art if any)
         '-map_metadata', '0', '-id3v2_version', '3',            # keep the tags
         '-af', chain, '-c:a', 'libmp3lame', '-q:a', str(quality), tmp],
        check=True)


def process(src, dst, chain, quality):
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix='.mp3', dir=os.path.dirname(os.path.abspath(dst)))
    os.close(fd)
    try:
        encode(src, tmp, chain, quality)
        peak, gain_db = decoded_peak(tmp), 0.0
        for _ in range(3):
            if peak <= 0.999:
                break
            gain_db += 20 * math.log10(0.995 / peak)               # bring the overshoot down to 0.995
            encode(src, tmp, chain + f',volume={gain_db:.3f}dB', quality)
            peak = decoded_peak(tmp)
        if gain_db:
            print(f'{src}: peak overshoot, applied {gain_db:.2f} dB (decoded peak now {peak:.3f})', flush=True)
        os.replace(tmp, dst)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    return os.path.getsize(src), os.path.getsize(dst)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='*')
    ap.add_argument('--tone', action='append', help='HZ[:WIDTH[:STAGES]], may be repeated')
    ap.add_argument('--quality', type=int, default=2, help='LAME VBR quality, 0 (best) - 9 (default 2, about 190 kbps)')
    ap.add_argument('--jobs', type=int, default=4, help='files processed in parallel')
    where = ap.add_mutually_exclusive_group()
    where.add_argument('--out-dir', help='write the results here, under the same file names')
    where.add_argument('--in-place', action='store_true', help='replace the input files')
    ap.add_argument('--print-filter', action='store_true')
    a = ap.parse_args()

    chain = filter_chain([parse_tone(t) for t in (a.tone or DEFAULT_TONES)])
    if a.print_filter:
        print(chain)
        sys.exit(0)
    if not a.files or not (a.out_dir or a.in_place):
        sys.exit(__doc__)

    def job(src):
        dst = src if a.in_place else os.path.join(a.out_dir, os.path.basename(src))
        before, after = process(src, dst, chain, a.quality)
        print(f'{src}: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB  ({dst})', flush=True)

    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for f in [ex.submit(job, s) for s in a.files]:
            f.result()
