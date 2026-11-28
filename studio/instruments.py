"""Procedural musical instrument synthesis engine."""

from __future__ import annotations

from typing import Dict, List
import numpy as np

from .theory import NoteEvent, midi_to_hz

SR = 44100

INSTRUMENT_CATALOG: Dict[str, List[str]] = {
    "keyboards_pianos": [
        "warm_rhodes", "wurlitzer", "detuned_upright", "felt_piano",
        "soft_grand_piano", "reverb_piano", "hammond_organ", "leslie_organ",
        "celeste", "music_box", "harpsichord",
    ],
    "guitars_plucked": [
        "clean_jazz_guitar", "hollow_body_guitar", "fingerpicked_acoustic",
        "muted_guitar", "palm_muted_guitar", "reverb_electric_guitar",
        "chorus_electric_guitar", "warm_bass_guitar", "fretless_bass",
        "upright_double_bass", "harp", "ukulele", "banjo", "mandolin", "oud_plucked",
    ],
    "winds_brass": [
        "tenor_sax", "alto_sax", "muted_trumpet", "flugelhorn",
        "soft_flute", "pan_flute", "clarinet", "oboe",
        "warm_brass_pad", "brass_swell",
    ],
    "strings_orchestral": [
        "violins", "violas", "cellos", "lush_string_pad",
        "pizzicato_strings", "solo_cello", "solo_violin",
        "bowed_double_bass", "cinematic_strings",
    ],
    "percussion_textures": [
        "soft_boom_bap", "dusty_drums", "soft_kick", "crisp_snare",
        "swung_hihats", "rimshot", "shaker", "tambourine",
        "kalimba", "marimba", "vibraphone", "glockenspiel",
        "vinyl_crackle", "tape_hiss", "page_turns", "soft_footsteps", "room_ambience",
    ],
    "synthesizers": [
        "warm_analog_pad", "ambient_pad", "analog_bass", "bell_synth",
        "pluck_synth", "evolving_synth_texture", "soft_arpeggio", "atmospheric_drone",
    ],
}

ALL_INSTRUMENTS = [inst for group in INSTRUMENT_CATALOG.values() for inst in group]


def _adsr(n: int, attack: float, decay: float, sustain: float, release: float, sr: int = SR) -> np.ndarray:
    a = min(n, max(1, int(attack * sr)))
    d = min(max(0, n - a), int(decay * sr))
    r = min(max(0, n - a - d), int(release * sr))
    s = max(0, n - a - d - r)
    parts = [np.linspace(0.0, 1.0, a, dtype=np.float32)]
    if d > 0:
        parts.append(np.linspace(1.0, sustain, d, dtype=np.float32))
    if s > 0:
        parts.append(np.full(s, sustain, dtype=np.float32))
    if r > 0:
        parts.append(np.linspace(sustain, 0.0, r, dtype=np.float32))
    env = np.concatenate(parts)
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    return env[:n]


def synthesize_note(instrument: str, freq: float, duration_s: float, velocity: float = 0.7, sr: int = SR) -> np.ndarray:
    n = max(1, int(duration_s * sr))
    t = np.arange(n, dtype=np.float32) / sr

    if instrument in ("warm_rhodes", "wurlitzer", "vibraphone", "celeste"):
        mod = 2.0 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t * 4.0)
        sig = np.sin(2 * np.pi * freq * t + mod) + 0.25 * np.sin(2 * np.pi * freq * 2.0 * t)
        env = _adsr(n, 0.01, 0.4, 0.45, 0.35, sr)
    elif instrument in ("felt_piano", "soft_grand_piano", "detuned_upright", "reverb_piano"):
        detune = 1.003 if instrument == "detuned_upright" else 1.001
        sig = (
            0.65 * np.sin(2 * np.pi * freq * t)
            + 0.25 * np.sin(2 * np.pi * freq * 2.0 * detune * t)
            + 0.10 * np.sin(2 * np.pi * freq * 3.0 * t)
        )
        env = _adsr(n, 0.015, 0.6, 0.30, 0.5, sr)
    elif instrument in ("music_box", "glockenspiel", "bell_synth", "kalimba", "marimba"):
        sig = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t * 8.0)
        env = _adsr(n, 0.004, 0.35, 0.10, 0.30, sr)
    elif instrument in ("hammond_organ", "leslie_organ"):
        leslie = 1.0 + 0.08 * np.sin(2 * np.pi * 5.5 * t)
        sig = (np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t) + 0.3 * np.sin(2 * np.pi * freq * 3 * t)) * leslie
        env = _adsr(n, 0.03, 0.1, 0.85, 0.15, sr)
    elif instrument in ("clean_jazz_guitar", "hollow_body_guitar", "fingerpicked_acoustic", "harp", "ukulele", "banjo", "mandolin", "oud_plucked", "harpsichord", "pluck_synth", "muted_guitar", "palm_muted_guitar", "reverb_electric_guitar", "chorus_electric_guitar"):
        bright = 4.0 if instrument in ("banjo", "harpsichord", "mandolin") else 2.0
        sig = np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * bright)
        decay_rate = 0.25 if "muted" in instrument else 0.55
        env = _adsr(n, 0.006, decay_rate, 0.20, 0.25, sr)
    elif instrument in ("warm_bass_guitar", "fretless_bass", "upright_double_bass", "analog_bass", "bowed_double_bass"):
        sig = 0.8 * np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 2 * t)
        env = _adsr(n, 0.02, 0.25, 0.65, 0.20, sr)
    elif instrument in ("soft_flute", "pan_flute", "clarinet", "oboe", "tenor_sax", "alto_sax", "muted_trumpet", "flugelhorn"):
        vib = 0.004 * freq * np.sin(2 * np.pi * 4.8 * t)
        breath = 0.03 * np.random.normal(0, 1, n).astype(np.float32)
        sig = np.sin(2 * np.pi * (freq + vib) * t) + 0.2 * np.sin(2 * np.pi * freq * 3 * t) + breath
        env = _adsr(n, 0.08, 0.15, 0.75, 0.20, sr)
    else:
        # Strings, pads, drones, arpeggios
        det1 = np.sin(2 * np.pi * freq * 0.997 * t)
        det2 = np.sin(2 * np.pi * freq * 1.003 * t)
        sig = 0.5 * (det1 + det2) + 0.2 * np.sin(2 * np.pi * freq * 2 * t)
        env = _adsr(n, 0.25, 0.3, 0.75, 0.45, sr)

    return (sig * env * velocity * 0.35).astype(np.float32)


def synthesize_percussion(hit_type: str, velocity: float = 0.6, sr: int = SR) -> np.ndarray:
    if hit_type in ("kick", "soft_kick", "soft_boom_bap"):
        n = int(0.28 * sr)
        t = np.arange(n, dtype=np.float32) / sr
        f_env = 110.0 * np.exp(-t * 24.0) + 44.0
        sig = np.sin(2 * np.pi * f_env * t) * np.exp(-t * 10.0)
        return (sig * velocity * 0.65).astype(np.float32)
    if hit_type in ("snare", "crisp_snare", "rimshot"):
        n = int(0.18 * sr)
        t = np.arange(n, dtype=np.float32) / sr
        noise = np.random.normal(0, 1, n).astype(np.float32)
        tone = np.sin(2 * np.pi * 185.0 * t) * np.exp(-t * 25.0)
        sig = (0.65 * noise * np.exp(-t * 18.0) + 0.35 * tone)
        return (sig * velocity * 0.40).astype(np.float32)
    # hat / shaker / tambourine
    n = int(0.08 * sr)
    t = np.arange(n, dtype=np.float32) / sr
    noise = np.random.normal(0, 1, n).astype(np.float32)
    hp = noise - np.convolve(noise, np.ones(5, dtype=np.float32) / 5.0, mode="same")
    sig = hp * np.exp(-t * 45.0)
    return (sig * velocity * 0.22).astype(np.float32)


def render_instrument_track(
    instrument: str,
    events: List[NoteEvent],
    tempo_bpm: int,
    total_samples: int,
    pan: float = 0.0,
    sr: int = SR,
) -> np.ndarray:
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    sec_per_beat = 60.0 / tempo_bpm
    left_gain = np.sqrt(max(0.0, 0.5 * (1.0 - pan)))
    right_gain = np.sqrt(max(0.0, 0.5 * (1.0 + pan)))

    for ev in events:
        start_idx = int(ev.start_beat * sec_per_beat * sr)
        if start_idx >= total_samples or start_idx < 0:
            continue
        dur_s = max(0.08, ev.duration_beats * sec_per_beat)
        mono = synthesize_note(instrument, midi_to_hz(ev.midi), dur_s, ev.velocity, sr)
        end_idx = min(total_samples, start_idx + len(mono))
        seg = mono[: end_idx - start_idx]
        stereo[start_idx:end_idx, 0] += seg * left_gain
        stereo[start_idx:end_idx, 1] += seg * right_gain
    return stereo


def render_rhythm_track(
    hits: List[tuple],
    tempo_bpm: int,
    total_samples: int,
    sr: int = SR,
) -> np.ndarray:
    stereo = np.zeros((total_samples, 2), dtype=np.float32)
    sec_per_beat = 60.0 / tempo_bpm
    for beat, hit_type, vel in hits:
        start_idx = int(beat * sec_per_beat * sr)
        if start_idx >= total_samples or start_idx < 0:
            continue
        mono = synthesize_percussion(hit_type, vel, sr)
        end_idx = min(total_samples, start_idx + len(mono))
        seg = mono[: end_idx - start_idx]
        pan = -0.15 if hit_type == "hat" else 0.0
        stereo[start_idx:end_idx, 0] += seg * (0.5 - pan * 0.3)
        stereo[start_idx:end_idx, 1] += seg * (0.5 + pan * 0.3)
    return stereo
