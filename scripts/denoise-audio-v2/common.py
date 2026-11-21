"""Shared helpers: decoding and encoding through ffmpeg pipes, band-limited baseband signals, filters.

Everything is decoded in memory; no WAV files are written. Requires ffmpeg (with libmp3lame) and NumPy.
"""
import json
import math
import os
import subprocess
import tempfile

import numpy as np


def probe_rate(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=sample_rate',
                          '-of', 'csv=p=0', path], capture_output=True, text=True, check=True).stdout
    return int(out.strip())


def decode(path, start=None, duration=None):
    """Decode to float32 samples, shape (n, 2) (mono files are duplicated). Returns (x, sample_rate)."""
    sr = probe_rate(path)
    cmd = ['ffmpeg', '-nostdin', '-v', 'error']
    if start is not None:
        cmd += ['-ss', str(start)]
    if duration is not None:
        cmd += ['-t', str(duration)]
    cmd += ['-i', path, '-vn', '-ac', '2', '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2), sr


def tags(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags', '-of', 'json', path],
                         capture_output=True, text=True, check=True).stdout
    t = json.loads(out).get('format', {}).get('tags', {})
    return {k.lower(): v for k, v in t.items()}


def _encode_once(x, sr, tag_source, dst, quality, gain_db):
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y',
           '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', '-',
           '-i', tag_source,
           '-map', '0:a', '-map', '1:v?', '-c:v', 'copy',            # cover art, if the source has any
           '-map_metadata', '1', '-id3v2_version', '3']
    if gain_db:
        cmd += ['-af', f'volume={gain_db:.3f}dB']
    cmd += ['-c:a', 'libmp3lame', '-q:a', str(quality), dst]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    data = np.ascontiguousarray(x, dtype=np.float32)
    step = 1 << 20
    for i in range(0, len(data), step):
        p.stdin.write(data[i:i + step].tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError(f'ffmpeg failed encoding {dst}')


def decoded_peak(path):
    x, _ = decode(path)
    return float(np.abs(x).max())


def encode_mp3(x, sr, tag_source, dst, quality=2):
    """Encode float samples (n, 2) to MP3 (LAME VBR), copying the tags (and cover art) of tag_source.

    Encoding can push a peak that was just below full scale over it. When the decoded result exceeds 0.999, the
    file is encoded again with just enough gain reduction (typically 0.1-0.2 dB). Returns the gain applied (dB).
    """
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix='.mp3', dir=os.path.dirname(os.path.abspath(dst)))
    os.close(fd)
    gain_db = 0.0
    try:
        _encode_once(x, sr, tag_source, tmp, quality, gain_db)
        peak = decoded_peak(tmp)
        for _ in range(3):
            if peak <= 0.999:
                break
            gain_db += 20 * math.log10(0.995 / peak)
            _encode_once(x, sr, tag_source, tmp, quality, gain_db)
            peak = decoded_peak(tmp)
        os.replace(tmp, dst)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    return gain_db


def fast_len(n, multiple=1):
    """Smallest length >= n that is a multiple of `multiple` and has no prime factor above 7.

    Whole-file FFTs must have such a length: for a length with a large prime factor NumPy falls back to a
    Bluestein FFT, which for a 25-minute file needs several GB of memory and is many times slower."""
    best = None
    p2 = 1
    while p2 < 2 * n + multiple:
        p3 = p2
        while p3 < 2 * n + multiple:
            p5 = p3
            while p5 < 2 * n + multiple:
                p7 = p5
                while p7 < 2 * n + multiple:
                    if p7 >= n and p7 % multiple == 0 and (best is None or p7 < best):
                        best = p7
                    p7 *= 7
                p5 *= 5
            p3 *= 3
        p2 *= 2
    return best


# ---------------------------------------------------------------------------------------------------------------
# Band-limited complex baseband ("heterodyne and decimate"), done exactly in the frequency domain.

class Band:
    """The analytic band [f0 - half, f0 + half] of a real signal, shifted to 0 Hz and decimated by `dec`.

    `z` has rate sr/dec; a component at frequency f in the input appears at f - fc in z, where fc is f0 rounded to
    the FFT grid. `to_real(z)` maps a (modified) baseband signal back to a real full-rate signal.
    """

    def __init__(self, X, n, sr, f0, half, dec):
        self.n, self.sr, self.dec = n, sr, dec
        self.m = n // dec
        self.rate = sr / dec
        if 2 * half >= self.rate:
            raise ValueError('band too wide for the decimation')
        self.kc = int(round(f0 * n / sr))
        self.fc = self.kc * sr / n
        k0, k1 = int(round((f0 - half) * n / sr)), int(round((f0 + half) * n / sr)) + 1
        Z = np.zeros(self.m, complex)
        Z[(np.arange(k0, k1) - self.kc) % self.m] = X[k0:k1] * 2
        self.z = np.fft.ifft(Z) * (self.m / n)

    def add_spectrum(self, z, X):
        """Add the full-rate spectrum of baseband signal z to X (an rfft-sized complex array)."""
        Z = np.fft.fft(z) * (self.n / self.m) / 2
        j = np.arange(-(self.m // 2), self.m - self.m // 2)
        k = self.kc + j
        ok = (k >= 0) & (k <= self.n // 2)
        X[k[ok]] += Z[j[ok] % self.m]

    def to_real(self, z):
        """Real full-rate signal whose analytic band is z."""
        return to_real([(self, z)], self.n)


def to_real(parts, n):
    """Sum of the real full-rate signals of several (band, baseband signal) pairs, with one inverse FFT."""
    X = np.zeros(n // 2 + 1, complex)
    for band, z in parts:
        band.add_spectrum(z, X)
    return np.fft.irfft(X, n)


def gauss_lowpass(y, rate, half_db6):
    """Zero-phase Gaussian low-pass of a (complex) signal; -6 dB at `half_db6` Hz."""
    Y = np.fft.fft(y)
    f = np.fft.fftfreq(len(y), 1 / rate)
    sigma = half_db6 / math.sqrt(2 * math.log(2))
    out = np.fft.ifft(Y * np.exp(-0.5 * (f / sigma) ** 2))
    return out if np.iscomplexobj(y) else out.real


def medfilt(v, k):
    p = k // 2
    vp = np.pad(v, p, mode='edge')
    return np.median(np.lib.stride_tricks.sliding_window_view(vp, k), axis=1)


def runs(mask):
    """[(start, stop)] of the True runs of a boolean array."""
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))
