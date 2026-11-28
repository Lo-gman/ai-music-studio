"""
AI Music Studio - Core Synthesis Engine.
Professional-grade procedural synthesis for original, monetization-ready
ambient music. No samples, no third-party audio assets - everything is
synthesized from code, so all output is original and commercially usable.

Modules:
  Oscillator  - sine, saw, square, triangle, noise
  Envelope    - ADSR amplitude shaping
  Filter      - one-pole lowpass/highpass
  Voice       - oscillator + envelope + filter (mono synth voice)
  Reverb      - comb-filter reverb network
  Delay       - stereo echo with feedback
  Chorus      - detuned voice layering
  Mixer       - stereo bus with compression

All synthesis is additive/modular. Every track is a unique arrangement
with chord progressions, melodic lines, and dynamic structure.
"""

import math
import numpy as np

SR = 44100


# ---------------------------------------------------------------------------
# Oscillators
# ---------------------------------------------------------------------------

def osc_sine(freq, n, sr=SR, phase=0.0):
    t = (np.arange(n, dtype=np.float32) + phase * sr / freq) / sr
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def osc_saw(freq, n, sr=SR, phase=0.0):
    t = (np.arange(n, dtype=np.float32) + phase * sr / freq) / sr
    return (2 * (t * freq - np.floor(t * freq + 0.5))).astype(np.float32)


def osc_square(freq, n, sr=SR, phase=0.0):
    t = (np.arange(n, dtype=np.float32) + phase * sr / freq) / sr
    return np.sign(np.sin(2 * np.pi * freq * t)).astype(np.float32)


def osc_triangle(freq, n, sr=SR, phase=0.0):
    t = (np.arange(n, dtype=np.float32) + phase * sr / freq) / sr
    x = 2 * (t * freq - np.floor(t * freq + 0.5))
    return (2 * np.abs(2 * np.abs(x) - 1) - 1).astype(np.float32)


def osc_noise(n, sr=SR):
    return np.random.normal(0, 0.5, n).astype(np.float32)


# ---------------------------------------------------------------------------
# Envelope (ADSR)
# ---------------------------------------------------------------------------

def adsr(n, attack=0.1, decay=0.1, sustain=0.7, release=0.3, sr=SR):
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    s = max(0, n - a - d - r)
    env = np.zeros(n, dtype=np.float32)
    if a > 0:
        env[:a] = np.linspace(0.0, 1.0, a)
    if d > 0:
        env[a:a + d] = 1.0 - (1.0 - sustain) * np.linspace(0.0, 1.0, d)
    if s > 0:
        env[a + d:a + d + s] = sustain
    if r > 0 and a + d + s < n:
        env[a + d + s:] = sustain * np.linspace(1.0, 0.0, min(r, n - a - d - s))
    return env


# ---------------------------------------------------------------------------
# Filters (one-pole IIR)
# ---------------------------------------------------------------------------

def lowpass(x, cutoff, sr=SR, resonance=0.0):
    """Simple one-pole lowpass. cutoff in Hz."""
    if cutoff >= sr / 2:
        return x.copy()
    c = 2.0 * math.sin(math.pi * cutoff / sr)
    y = np.zeros_like(x)
    for i in range(1, len(x)):
        y[i] = y[i - 1] + c * (x[i] - y[i - 1])
    return y.astype(np.float32)


def highpass(x, cutoff, sr=SR):
    if cutoff <= 0:
        return x.copy()
    c = 2.0 * math.sin(math.pi * cutoff / sr)
    y = np.zeros_like(x)
    for i in range(1, len(x)):
        y[i] = x[i] - x[i - 1] + c * y[i - 1]
    return y.astype(np.float32)


# ---------------------------------------------------------------------------
# Voice
# ---------------------------------------------------------------------------

class Voice:
    """A single synthesizer voice with oscillator, envelope, filter."""

    def __init__(self, osc="sine", sr=SR):
        self.osc = osc
        self.sr = sr

    def play(self, freq, dur, vel=0.5, attack=0.1, decay=0.2, sustain=0.6,
             release=0.5, cutoff=None, phase=0.0):
        n = int(dur * self.sr)
        if n <= 0:
            return np.zeros(0, dtype=np.float32)
        if self.osc == "sine":
            sig = osc_sine(freq, n, self.sr, phase)
        elif self.osc == "saw":
            sig = osc_saw(freq, n, self.sr, phase)
        elif self.osc == "square":
            sig = osc_square(freq, n, self.sr, phase)
        elif self.osc == "triangle":
            sig = osc_triangle(freq, n, self.sr, phase)
        else:
            sig = osc_sine(freq, n, self.sr, phase)
        env = adsr(n, attack, decay, sustain, release, self.sr)
        sig = sig * env * vel
        if cutoff:
            sig = lowpass(sig, cutoff, self.sr)
        return sig


# ---------------------------------------------------------------------------
# Reverb (comb filter network)
# ---------------------------------------------------------------------------

class Reverb:
    """Schroeder-style comb-filter reverb (original code, no IR files)."""

    def __init__(self, sr=SR, room_size=0.6, damping=0.5):
        self.sr = sr
        self.room_size = room_size
        self.damping = damping
        # Comb delay times in milliseconds (prime-ish for decorrelation)
        self.comb_delays_ms = [29.7, 37.1, 41.1, 43.7, 47.3, 51.1]
        self.allpass_delays_ms = [5.5, 1.7]

    def process(self, x):
        n = len(x)
        out = np.zeros(n, dtype=np.float32)
        gain = 1.0 / len(self.comb_delays_ms)
        for dms in self.comb_delays_ms:
            delay = int(dms / 1000.0 * self.sr)
            if delay <= 0 or delay >= n:
                continue
            buf = np.zeros(delay, dtype=np.float32)
            idx = 0
            for i in range(n):
                in_sample = x[i] + self.room_size * buf[idx]
                buf[idx] = in_sample * (1.0 - self.damping) + \
                    (buf[idx] * self.damping if idx > 0 else 0.0)
                out[i] += gain * buf[idx]
                idx = (idx + 1) % delay
        return out.astype(np.float32)


# ---------------------------------------------------------------------------
# Delay (stereo echo)
# ---------------------------------------------------------------------------

class Delay:
    def __init__(self, sr=SR, delay_ms=300, feedback=0.3, wet=0.25):
        self.sr = sr
        self.delay_ms = delay_ms
        self.feedback = feedback
        self.wet = wet

    def process(self, x):
        n = len(x)
        delay = int(self.delay_ms / 1000.0 * self.sr)
        if delay <= 0:
            return x.copy()
        out = x.copy()
        buf = np.zeros(delay, dtype=np.float32)
        for i in range(delay, n):
            echo = buf[(i - delay) % delay]
            out[i] = x[i] + self.wet * echo
            buf[i % delay] = x[i] + self.feedback * echo
        return out.astype(np.float32)


# ---------------------------------------------------------------------------
# Chorus (detuned layers)
# ---------------------------------------------------------------------------

def chorus(x, depth=0.01, rate=0.5, sr=SR, mix=0.3):
    n = len(x)
    t = np.arange(n, dtype=np.float32) / sr
    lfo = depth * np.sin(2 * np.pi * rate * t)
    out = np.zeros(n, dtype=np.float32)
    for i in range(n):
        frac = i + lfo[i] * sr
        j0 = int(frac)
        if j0 < 0 or j0 >= n - 1:
            out[i] = x[i]
            continue
        j1 = j0 + 1
        frac_f = frac - j0
        out[i] = (1 - frac_f) * x[j0] + frac_f * x[j1]
    return (1 - mix) * x + mix * out


# ---------------------------------------------------------------------------
# Compressor / Limiter
# ---------------------------------------------------------------------------

def compress(x, threshold=0.6, ratio=4.0, attack=0.005, release=0.1, sr=SR):
    """Simple peak compressor."""
    env = np.zeros_like(x)
    peak = 0.0
    att = attack * sr
    rel = release * sr
    for i in range(len(x)):
        ax = abs(x[i])
        if ax > peak:
            peak = peak + (ax - peak) / max(1, att)
        else:
            peak = peak + (ax - peak) / max(1, rel)
        env[i] = peak
    gain = np.ones_like(x)
    over = env > threshold
    gain[over] = threshold + (env[over] - threshold) / ratio
    gain = np.divide(gain, env, out=np.ones_like(gain), where=env > 0)
    return x * gain


def normalize(x, peak=0.7):
    mx = float(np.max(np.abs(x))) if len(x) else 0.001
    if mx > 0:
        x = x / mx * peak
    return np.clip(x, -1, 1)


# ---------------------------------------------------------------------------
# Stereo widening
# ---------------------------------------------------------------------------

def stereo(width=0.3):
    """Return (L, R) gain matrices for a mono signal to create stereo width."""
    return (1.0 - width), width


# ---------------------------------------------------------------------------
# Chord and harmony helpers
# ---------------------------------------------------------------------------

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_freq(note):
    """MIDI note number to frequency."""
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def midi_name(note):
    return NOTE_NAMES[note % 12] + str(note // 12 - 1)


def chord_from_root(root_midi, intervals):
    """Build a chord from root MIDI note + semitone intervals."""
    return [root_midi + i for i in intervals]


MAJ = [0, 4, 7]
MIN = [0, 3, 7]
MAJ7 = [0, 4, 7, 11]
MIN7 = [0, 3, 7, 10]
DOM7 = [0, 4, 7, 10]
DIM7 = [0, 3, 6, 9]
SUS2 = [0, 2, 7]
SUS4 = [0, 5, 7]
ADD9 = [0, 4, 7, 14]


# ---------------------------------------------------------------------------
# End of synth_engine module
# ---------------------------------------------------------------------------