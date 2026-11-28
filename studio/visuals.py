"""Thematic procedural scene & thumbnail generator (16:9, animated & audio-reactive)."""

from __future__ import annotations

import math
import random
from typing import Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .themes import ThemePreset


def _gradient_bg(width: int, height: int, top: Tuple[int, int, int], bottom: Tuple[int, int, int]) -> Image.Image:
    y = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None, None]
    t = np.array(top, dtype=np.float32)[None, None, :]
    b = np.array(bottom, dtype=np.float32)[None, None, :]
    arr = (t * (1.0 - y) + b * y).clip(0, 255).astype(np.uint8)
    arr = np.broadcast_to(arr, (height, width, 3)).copy()
    return Image.fromarray(arr, mode="RGB")


def render_scene_frame(
    theme: ThemePreset,
    frame_idx: int,
    total_frames: int,
    energy: float = 0.5,
    width: int = 1280,
    height: int = 720,
    seed: int = 2026,
    show_title: bool = False,
) -> Image.Image:
    top, bottom, accent = theme.palette
    im = _gradient_bg(width, height, top, bottom)
    d = ImageDraw.Draw(im, "RGBA")
    t = frame_idx / max(1, total_frames)
    rng = random.Random(seed + 17)

    # Stars / night sky for nocturnal scenes
    if theme.visual_scene in ("deep_sleep", "night_forest", "desert_night", "ocean_dreams", "winter_cabin", "jazz_night"):
        for i in range(60):
            sx = int((rng.random() * width + frame_idx * 0.15) % width)
            sy = int(rng.random() * height * 0.55)
            twinkle = int(120 + 110 * math.sin(frame_idx * 0.12 + i))
            d.ellipse((sx, sy, sx + 2, sy + 2), fill=(255, 255, 240, max(30, min(255, twinkle))))
        # Moon
        mx, my = int(width * 0.78), int(height * 0.20)
        mr = int(min(width, height) * 0.065)
        d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=(*accent, 210))
        d.ellipse((mx - mr * 2, my - mr * 2, mx + mr * 2, my + mr * 2), fill=(*accent, 25))

    # Theme-specific landscape / architectural elements
    if theme.visual_scene in ("rainy_cafe", "lofi_study", "jazz_night"):
        # Warm interior window frame & lamp glow
        d.rectangle((0, 0, int(width * 0.12), height), fill=(18, 14, 20, 220))
        d.rectangle((int(width * 0.88), 0, width, height), fill=(18, 14, 20, 220))
        d.rectangle((0, int(height * 0.78), width, height), fill=(24, 18, 22, 240))
        glow_r = int(140 + 35 * energy)
        gx, gy = int(width * 0.24), int(height * 0.62)
        d.ellipse((gx - glow_r, gy - glow_r, gx + glow_r, gy + glow_r), fill=(*accent, 55))
        # Falling rain streaks
        for i in range(90):
            rx = int((rng.random() * width + frame_idx * 2.5) % width)
            ry = int((rng.random() * height + frame_idx * 14.0) % height)
            d.line((rx, ry, rx - 3, ry + 18), fill=(190, 215, 240, 110), width=1)
    elif theme.visual_scene in ("ocean_dreams",):
        horizon = int(height * 0.58)
        d.rectangle((0, horizon, width, height), fill=(16, 48, 78, 220))
        for w_idx in range(6):
            wy = horizon + 18 + w_idx * 28
            offset = int(22 * math.sin(t * 6.28 + w_idx))
            d.arc((offset - 100, wy, width + offset + 100, wy + 26), 0, 180, fill=(*accent, 90), width=2)
    elif theme.visual_scene in ("forest_morning", "mountain_stream", "night_forest"):
        # Layered hills/mountains & trees
        d.polygon([(0, height), (0, int(height * 0.62)), (int(width * 0.35), int(height * 0.42)), (int(width * 0.7), int(height * 0.60)), (width, int(height * 0.48)), (width, height)], fill=(14, 28, 24, 200))
        for i in range(18):
            tx = int((i + 0.5) * width / 18)
            th = int(height * (0.16 + 0.08 * (i % 3)))
            ty = int(height * 0.76)
            d.polygon([(tx, ty - th), (tx - 24, ty), (tx + 24, ty)], fill=(10, 24, 18, 230))
    elif theme.visual_scene in ("desert_night",):
        d.polygon([(0, height), (0, int(height * 0.68)), (int(width * 0.4), int(height * 0.56)), (int(width * 0.8), int(height * 0.70)), (width, int(height * 0.60)), (width, height)], fill=(38, 26, 44, 225))
    elif theme.visual_scene in ("winter_cabin",):
        # Snow ground + cabin silhouette + firelight window + falling snow
        d.rectangle((0, int(height * 0.72), width, height), fill=(215, 225, 240, 220))
        cx, cy = int(width * 0.38), int(height * 0.52)
        d.rectangle((cx, cy, cx + 200, cy + 145), fill=(28, 24, 30, 245))
        d.polygon([(cx - 20, cy), (cx + 100, cy - 70), (cx + 220, cy)], fill=(20, 18, 24, 250))
        d.rectangle((cx + 70, cy + 45, cx + 130, cy + 95), fill=(*accent, int(190 + 50 * energy)))
        for i in range(70):
            sx = int((rng.random() * width + math.sin(frame_idx * 0.05 + i) * 18) % width)
            sy = int((rng.random() * height + frame_idx * 4.0) % height)
            d.ellipse((sx, sy, sx + 4, sy + 4), fill=(245, 250, 255, 175))
    else:
        # Deep sleep: calm mountains & mist
        d.polygon([(0, height), (0, int(height * 0.65)), (int(width * 0.3), int(height * 0.48)), (int(width * 0.65), int(height * 0.64)), (width, int(height * 0.50)), (width, height)], fill=(12, 18, 38, 225))

    # Subtle audio-reactive particles
    for i in range(16):
        px = int((rng.random() * width + frame_idx * 0.8) % width)
        py = int((rng.random() * height - frame_idx * 0.5) % height)
        pr = int(2 + 4 * energy)
        d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(*accent, 55))

    if show_title:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(height * 0.07))
            small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(height * 0.032))
        except OSError:
            font = small = ImageFont.load_default()
        d.rounded_rectangle((int(width * 0.06), int(height * 0.72), int(width * 0.58), int(height * 0.92)), radius=18, fill=(0, 0, 0, 110))
        d.text((int(width * 0.085), int(height * 0.745)), "QUIET FREQUENCIES", font=small, fill=(220, 230, 245, 220))
        d.text((int(width * 0.085), int(height * 0.79)), theme.title, font=font, fill=(255, 255, 255, 255))
        d.text((int(width * 0.085), int(height * 0.875)), theme.mood, font=small, fill=(*accent, 230))

    return im
