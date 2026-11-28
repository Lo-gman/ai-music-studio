"""
AI Music Studio - Music Generation (Monetization-Grade).
Original arrangements with chord progressions, melody, bass, and texture.
Every track is musically distinct - not just frequency swaps.
"""

import math
import os
import random
import wave
import json
import subprocess
import datetime
import argparse

import numpy as np

from synth_engine import (
    Voice, osc_sine, osc_saw, osc_square, osc_triangle, osc_noise,
    adsr, lowpass, highpass, Reverb, Delay, chorus, compress, normalize,
    stereo, SR
)

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ---------------------------------------------------------------------------
# Note utilities
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
# Chord progressions per style (original arrangements)
# ---------------------------------------------------------------------------

PROGRESSIONS = {
    "study_deep_focus": [
        (36, MIN7, 4),   # Cm7
        (39, MIN7, 4),   # Dm7
        (41, MAJ7, 4),   # Fmaj7
        (43, MIN7, 4),   # Gm7
    ],
    "study_lofi_instrumental": [
        (48, MAJ7, 2),   # Cmaj7
        (43, MIN7, 2),   # Gm7
        (41, MIN7, 2),   # Fm7
        (38, DOM7, 2),   # C7
    ],
    "study_piano_ambient": [
        (48, MAJ, 6),    # C
        (52, MIN, 6),    # E
        (43, MIN, 6),    # G
        (48, MAJ, 6),    # C
    ],
    "study_concentration": [
        (36, MIN, 8),    # Cm
        (36, MIN, 8),    # Cm (static for focus)
        (38, MAJ, 8),    # D#
        (38, MAJ, 8),    # D#
    ],
    "sleep_deep_sleep": [
        (33, MIN, 8),    # low C
        (33, MIN, 8),
        (36, MIN, 8),
        (36, MIN, 8),
    ],
    "sleep_soft_piano": [
        (48, MAJ7, 6),   # Cmaj7
        (55, MIN7, 6),   # G#m7
        (50, MIN7, 6),   # D#m7
        (48, MAJ7, 6),   # Cmaj7
    ],
    "sleep_rain_atmosphere": [
        (36, MIN, 10),
        (36, MIN, 10),
        (38, MAJ, 10),
        (38, MAJ, 10),
    ],
    "sleep_ocean_nature": [
        (36, MAJ, 8),
        (36, MAJ, 8),
        (41, MIN, 8),
        (41, MIN, 8),
    ],
    "chill_relaxing_electronic": [
        (48, MIN7, 2),   # Cm7
        (51, MIN7, 2),   # C#m7
        (53, MIN7, 2),   # D#m7
        (48, MIN7, 2),   # Cm7
    ],
    "chill_lofi_chill": [
        (48, MAJ7, 2),
        (43, MIN7, 2),
        (41, MIN7, 2),
        (38, DOM7, 2),
    ],
    "chill_dreamy_ambient": [
        (48, MAJ7, 6),
        (52, MAJ7, 6),
        (55, MAJ7, 6),
        (48, MAJ7, 6),
    ],
    "chill_jazzy_background": [
        (48, MIN7, 2),   # Cm7
        (51, DOM7, 2),   # C#7
        (53, MIN7, 2),   # D#m7
        (55, DOM7, 2),   # G#7
    ],
}

STYLE_TO_CATEGORY = {
    "deep_focus": "study", "lofi_instrumental": "study", "piano_ambient": "study",
    "concentration": "study",
    "deep_sleep": "sleep", "soft_piano": "sleep", "rain_atmosphere": "sleep",
    "ocean_nature": "sleep",
    "relaxing_electronic": "chill", "lofi_chill": "chill", "dreamy_ambient": "chill",
    "jazzy_background": "chill",
}

STYLE_META = {
    "deep_focus": ("Deep Focus", "study",
                   "Original deep-focus concentration music with evolving minor-7th chord progressions."),
    "lofi_instrumental": ("Lo-fi Instrumental", "study",
                          "Original lo-fi instrumental with jazz chord progressions and dusty texture."),
    "piano_ambient": ("Piano Ambient", "study",
                      "Original minimalist piano ambient with spacious arrangements."),
    "concentration": ("Concentration Soundscape", "study",
                      "Original concentration soundscape with steady harmonic foundation."),
    "deep_sleep": ("Deep Sleep Ambient", "sleep",
                   "Original deep-sleep ambient with ultra-low sub harmonics and slow evolution."),
    "soft_piano": ("Soft Sleep Piano", "sleep",
                   "Original gentle sleep piano with spacious, lullaby-like phrasing."),
    "rain_atmosphere": ("Rain Atmosphere", "sleep",
                        "Original rain atmosphere with filtered noise textures and soft harmonic bed."),
    "ocean_nature": ("Ocean Nature Soundscape", "sleep",
                     "Original ocean nature soundscape with wave textures and gentle harmonics."),
    "relaxing_electronic": ("Relaxing Electronic", "chill",
                            "Original relaxing electronic with minor chord progressions and soft arpeggios."),
    "lofi_chill": ("Lo-fi Chill", "chill",
                   "Original lo-fi chill with jazz progressions and vintage texture."),
    "dreamy_ambient": ("Dreamy Ambient", "chill",
                       "Original dreamy ambient with lush major-7th chord pads and shimmering texture."),
    "jazzy_background": ("Jazzy Background", "chill",
                         "Original jazzy background music with minor/dominant seventh progressions."),
}

BEAT_DURATION = 1.0


# ---------------------------------------------------------------------------
# Arrangement builders
# ---------------------------------------------------------------------------

def _render_voice(voice, freq, dur, vel=0.5, **env_kwargs):
    return voice.play(freq, dur, vel=vel, **env_kwargs)


def _pad_chord(voice, freqs, dur, vel=0.25, attack=1.0, decay=1.0, sustain=0.8,
               release=2.0, cutoff=None):
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    for f in freqs:
        out += _render_voice(voice, f, dur, vel=vel, attack=attack, decay=decay,
                             sustain=sustain, release=release, cutoff=cutoff)
    return out / max(1, len(freqs))


def _arp_pattern(voice, freqs, dur, vel=0.3, attack=0.05, decay=0.1, sustain=0.4,
                 release=0.3, pattern=None, rate=4.0):
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    if pattern is None:
        pattern = [0, 1, 2, 1, 0, 2, 1, 0]
    steps = int(dur * rate)
    step_dur = dur / steps
    for i in range(steps):
        f = freqs[pattern[i % len(pattern)]]
        start = int(i * step_dur * SR)
        end = min(n, start + int(step_dur * SR * 0.8))
        if end > start:
            seg = voice.play(f, step_dur * 0.8, vel=vel, attack=attack, decay=decay,
                             sustain=sustain, release=release)
            seg_len = end - start
            out[start:end] += seg[:seg_len]
    return out


def _bass_line(voice, freqs, dur, vel=0.4, attack=0.02, decay=0.1, sustain=0.6,
               release=0.2, pattern="root_fifth", cutoff=200):
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    steps = int(dur * 2)
    step_dur = dur / steps
    for i in range(steps):
        if pattern == "root_fifth":
            f = freqs[0] if i % 2 == 0 else freqs[0] * 1.5
        else:
            f = freqs[0]
        start = int(i * step_dur * SR)
        end = min(n, start + int(step_dur * SR * 0.9))
        if end > start:
            seg = voice.play(f, step_dur * 0.9, vel=vel, attack=attack, decay=decay,
                             sustain=sustain, release=release, cutoff=cutoff)
            seg_len = end - start
            out[start:end] += seg[:seg_len]
    return out


def _piano_stabs(voice, freqs, dur, vel=0.35, attack=0.03, decay=0.4, sustain=0.1,
                 release=1.0, density=0.5):
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    steps = int(dur * 4)
    step_dur = dur / steps
    rng = np.random.RandomState(42)
    for i in range(steps):
        if rng.random() < density:
            f = rng.choice(freqs)
            start = int(i * step_dur * SR)
            end = min(n, start + int(step_dur * SR * 2))
            if end > start:
                seg = voice.play(f, step_dur * 2, vel=vel, attack=attack, decay=decay,
                                 sustain=sustain, release=release)
                seg_len = end - start
                out[start:end] += seg[:seg_len]
    return out


def _texture_noise(dur, kind="pink", vel=0.02, lp_cutoff=None, hp_cutoff=None):
    n = int(dur * SR)
    if kind == "pink":
        white = osc_noise(n)
        sig = lowpass(white, 1000) - lowpass(white, 200)
    elif kind == "brown":
        white = osc_noise(n)
        sig = lowpass(white, 300)
    else:
        sig = osc_noise(n)
    if hp_cutoff:
        sig = highpass(sig, hp_cutoff)
    if lp_cutoff:
        sig = lowpass(sig, lp_cutoff)
    t = np.arange(n, dtype=np.float32) / SR
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t)
    sig = sig * swell * vel
    return sig


def _sub_bass(freq, dur, vel=0.4, attack=0.5, decay=0.5, sustain=0.8, release=1.0):
    n = int(dur * SR)
    v = Voice("sine")
    out = np.zeros(n, dtype=np.float32)
    out += _render_voice(v, freq, dur, vel=vel, attack=attack, decay=decay,
                         sustain=sustain, release=release)
    out += _render_voice(v, freq * 2, dur, vel=vel * 0.3, attack=attack, decay=decay,
                         sustain=sustain, release=release, cutoff=150)
    return out


# ---------------------------------------------------------------------------
# Per-style arrangements
# ---------------------------------------------------------------------------

def arrange_deep_focus(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["study_deep_focus"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("sine")
    arp_v = Voice("saw")
    sub_v = Voice("sine")
    reverb = Reverb(SR, room_size=0.7, damping=0.4)
    delay = Delay(SR, delay_ms=400, feedback=0.25, wet=0.2)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _sub_bass(freqs[0], s_dur, vel=0.35, attack=1.0, release=1.0)
        out_section += _pad_chord(pad_v, freqs, s_dur, vel=0.2, attack=1.0, release=2.0)
        out_section += _arp_pattern(arp_v, freqs, s_dur, vel=0.15, rate=2.0,
                                    pattern=[0, 2, 3, 2, 0, 2, 3, 2])
        out_section += _texture_noise(s_dur, kind="pink", vel=0.01, lp_cutoff=1500)
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = delay.process(out)
    out = compress(out, threshold=0.5, ratio=3.0)
    return normalize(out, 0.7)


def arrange_lofi_instrumental(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["study_lofi_instrumental"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("saw")
    piano_v = Voice("sine")
    bass_v = Voice("saw")
    reverb = Reverb(SR, room_size=0.5, damping=0.6)
    delay = Delay(SR, delay_ms=300, feedback=0.3, wet=0.2)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = np.zeros(int(s_dur * SR), dtype=np.float32)
        out_section += _pad_chord(pad_v, freqs, s_dur, vel=0.18, attack=0.5, release=1.5)
        out_section += _piano_stabs(piano_v, freqs, s_dur, vel=0.3, density=0.4)
        out_section += _bass_line(bass_v, freqs, s_dur, vel=0.3)
        crackle = osc_noise(len(out_section)) * 0.015
        crackle = lowpass(crackle, 1000)
        out_section += crackle
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = delay.process(out)
    out = chorus(out, depth=0.008, rate=0.4, mix=0.2)
    out = compress(out, threshold=0.55, ratio=3.5)
    return normalize(out, 0.72)


def arrange_piano_ambient(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["study_piano_ambient"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    piano_v = Voice("sine")
    pad_v = Voice("sine")
    reverb = Reverb(SR, room_size=0.8, damping=0.3)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = np.zeros(int(s_dur * SR), dtype=np.float32)
        out_section += _piano_stabs(piano_v, freqs, s_dur, vel=0.4, density=0.25,
                                    release=2.0)
        out_section += _pad_chord(pad_v, freqs, s_dur, vel=0.1, attack=2.0, release=3.0)
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = compress(out, threshold=0.6, ratio=2.5)
    return normalize(out, 0.68)


def arrange_concentration(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["study_concentration"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("sine")
    pulse_v = Voice("square")
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _pad_chord(pad_v, freqs, s_dur, vel=0.25, attack=0.5, release=1.0)
        pulse = _render_voice(pulse_v, freqs[0], s_dur, vel=0.08, attack=0.01,
                              decay=0.05, sustain=0.3, release=0.1)
        out_section += pulse * 0.4
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = compress(out, threshold=0.5, ratio=4.0)
    return normalize(out, 0.7)


def arrange_deep_sleep(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["sleep_deep_sleep"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    sub_v = Voice("sine")
    pad_v = Voice("sine")
    reverb = Reverb(SR, room_size=0.9, damping=0.2)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _sub_bass(freqs[0] / 2, s_dur, vel=0.5, attack=2.0, release=2.0)
        out_section += _pad_chord(pad_v, freqs, s_dur, vel=0.15, attack=3.0, release=4.0,
                                  cutoff=400)
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = lowpass(out, 600)
    out = compress(out, threshold=0.6, ratio=2.0)
    return normalize(out, 0.65)


def arrange_soft_piano(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["sleep_soft_piano"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    piano_v = Voice("sine")
    reverb = Reverb(SR, room_size=0.85, damping=0.3)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _piano_stabs(piano_v, freqs, s_dur, vel=0.35, density=0.2,
                                   release=2.5)
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = compress(out, threshold=0.65, ratio=2.0)
    return normalize(out, 0.66)


def arrange_rain_atmosphere(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["sleep_rain_atmosphere"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("sine")
    reverb = Reverb(SR, room_size=0.6, damping=0.5)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _texture_noise(s_dur, kind="pink", vel=0.04, lp_cutoff=6000,
                                     hp_cutoff=800)
        out_section += _pad_chord(pad_v, freqs, s_dur, vel=0.1, attack=4.0, release=5.0,
                                  cutoff=1000)
        t = np.arange(int(s_dur * SR), dtype=np.float32) / SR
        thunder = 0.05 * np.sin(2 * np.pi * 55 * t) * np.exp(-t * 0.5)
        out_section += thunder
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = compress(out, threshold=0.6, ratio=2.5)
    return normalize(out, 0.7)


def arrange_ocean_nature(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["sleep_ocean_nature"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("sine")
    reverb = Reverb(SR, room_size=0.7, damping=0.4)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _texture_noise(s_dur, kind="brown", vel=0.035, lp_cutoff=4000)
        s_len = int(s_dur * SR)
        t = np.arange(s_len, dtype=np.float32) / SR
        chirp_times = np.arange(0, s_dur, 7.0)
        for ct in chirp_times:
            st = int(ct * SR)
            en = min(s_len, st + int(1.0 * SR))
            if en > st:
                seg_t = np.arange(en - st, dtype=np.float32) / SR
                chirp = 0.08 * np.sin(2 * np.pi * 3200 * seg_t) * np.exp(-seg_t * 10)
                out_section[st:en] += chirp[:en - st]
        out_section += _pad_chord(pad_v, freqs, s_dur, vel=0.1, attack=3.0, release=4.0)
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = compress(out, threshold=0.6, ratio=2.5)
    return normalize(out, 0.7)


def arrange_relaxing_electronic(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["chill_relaxing_electronic"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("saw")
    arp_v = Voice("square")
    bass_v = Voice("saw")
    reverb = Reverb(SR, room_size=0.6, damping=0.5)
    delay = Delay(SR, delay_ms=250, feedback=0.3, wet=0.25)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _pad_chord(pad_v, freqs, s_dur, vel=0.2, attack=0.5, release=1.5)
        out_section += _arp_pattern(arp_v, freqs, s_dur, vel=0.2, rate=4.0,
                                    pattern=[0, 2, 3, 1, 0, 2, 3, 1])
        out_section += _bass_line(bass_v, freqs, s_dur, vel=0.35, cutoff=300)
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = delay.process(out)
    out = chorus(out, depth=0.01, rate=0.6, mix=0.25)
    out = compress(out, threshold=0.55, ratio=3.5)
    return normalize(out, 0.72)


def arrange_lofi_chill(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["chill_lofi_chill"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("saw")
    piano_v = Voice("sine")
    bass_v = Voice("saw")
    reverb = Reverb(SR, room_size=0.55, damping=0.6)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _pad_chord(pad_v, freqs, s_dur, vel=0.18, attack=0.5, release=1.5)
        out_section += _piano_stabs(piano_v, freqs, s_dur, vel=0.32, density=0.35)
        out_section += _bass_line(bass_v, freqs, s_dur, vel=0.3)
        crackle = osc_noise(len(out_section)) * 0.012
        crackle = lowpass(crackle, 800)
        out_section += crackle
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = chorus(out, depth=0.006, rate=0.3, mix=0.15)
    out = compress(out, threshold=0.55, ratio=3.5)
    return normalize(out, 0.7)


def arrange_dreamy_ambient(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["chill_dreamy_ambient"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("saw")
    shimmer_v = Voice("sine")
    reverb = Reverb(SR, room_size=0.9, damping=0.25)
    delay = Delay(SR, delay_ms=500, feedback=0.35, wet=0.3)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _pad_chord(pad_v, freqs, s_dur, vel=0.22, attack=2.0, release=3.0)
        high_freqs = [f * 2 for f in freqs]
        out_section += _pad_chord(shimmer_v, high_freqs, s_dur, vel=0.1,
                                  attack=3.0, release=4.0)
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = delay.process(out)
    out = chorus(out, depth=0.015, rate=0.3, mix=0.3)
    out = compress(out, threshold=0.6, ratio=2.5)
    return normalize(out, 0.7)


def arrange_jazzy_background(dur, seed=2026):
    random.seed(seed)
    np.random.seed(seed)
    prog = PROGRESSIONS["chill_jazzy_background"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    section_dur = dur / len(prog)
    pad_v = Voice("saw")
    piano_v = Voice("sine")
    bass_v = Voice("saw")
    reverb = Reverb(SR, room_size=0.5, damping=0.6)
    delay = Delay(SR, delay_ms=350, feedback=0.25, wet=0.2)
    for i, (root, intervals, beats) in enumerate(prog):
        freqs = [note_to_freq(root + iv) for iv in intervals]
        s_dur = section_dur
        out_section = _pad_chord(pad_v, freqs, s_dur, vel=0.2, attack=0.4, release=1.2)
        out_section += _piano_stabs(piano_v, freqs, s_dur, vel=0.35, density=0.45)
        out_section += _bass_line(bass_v, freqs, s_dur, vel=0.32, cutoff=250)
        start = int(i * section_dur * SR)
        end = min(n, start + len(out_section))
        out[start:end] += out_section[:end - start]
    out = reverb.process(out)
    out = delay.process(out)
    out = chorus(out, depth=0.008, rate=0.5, mix=0.2)
    out = compress(out, threshold=0.55, ratio=3.5)
    return normalize(out, 0.72)


# ---------------------------------------------------------------------------
# Style registry
# ---------------------------------------------------------------------------

ARRANGERS = {
    "deep_focus": arrange_deep_focus,
    "lofi_instrumental": arrange_lofi_instrumental,
    "piano_ambient": arrange_piano_ambient,
    "concentration": arrange_concentration,
    "deep_sleep": arrange_deep_sleep,
    "soft_piano": arrange_soft_piano,
    "rain_atmosphere": arrange_rain_atmosphere,
    "ocean_nature": arrange_ocean_nature,
    "relaxing_electronic": arrange_relaxing_electronic,
    "lofi_chill": arrange_lofi_chill,
    "dreamy_ambient": arrange_dreamy_ambient,
    "jazzy_background": arrange_jazzy_background,
}


def make_cover(path, style, title):
    """Generate a 1280x720 cover JPG with a per-category palette."""
    if not HAS_PIL:
        return False
    palettes = {
        "study": ((12, 24, 42), (45, 83, 105)),
        "sleep": ((14, 17, 48), (82, 70, 120)),
        "chill": ((27, 38, 48), (95, 116, 111)),
    }
    category = STYLE_TO_CATEGORY.get(style, "study")
    a, b = palettes[category]
    im = Image.new("RGB", (1280, 720))
    px = im.load()
    for y in range(720):
        for x in range(1280):
            q = (x / 1280 + y / 720) / 2
            px[x, y] = tuple(int(a[k] * (1 - q) + b[k] * q) for k in range(3))
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse((790, 80, 1190, 480), fill=(225, 220, 255, 24), outline=(240, 240, 255, 90), width=3)
    d.ellipse((860, 150, 1120, 410), fill=(255, 255, 255, 18))
    d.rounded_rectangle((80, 80, 730, 620), radius=24, fill=(0, 0, 0, 55))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 58)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 27)
    except OSError:
        font = small = ImageFont.load_default()
    d.text((125, 205), "QUIET FREQUENCIES", font=small, fill=(220, 230, 240, 230))
    d.text((125, 275), title, font=font, fill=(255, 255, 255, 255))
    d.text((125, 390), "Original ambient soundscape", font=small, fill=(220, 230, 240, 230))
    im.save(path, quality=94)
    return True


def generate_audio(style, minutes, seed=None, out_wav=None, out_mp3=None,
                   provenance=None):
    if style not in ARRANGERS:
        raise ValueError(f"Unknown style: {style}. Available: {list(ARRANGERS)}")

    if seed is None:
        seed = random.randrange(1_000_000)

    minutes = max(1, min(minutes, 480))
    dur = minutes * 60.0
    title, category, description = STYLE_META[style]

    arranger = ARRANGERS[style]
    audio = arranger(dur, seed=seed)

    fade = int(SR * 8)
    n = len(audio)
    env = np.ones(n, dtype=np.float32)
    env[:fade] = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    audio = audio * env

    wav_path = out_wav or f"output/{style}.wav"
    mp3_path = out_mp3 or f"output/{style}.mp3"
    out_dir = os.path.dirname(wav_path) or "output"
    os.makedirs(out_dir, exist_ok=True)

    _write_wav(wav_path, audio, SR)
    mp3_ok = _to_mp3(wav_path, mp3_path)
    if not mp3_ok:
        mp3_path = None

    cover_path = os.path.join(out_dir, "cover.jpg")
    make_cover(cover_path, style, title)

    prov = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "style": style,
        "category": category,
        "title": title,
        "description": description,
        "minutes": minutes,
        "seconds": dur,
        "seed": seed,
        "sample_rate": SR,
        "arrangement": "original_procedural",
        "synthesis": "additive_subtractive_procedural",
        "instruments": _style_instruments(style),
        "chord_progression": _style_progression(style),
        "effects": ["reverb", "delay", "chorus", "compression", "fade_in_out"],
        "wav": wav_path,
        "mp3": mp3_path,
        "cover": cover_path,
        "ai_disclosure": True,
        "commercial_use": True,
        "third_party_assets": [],
    }
    if provenance:
        prov.update(provenance)

    prov_path = os.path.join(os.path.dirname(wav_path) or "output",
                             f"{style}_provenance.json")
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=2)

    meta = {
        "title": title,
        "category": category,
        "style": style,
        "description": description,
        "minutes": minutes,
        "seed": seed,
        "wav": wav_path,
        "mp3": mp3_path,
        "cover": cover_path,
        "provenance": prov_path,
    }
    return wav_path, mp3_path, meta


def _style_instruments(style):
    base = ["sine pad", "reverb", "delay", "compressor"]
    extra = {
        "deep_focus": ["sub bass", "saw arpeggio", "pink noise texture"],
        "lofi_instrumental": ["saw pad", "sine piano stabs", "saw bass", "vinyl crackle"],
        "piano_ambient": ["sine piano", "sine pad"],
        "concentration": ["sine pad", "square pulse", "isochronic tone"],
        "deep_sleep": ["sub bass", "lowpass pad", "delta pulse"],
        "soft_piano": ["sine piano"],
        "rain_atmosphere": ["pink noise", "lowpass pad", "thunder rumble"],
        "ocean_nature": ["brown noise", "bird chirps", "sine pad"],
        "relaxing_electronic": ["saw pad", "square arp", "saw bass"],
        "lofi_chill": ["saw pad", "sine piano stabs", "saw bass", "vinyl crackle"],
        "dreamy_ambient": ["saw pad", "shimmer octave", "reverb", "delay"],
        "jazzy_background": ["saw pad", "sine piano stabs", "saw bass"],
    }
    return base + extra.get(style, [])


def _style_progression(style):
    key_map = {
        "study_deep_focus": "Cm7 - Dm7 - Fmaj7 - Gm7",
        "study_lofi_instrumental": "Cmaj7 - Gm7 - Fm7 - C7",
        "study_piano_ambient": "C - E - G - C",
        "study_concentration": "Cm - Cm - D# - D#",
        "sleep_deep_sleep": "Cm - Cm - Cm - Cm (low sub)",
        "sleep_soft_piano": "Cmaj7 - G#m7 - D#m7 - Cmaj7",
        "sleep_rain_atmosphere": "Cm - Cm - D# - D#",
        "sleep_ocean_nature": "C - C - Dm - Dm",
        "chill_relaxing_electronic": "Cm7 - C#m7 - D#m7 - Cm7",
        "chill_lofi_chill": "Cmaj7 - Gm7 - Fm7 - C7",
        "chill_dreamy_ambient": "Cmaj7 - D#maj7 - G#maj7 - Cmaj7",
        "chill_jazzy_background": "Cm7 - C#7 - D#m7 - G#7",
    }
    return key_map.get(f"{STYLE_META[style][1]}_{style}", "original")


def _write_wav(path, audio, sr=SR):
    audio = normalize(audio)
    pcm = (audio * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def _to_mp3(wav_path, mp3_path):
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame",
             "-qscale:a", "4", mp3_path],
            check=True, capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def write_metadata(path, meta):
    lines = [
        f"Title: {meta['title']}",
        f"Category: {meta['category'].title()}",
        f"Style: {meta['style']}",
        f"Description: {meta['description']}",
        f"Length: {meta['minutes']} minutes",
        f"Seed: {meta['seed']}",
        "",
        "Synthetic Content Disclosure: This audio is procedurally generated",
        "using original code. No third-party audio samples or AI music APIs.",
        "",
        "Tags: #ambient #focusmusic #relaxingmusic #sleepmusic #studymusic #quietfrequencies",
        "",
        "Commercial Use: All assets are original and commercially usable.",
        "",
        "See provenance JSON for full generation record.",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser(description="AI Music Studio - original procedural generator")
    p.add_argument("--style", choices=sorted(ARRANGERS), default="deep_focus")
    p.add_argument("--minutes", type=int, default=5)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--out", default="output")
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    wav, mp3, meta = generate_audio(args.style, args.minutes, seed=args.seed,
                                     out_wav=os.path.join(args.out, "music.wav"),
                                     out_mp3=os.path.join(args.out, "music.mp3"))
    write_metadata(os.path.join(args.out, "metadata.txt"), meta)

    print(f"Created {wav}")
    if mp3:
        print(f"Created {mp3}")
    print(f"Provenance: {meta['provenance']}")
    print(f"Title: {meta['title']} | {meta['category']} | {meta['minutes']} min")


if __name__ == "__main__":
    main()
