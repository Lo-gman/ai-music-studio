"""
AI Music Studio - Audio-Reactive Visualizer.
Generates unique animated 16:9 visuals per track using the audio itself.
All rendering is numpy-vectorized for speed. No stock footage, no third-party
assets - everything is procedurally drawn and reacts to the music's spectrum.
"""

import os
import subprocess
import math
import argparse

import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

SR = 44100
FPS = 24
W, H = 1280, 720


# ---------------------------------------------------------------------------
# Audio analysis
# ---------------------------------------------------------------------------

def analyze_audio(wav_path, fps=FPS):
    """Return per-frame bass/mid/treble energy and waveform."""
    import wave
    with wave.open(wav_path, "rb") as w:
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        n_frames_total = w.getnframes()
        raw = w.readframes(n_frames_total)

    if sampwidth == 2:
        audio = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32767.0
    else:
        audio = np.frombuffer(raw, dtype=np.float32)

    if n_channels > 1:
        audio = audio.reshape(-1, n_channels).mean(axis=1)

    total_samples = len(audio)
    samples_per_frame = int(framerate / fps)
    n_frames = total_samples // samples_per_frame

    bass = np.zeros(n_frames, dtype=np.float32)
    mid = np.zeros(n_frames, dtype=np.float32)
    treble = np.zeros(n_frames, dtype=np.float32)
    waveform = np.zeros((n_frames, 64), dtype=np.float32)

    for i in range(n_frames):
        seg = audio[i * samples_per_frame:(i + 1) * samples_per_frame]
        if len(seg) == 0:
            continue
        fft = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
        freqs = np.fft.rfftfreq(len(seg), 1 / framerate)
        bass_mask = (freqs >= 40) & (freqs <= 150)
        mid_mask = (freqs > 150) & (freqs <= 1500)
        treble_mask = (freqs > 1500) & (freqs <= 8000)
        bass[i] = np.sqrt(np.mean(fft[bass_mask] ** 2)) if bass_mask.any() else 0
        mid[i] = np.sqrt(np.mean(fft[mid_mask] ** 2)) if mid_mask.any() else 0
        treble[i] = np.sqrt(np.mean(fft[treble_mask] ** 2)) if treble_mask.any() else 0
        env = np.abs(seg)
        waveform[i] = np.interp(np.linspace(0, len(seg), 64), np.arange(len(seg)), env)

    for arr in (bass, mid, treble):
        mx = arr.max()
        if mx > 0:
            arr /= mx
    return bass, mid, treble, waveform


# ---------------------------------------------------------------------------
# Fast numpy gradient
# ---------------------------------------------------------------------------

def gradient_np(w, h, c1, c2, direction="vertical"):
    c1 = np.array(c1, dtype=np.float32).reshape(1, 1, 3)
    c2 = np.array(c2, dtype=np.float32).reshape(1, 1, 3)
    if direction == "vertical":
        q = np.linspace(0, 1, h, dtype=np.float32).reshape(h, 1, 1)
    else:
        q = np.linspace(0, 1, w, dtype=np.float32).reshape(1, w, 1)
    arr = c1 * (1 - q) + c2 * q
    return np.clip(arr, 0, 255).astype(np.uint8)


def overlay_array(base, arr, alpha=1.0, offset=(0, 0)):
    """Blend a uint8 RGB array onto base PIL image."""
    ox, oy = offset
    h, w = arr.shape[:2]
    region = base.crop((ox, oy, ox + w, oy + h))
    region_arr = np.array(region, dtype=np.float32)
    blended = region_arr * (1 - alpha) + arr.astype(np.float32) * alpha
    blended = np.clip(blended, 0, 255).astype(np.uint8)
    base.paste(Image.fromarray(blended), (ox, oy))
    return base


# ---------------------------------------------------------------------------
# Font
# ---------------------------------------------------------------------------

def _font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Visual concepts per category
# ---------------------------------------------------------------------------

def visual_study(im, d, frame, bass, mid, treble, waveform, title, meta):
    """Clean geometric - focused, minimal, blue/teal."""
    cx, cy = W // 2, H // 2
    bg = gradient_np(W, H, (8, 16, 32), (20, 40, 70), "vertical")
    im.paste(Image.fromarray(bg))
    # Central rotating hexagon
    angle = (frame / 60.0) * 2 * math.pi
    radius = 100 + bass * 150
    points = []
    for k in range(6):
        a = angle + k * (math.pi / 3)
        points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    d.polygon(points, outline=(100, 180, 220), width=3)
    # Spectrum bars at bottom
    wf = np.asarray(waveform, dtype=np.float32)
    if wf.ndim == 0:
        wf = np.array([wf])
    bx = 100
    for i in range(0, len(wf), 4):
        h_bar = int(wf[i] * 200 * mid)
        if h_bar > 0:
            d.rectangle([bx, H - 100 - h_bar, bx + 6, H - 100], fill=(120, 190, 230))
        bx += 10
    d.text((W // 2, H - 60), title, font=_font(40, True),
           fill=(240, 245, 255), anchor="mt")
    return im


def visual_sleep(im, d, frame, bass, mid, treble, waveform, title, meta):
    """Slow breathing - soft gradients, drifting circles, indigo/purple."""
    cx, cy = W // 2, H // 2
    breath = 0.8 + 0.2 * math.sin(frame / 30.0)
    bg = gradient_np(W, H, (8, 6, 24), (30, 25, 60), "vertical")
    im.paste(Image.fromarray(bg))
    # Drifting circles
    for k in range(4):
        t = (frame + k * 150) / 200.0
        px = cx + 150 * math.sin(t * 0.5 + k)
        py = cy + 100 * math.cos(t * 0.3 + k)
        r = int(60 * breath + treble * 40)
        d.ellipse([px - r, py - r, px + r, py + r],
                  outline=(150, 130, 220), width=2)
    d.text((W // 2, H - 70), title, font=_font(44, True),
           fill=(220, 215, 255), anchor="mt")
    return im


def visual_chill(im, d, frame, bass, mid, treble, waveform, title, meta):
    """Warm flowing - lines and bass pulse, teal/gold."""
    cx, cy = W // 2, H // 2
    bg = gradient_np(W, H, (15, 25, 30), (40, 60, 70), "vertical")
    im.paste(Image.fromarray(bg))
    # Flowing lines based on mid energy
    for k in range(5):
        t = (frame + k * 100) / 100.0
        x1 = cx + 200 * math.sin(t + k)
        y1 = cy + 150 * math.cos(t * 0.7 + k)
        x2 = cx + 200 * math.sin(t + 1 + k)
        y2 = cy + 150 * math.cos(t * 0.7 + 1 + k)
        d.line([x1, y1, x2, y2], fill=(100, 200, 180), width=2)
    # Bass pulse circle
    r = int(80 + bass * 120)
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              outline=(220, 180, 100), width=3)
    d.text((W // 2, H - 70), title, font=_font(42, True),
           fill=(240, 235, 220), anchor="mt")
    return im


VISUALS = {
    "study": visual_study,
    "sleep": visual_sleep,
    "chill": visual_chill,
}


# ---------------------------------------------------------------------------
# Video rendering
# ---------------------------------------------------------------------------

def render_video(wav_path, cover_path, out_path, style, title, seconds=None,
                 fps=FPS):
    """Render an audio-reactive MP4 video."""
    if not HAS_PIL:
        raise RuntimeError("Pillow is required for video rendering.")

    import wave
    with wave.open(wav_path, "rb") as w:
        n_frames_audio = w.getnframes()
        framerate = w.getframerate()

    if seconds:
        n_frames = int(seconds * fps)
    else:
        n_frames = n_frames_audio // int(framerate / fps)

    bass, mid, treble, waveform = analyze_audio(wav_path, fps=fps)

    category = None
    for cat, styles in {
        "study": ["deep_focus", "lofi_instrumental", "piano_ambient", "concentration"],
        "sleep": ["deep_sleep", "soft_piano", "rain_atmosphere", "ocean_nature"],
        "chill": ["relaxing_electronic", "lofi_chill", "dreamy_ambient", "jazzy_background"],
    }.items():
        if style in styles:
            category = cat
            break
    if category is None:
        category = "study"

    visual_fn = VISUALS[category]

    tmp_dir = os.path.join(os.path.dirname(out_path) or ".", "_frames")
    os.makedirs(tmp_dir, exist_ok=True)

    base_img = None
    if cover_path and os.path.exists(cover_path):
        base_img = Image.open(cover_path).convert("RGB").resize((W, H))

    frame_paths = []
    n_bass = len(bass)
    for i in range(n_frames):
        fi = min(i, n_bass - 1)
        if base_img:
            im = base_img.copy()
            # Dim cover
            arr = np.array(im, dtype=np.float32) * 0.5
            im = Image.fromarray(arr.astype(np.uint8))
        else:
            im = Image.new("RGB", (W, H), (10, 10, 20))
        d = ImageDraw.Draw(im, "RGBA")
        im = visual_fn(im, d, fi, bass[fi], mid[fi], treble[fi], waveform[fi],
                       title, {"category": category})
        fp = os.path.join(tmp_dir, f"frame_{i:06d}.png")
        im.save(fp)
        frame_paths.append(fp)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", os.path.join(tmp_dir, "frame_%06d.png"),
        "-i", wav_path,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    for fp in frame_paths:
        try:
            os.remove(fp)
        except OSError:
            pass
    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass

    return out_path


def main():
    p = argparse.ArgumentParser(description="Render audio-reactive video")
    p.add_argument("--audio", required=True)
    p.add_argument("--cover", default=None)
    p.add_argument("--out", required=True)
    p.add_argument("--style", required=True,
                   choices=["deep_focus", "lofi_instrumental", "piano_ambient",
                            "concentration", "deep_sleep", "soft_piano",
                            "rain_atmosphere", "ocean_nature",
                            "relaxing_electronic", "lofi_chill",
                            "dreamy_ambient", "jazzy_background"])
    p.add_argument("--title", required=True)
    p.add_argument("--seconds", type=int, default=None)
    args = p.parse_args()
    render_video(args.audio, args.cover, args.out, args.style, args.title,
                 seconds=args.seconds)
    print(f"Rendered {args.out}")


if __name__ == "__main__":
    main()
