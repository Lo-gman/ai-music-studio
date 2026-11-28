"""Video production engine (16:9 MP4, H.264 + AAC, animated & audio-reactive)."""

from __future__ import annotations

import os
import subprocess
import numpy as np

from .themes import ThemePreset
from .visuals import render_scene_frame


def compute_frame_energies(audio_stereo: np.ndarray, total_frames: int) -> np.ndarray:
    if len(audio_stereo) == 0 or total_frames <= 0:
        return np.zeros(max(1, total_frames), dtype=np.float32)
    mono = np.mean(np.abs(audio_stereo), axis=1)
    chunk = max(1, len(mono) // total_frames)
    energies = np.array(
        [float(np.mean(mono[i * chunk : min(len(mono), (i + 1) * chunk)])) for i in range(total_frames)],
        dtype=np.float32,
    )
    peak = max(1e-5, float(np.max(energies)))
    return np.clip(energies / peak, 0.0, 1.0)


def render_video_mp4(
    theme: ThemePreset,
    audio_path: str,
    video_path: str,
    audio_stereo: np.ndarray,
    duration_s: float,
    fps: int = 12,
    width: int = 1280,
    height: int = 720,
    seed: int = 2026,
) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(video_path)), exist_ok=True)
    total_frames = max(1, int(round(duration_s * fps)))
    energies = compute_frame_energies(audio_stereo, total_frames)

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        video_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert proc.stdin is not None
    try:
        for idx in range(total_frames):
            frame = render_scene_frame(
                theme=theme,
                frame_idx=idx,
                total_frames=total_frames,
                energy=float(energies[idx]),
                width=width,
                height=height,
                seed=seed,
                show_title=(idx < fps * 6),
            )
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
    except Exception:
        proc.kill()
        proc.wait()
        raise
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {ret}")
