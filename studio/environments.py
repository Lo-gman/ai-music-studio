"""Modular procedural environmental soundscape engine."""

from __future__ import annotations

from typing import Dict, List
import numpy as np

SR = 44100

ENVIRONMENT_CATALOG: Dict[str, List[str]] = {
    "water_weather": [
        "gentle_window_rain", "rain_on_umbrellas", "rain_on_roofs", "heavy_downpour",
        "tropical_storms", "distant_thunder", "ocean_waves_sandy", "ocean_waves_rocky",
        "calm_lake_lapping", "babbling_brook", "mountain_stream", "waterfall_ambience",
        "misty_cascades",
    ],
    "wind": [
        "wind_tall_grass", "wind_reeds", "wind_desert_dunes", "soft_forest_wind",
        "wind_pine_needles", "wind_tree_branches", "howling_wind", "whistling_wind",
        "mountain_wind", "coastal_wind",
    ],
    "forests_landscapes": [
        "leaves_rustling", "pine_forest_ambience", "dry_leaves", "forest_floor_textures",
        "footsteps_on_leaves", "cracking_twigs", "campfire_crackling", "popping_embers",
        "cave_dripping_water", "subterranean_echoes",
    ],
    "wildlife_birds": [
        "morning_songbirds", "sparrows", "forest_birds", "owls", "crickets",
        "cicadas", "frogs", "loons", "seagulls", "whales", "distant_wolves",
    ],
    "earth_atmospheric": [
        "distant_earth_rumbling", "tectonic_rumbles", "ice_cracking", "glacier_ambience",
        "frozen_lake_sounds", "soft_snowfall", "quiet_winter_forest", "hail_tapping",
    ],
    "indoor_textures": [
        "room_ambience", "wooden_cabin_ambience", "vinyl_crackle", "city_rain_ambience",
    ],
}

ALL_ENVIRONMENTS = [env for group in ENVIRONMENT_CATALOG.values() for env in group]


def _smooth_noise(n: int, window: int, rng: np.random.Generator) -> np.ndarray:
    noise = rng.normal(0.0, 1.0, n).astype(np.float32)
    w = max(2, window)
    cs = np.cumsum(np.pad(noise, (w, 0)))
    smoothed = (cs[w:] - cs[:-w]) / float(w)
    return smoothed[:n].astype(np.float32)


def synthesize_environment_layer(
    env_name: str,
    total_samples: int,
    seed: int = 2026,
    safe_for_sleep: bool = False,
    sr: int = SR,
) -> np.ndarray:
    rng = np.random.default_rng(seed + abs(hash(env_name)) % 10000)
    t = np.arange(total_samples, dtype=np.float32) / sr
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    if "rain" in env_name or "downpour" in env_name or "storm" in env_name or "snowfall" in env_name:
        win = 14 if "window" in env_name or "snowfall" in env_name else 6
        left = _smooth_noise(total_samples, win, rng) * 0.14
        right = _smooth_noise(total_samples, win, rng) * 0.14
        if "thunder" in env_name and not safe_for_sleep:
            rumble = _smooth_noise(total_samples, 400, rng) * (0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.04 * t)))
            left += rumble
            right += rumble
    elif "ocean" in env_name or "waves" in env_name or "lake" in env_name:
        swell = 0.5 + 0.45 * np.sin(2 * np.pi * 0.09 * t)
        left = _smooth_noise(total_samples, 30, rng) * swell * 0.18
        right = _smooth_noise(total_samples, 32, rng) * np.roll(swell, sr // 2) * 0.18
    elif "stream" in env_name or "brook" in env_name or "waterfall" in env_name or "cascade" in env_name:
        left = _smooth_noise(total_samples, 10, rng) * 0.15
        right = _smooth_noise(total_samples, 12, rng) * 0.15
    elif "wind" in env_name or "forest" in env_name or "leaves" in env_name:
        mod = 0.4 + 0.35 * np.sin(2 * np.pi * 0.06 * t + 0.5)
        left = _smooth_noise(total_samples, 45, rng) * mod * 0.13
        right = _smooth_noise(total_samples, 48, rng) * np.roll(mod, sr) * 0.13
    elif "campfire" in env_name or "ember" in env_name or "vinyl" in env_name:
        base = _smooth_noise(total_samples, 80, rng) * 0.06
        pops = (rng.random(total_samples) < 0.0008).astype(np.float32) * rng.uniform(0.1, 0.35, total_samples).astype(np.float32)
        left = base + pops
        right = base + np.roll(pops, 200)
    elif env_name in ("morning_songbirds", "sparrows", "forest_birds", "owls", "crickets", "cicadas", "frogs", "loons", "seagulls"):
        # Sparse, spatialized wildlife calls
        num_calls = max(2, int(total_samples / (sr * 6)))
        for _ in range(num_calls):
            pos = int(rng.integers(sr, max(sr + 1, total_samples - sr)))
            dur = int(0.35 * sr)
            tt = np.arange(dur, dtype=np.float32) / sr
            base_f = 2400.0 if "bird" in env_name or "sparrow" in env_name else (420.0 if "owl" in env_name else 3800.0)
            chirp = np.sin(2 * np.pi * (base_f + 300.0 * np.sin(2 * np.pi * 12.0 * tt)) * tt) * np.exp(-tt * 6.0) * 0.06
            pan = rng.uniform(-0.7, 0.7)
            end = min(total_samples, pos + dur)
            seg = chirp[: end - pos]
            left[pos:end] += seg * (0.5 - pan * 0.4)
            right[pos:end] += seg * (0.5 + pan * 0.4)
    else:
        # Subtle room / earth / atmospheric texture
        left = _smooth_noise(total_samples, 120, rng) * 0.06
        right = _smooth_noise(total_samples, 120, rng) * 0.06

    return np.stack([left, right], axis=1).astype(np.float32)
