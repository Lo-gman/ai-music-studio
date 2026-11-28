"""AI Music Studio - Thematic Music Composition & Cinematic Scene Generation CLI."""

from __future__ import annotations

import argparse
import os
import random
import uuid
import wave
import numpy as np

from studio.environments import SR, synthesize_environment_layer
from studio.instruments import render_instrument_track, render_rhythm_track
from studio.mixing import mix_master
from studio.provenance import is_unique_track, load_catalog, record_provenance
from studio.qc import run_qc
from studio.themes import THEMES, resolve_theme
from studio.theory import generate_composition
from studio.video import render_video_mp4
from studio.visuals import render_scene_frame


def save_wav_stereo(path: str, stereo: np.ndarray, sr: int = SR) -> None:
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767.0).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main() -> None:
    p = argparse.ArgumentParser(description="AI Music Studio - Thematic Composition & Video Engine")
    p.add_argument("--style", default=None, help="Legacy mood alias (study, sleep, chill)")
    p.add_argument("--theme", default="rainy_cafe", help=f"Theme preset: {', '.join(THEMES.keys())}")
    p.add_argument("--minutes", type=float, default=5.0, help="Track duration in minutes (0.1 to 30)")
    p.add_argument("--seed", type=int, default=None, help="Random seed for composition")
    p.add_argument("--instruments", default=None, help="Comma-separated instrument overrides (e.g. felt_piano,soft_flute)")
    p.add_argument("--environments", default=None, help="Comma-separated environment overrides (e.g. gentle_window_rain,room_ambience)")
    p.add_argument("--out", default="output", help="Output directory")
    p.add_argument("--catalog", default="library/catalog.json", help="Provenance catalog JSON path")
    p.add_argument("--video", action="store_true", help="Render animated MP4 video")
    p.add_argument("--fps", type=int, default=12, help="Video FPS")
    p.add_argument("--width", type=int, default=1280, help="Video/cover width")
    p.add_argument("--height", type=int, default=720, help="Video/cover height")
    p.add_argument("--qc", action="store_true", help="Run automated quality control checks")
    args = p.parse_args()

    theme_name = args.style if args.style else args.theme
    theme = resolve_theme(theme_name)

    catalog = load_catalog(args.catalog)
    seed = args.seed if args.seed is not None else random.randint(1000, 999999)
    while args.seed is None and not is_unique_track(catalog, theme.id, seed):
        seed = random.randint(1000, 999999)

    minutes = max(0.1, min(args.minutes, 30.0))
    duration_s = minutes * 60.0
    total_samples = int(SR * duration_s)

    plan = generate_composition(
        seed=seed,
        tempo_range=theme.tempo_range,
        scale_choices=theme.scales,
        progression_choices=theme.progressions,
        total_minutes=minutes,
        energy_profile=theme.energy_profile,
    )

    instruments = dict(theme.instruments)
    if args.instruments:
        custom_inst = [x.strip() for x in args.instruments.split(",") if x.strip()]
        if len(custom_inst) >= 1:
            instruments["keys"] = custom_inst[0]
        if len(custom_inst) >= 2:
            instruments["melody"] = custom_inst[1]

    environments = list(theme.environments)
    if args.environments:
        environments = [x.strip() for x in args.environments.split(",") if x.strip()]

    # Render instrument layers
    music_stereo = np.zeros((total_samples, 2), dtype=np.float32)
    if "pad" in instruments:
        music_stereo += render_instrument_track(instruments["pad"], plan.harmony, plan.tempo_bpm, total_samples, pan=-0.15) * 0.65
    if "keys" in instruments:
        music_stereo += render_instrument_track(instruments["keys"], plan.harmony, plan.tempo_bpm, total_samples, pan=0.15) * 0.75
    if "melody" in instruments:
        music_stereo += render_instrument_track(instruments["melody"], plan.melody, plan.tempo_bpm, total_samples, pan=0.05) * 0.90
    if "bass" in instruments:
        music_stereo += render_instrument_track(instruments["bass"], plan.bass, plan.tempo_bpm, total_samples, pan=0.0) * 0.85
    if "strings" in instruments:
        music_stereo += render_instrument_track(instruments["strings"], plan.harmony, plan.tempo_bpm, total_samples, pan=-0.25) * 0.50
    if "rhythm" in instruments and plan.rhythm_hits:
        music_stereo += render_rhythm_track(plan.rhythm_hits, plan.tempo_bpm, total_samples) * 0.60

    # Render environmental layers
    env_stereo = np.zeros((total_samples, 2), dtype=np.float32)
    for env_name in environments:
        env_stereo += synthesize_environment_layer(env_name, total_samples, seed=seed, safe_for_sleep=theme.safe_for_sleep)
    if environments:
        env_stereo /= max(1.0, len(environments) ** 0.5)

    master = mix_master(music_stereo, env_stereo, profile_name=theme.mixing_profile)

    os.makedirs(args.out, exist_ok=True)
    track_id = f"{theme.id}_{seed}_{uuid.uuid4().hex[:6]}"
    audio_path = os.path.join(args.out, "music.wav")
    cover_path = os.path.join(args.out, "cover.jpg")
    metadata_path = os.path.join(args.out, "metadata.txt")
    video_path = os.path.join(args.out, f"quiet-frequencies-{theme.id}.mp4") if args.video else None

    save_wav_stereo(audio_path, master)
    cover = render_scene_frame(theme, frame_idx=0, total_frames=1, energy=0.5, width=args.width, height=args.height, seed=seed, show_title=True)
    cover.save(cover_path, quality=94)

    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(f"Title: {theme.title} | {theme.mood} ({plan.key_name}, {plan.tempo_bpm} BPM)\n")
        f.write(f"Description: Original procedural {theme.title.lower()} soundscape. Track ID: {track_id}\n")
        f.write(f"Instruments: {', '.join(instruments.values())}\n")
        f.write(f"Environments: {', '.join(environments)}\n")
        f.write("#ambient #study #sleep #chill #proceduralmusic\n")

    if video_path:
        render_video_mp4(
            theme=theme,
            audio_path=audio_path,
            video_path=video_path,
            audio_stereo=master,
            duration_s=duration_s,
            fps=args.fps,
            width=args.width,
            height=args.height,
            seed=seed,
        )

    prov = record_provenance(
        catalog_path=args.catalog,
        track_id=track_id,
        theme_id=theme.id,
        seed=seed,
        tempo_bpm=plan.tempo_bpm,
        key_name=plan.key_name,
        chord_progression=[c[0] for c in plan.chord_progression],
        instruments=instruments,
        environments=environments,
        arrangement=[s.name for s in plan.sections],
        duration_seconds=duration_s,
        audio_filename=audio_path,
        video_filename=video_path,
        artwork_filename=cover_path,
        metadata_filename=metadata_path,
        parameters={"minutes": minutes, "fps": args.fps, "resolution": f"{args.width}x{args.height}"},
    )

    if args.qc:
        qc_res = run_qc(audio_path, cover_path, metadata_path, prov, duration_s, video_path=video_path)
        if not qc_res["passed"]:
            raise RuntimeError(f"QC failed: {qc_res['errors']}")
        print(f"QC PASSED: {qc_res['checks']}")

    print(f"Created {audio_path}, {cover_path}" + (f", {video_path}" if video_path else ""))


if __name__ == "__main__":
    main()
