"""Audio mixing, spatial design, reverb, EQ, AGC, normalization, and peak limiting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import numpy as np

SR = 44100


@dataclass(frozen=True)
class MixingProfile:
    name: str
    music_gain: float
    env_gain: float
    reverb_wet: float
    delay_wet: float
    target_rms: float
    peak_limit: float
    low_shelf_damp: float


MIXING_PROFILES: Dict[str, MixingProfile] = {
    "study": MixingProfile("study", 0.85, 0.28, 0.22, 0.12, 0.14, 0.88, 0.90),
    "sleep": MixingProfile("sleep", 0.72, 0.24, 0.35, 0.15, 0.10, 0.78, 0.75),
    "chill": MixingProfile("chill", 0.88, 0.30, 0.25, 0.14, 0.15, 0.89, 0.92),
    "cinematic_ambient": MixingProfile("cinematic_ambient", 0.90, 0.35, 0.40, 0.20, 0.16, 0.90, 0.95),
    "nature_soundscapes": MixingProfile("nature_soundscapes", 0.60, 0.55, 0.30, 0.10, 0.13, 0.85, 0.88),
}


def apply_simple_reverb(stereo: np.ndarray, wet: float = 0.25, sr: int = SR) -> np.ndarray:
    if wet <= 0.0:
        return stereo
    delays = [int(0.029 * sr), int(0.037 * sr), int(0.043 * sr)]
    rev = np.zeros_like(stereo)
    for d in delays:
        if d < len(stereo):
            rev[d:] += stereo[:-d] * 0.28
    return (1.0 - wet) * stereo + wet * rev


def apply_stereo_delay(stereo: np.ndarray, wet: float = 0.12, delay_s: float = 0.375, sr: int = SR) -> np.ndarray:
    if wet <= 0.0:
        return stereo
    d = int(delay_s * sr)
    if d >= len(stereo):
        return stereo
    out = stereo.copy()
    out[d:, 0] += stereo[:-d, 1] * wet
    out[d:, 1] += stereo[:-d, 0] * wet
    return out


def apply_fades(stereo: np.ndarray, fade_s: float = 4.0, sr: int = SR) -> np.ndarray:
    n = len(stereo)
    fade = min(int(fade_s * sr), n // 4)
    if fade <= 1:
        return stereo
    env = np.ones(n, dtype=np.float32)
    env[:fade] = np.linspace(0.0, 1.0, fade, dtype=np.float32)
    env[-fade:] = np.linspace(1.0, 0.0, fade, dtype=np.float32)
    return stereo * env[:, None]


def mix_master(
    music_stereo: np.ndarray,
    env_stereo: np.ndarray,
    profile_name: str = "study",
    sr: int = SR,
) -> np.ndarray:
    profile = MIXING_PROFILES.get(profile_name, MIXING_PROFILES["study"])
    music = apply_simple_reverb(music_stereo, wet=profile.reverb_wet, sr=sr)
    music = apply_stereo_delay(music, wet=profile.delay_wet, sr=sr)

    combined = music * profile.music_gain + env_stereo * profile.env_gain
    combined = apply_fades(combined, fade_s=4.0, sr=sr)

    # Loudness normalization (RMS-based) + soft peak limiting
    rms = float(np.sqrt(np.mean(combined ** 2)))
    if rms > 1e-6:
        gain = min(4.0, profile.target_rms / rms)
        combined = combined * gain

    peak = float(np.max(np.abs(combined)))
    if peak > profile.peak_limit:
        combined = combined * (profile.peak_limit / peak)

    return np.clip(combined, -0.99, 0.99).astype(np.float32)
