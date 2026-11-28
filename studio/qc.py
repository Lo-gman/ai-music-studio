"""Automated Quality Control (QC) for generated audio, video, artwork, and provenance."""

from __future__ import annotations

import json
import os
import subprocess
import wave
from typing import Any, Dict, List, Optional
import numpy as np
from PIL import Image


def _ffprobe_streams(path: str) -> Dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_format",
        "-show_streams",
        "-of", "json",
        path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {}
    return json.loads(res.stdout)


def run_qc(
    audio_path: str,
    artwork_path: str,
    metadata_path: str,
    provenance_entry: Dict[str, Any],
    expected_duration_s: float,
    video_path: Optional[str] = None,
) -> Dict[str, Any]:
    checks: Dict[str, bool] = {}
    errors: List[str] = []

    # 1. Audio file & no clipping & volume levels & duration
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
        checks["audio_exists"] = False
        errors.append("Audio file missing or too small.")
    else:
        checks["audio_exists"] = True
        with wave.open(audio_path, "rb") as w:
            sr = w.getframerate()
            frames = w.getnframes()
            dur = frames / float(sr)
            raw = w.readframes(frames)
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0
        peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
        rms = float(np.sqrt(np.mean(samples ** 2))) if len(samples) else 0.0
        checks["audio_duration_ok"] = abs(dur - expected_duration_s) <= 2.0
        checks["audio_no_clipping"] = peak < 0.995
        checks["audio_volume_ok"] = 0.01 <= rms <= 0.45
        if not checks["audio_duration_ok"]:
            errors.append(f"Audio duration {dur:.2f}s != expected {expected_duration_s:.2f}s")
        if not checks["audio_no_clipping"]:
            errors.append(f"Audio clipping detected (peak={peak:.4f})")
        if not checks["audio_volume_ok"]:
            errors.append(f"Audio RMS out of range (rms={rms:.4f})")

    # 2. Artwork / visual output
    if not os.path.exists(artwork_path) or os.path.getsize(artwork_path) < 1000:
        checks["artwork_ok"] = False
        errors.append("Artwork file missing or too small.")
    else:
        with Image.open(artwork_path) as im:
            checks["artwork_ok"] = im.size[0] >= 1280 and im.size[1] >= 720
        if not checks["artwork_ok"]:
            errors.append("Artwork resolution below 1280x720.")

    # 3. Metadata
    checks["metadata_ok"] = os.path.exists(metadata_path) and os.path.getsize(metadata_path) > 20
    if not checks["metadata_ok"]:
        errors.append("Metadata file missing or empty.")

    # 4. Provenance
    required_keys = {"track_id", "theme", "seed", "tempo_bpm", "key", "instruments", "environmental_sounds"}
    checks["provenance_ok"] = required_keys.issubset(provenance_entry.keys())
    if not checks["provenance_ok"]:
        errors.append("Provenance entry missing required fields.")

    # 5. Video & A/V sync (when video_path is provided)
    if video_path:
        if not os.path.exists(video_path) or os.path.getsize(video_path) < 5000:
            checks["video_ok"] = False
            errors.append("Video file missing or too small.")
        else:
            info = _ffprobe_streams(video_path)
            streams = info.get("streams", [])
            codecs = {s.get("codec_type"): s.get("codec_name") for s in streams}
            v_dur = float(info.get("format", {}).get("duration", 0.0))
            checks["video_ok"] = codecs.get("video") == "h264" and codecs.get("audio") == "aac"
            checks["av_sync_ok"] = abs(v_dur - expected_duration_s) <= 2.5
            if not checks["video_ok"]:
                errors.append(f"Unexpected codecs: {codecs}")
            if not checks["av_sync_ok"]:
                errors.append(f"Video duration {v_dur:.2f}s out of sync with {expected_duration_s:.2f}s")

    passed = all(checks.values())
    return {"passed": passed, "checks": checks, "errors": errors}
