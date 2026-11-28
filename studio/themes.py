"""Theme-based composition presets and intelligent sound selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class ThemePreset:
    id: str
    title: str
    mood: str
    mixing_profile: str
    tempo_range: Tuple[int, int]
    scales: List[str]
    progressions: List[str]
    instruments: Dict[str, str]
    environments: List[str]
    visual_scene: str
    palette: Tuple[Tuple[int, int, int], Tuple[int, int, int], Tuple[int, int, int]]
    safe_for_sleep: bool = False
    energy_profile: str = "balanced"


THEMES: Dict[str, ThemePreset] = {
    "rainy_cafe": ThemePreset(
        id="rainy_cafe",
        title="Rainy Café",
        mood="Cozy, Intimate, Warm, Reflective",
        mixing_profile="chill",
        tempo_range=(68, 82),
        scales=["major", "dorian"],
        progressions=["cozy_jazz", "lofi_chill"],
        instruments={
            "keys": "felt_piano",
            "pad": "warm_rhodes",
            "melody": "clean_jazz_guitar",
            "bass": "upright_double_bass",
            "rhythm": "soft_boom_bap",
        },
        environments=["gentle_window_rain", "room_ambience", "distant_thunder"],
        visual_scene="rainy_cafe",
        palette=((22, 18, 28), (58, 42, 48), (245, 185, 110)),
    ),
    "forest_morning": ThemePreset(
        id="forest_morning",
        title="Forest Morning",
        mood="Fresh, Peaceful, Organic",
        mixing_profile="nature_soundscapes",
        tempo_range=(72, 88),
        scales=["major", "lydian", "pentatonic_major"],
        progressions=["folk_morning", "ambient_drift"],
        instruments={
            "keys": "felt_piano",
            "pad": "lush_string_pad",
            "melody": "soft_flute",
            "bass": "warm_bass_guitar",
            "strings": "violins",
        },
        environments=["morning_songbirds", "leaves_rustling", "soft_forest_wind", "babbling_brook"],
        visual_scene="forest_morning",
        palette=((18, 42, 34), (62, 112, 82), (245, 225, 165)),
    ),
    "ocean_dreams": ThemePreset(
        id="ocean_dreams",
        title="Ocean Dreams",
        mood="Calm, Dreamy, Meditative",
        mixing_profile="cinematic_ambient",
        tempo_range=(58, 72),
        scales=["lydian", "major"],
        progressions=["ambient_drift", "cinematic"],
        instruments={
            "keys": "reverb_piano",
            "pad": "ambient_pad",
            "melody": "harp",
            "strings": "cellos",
        },
        environments=["ocean_waves_sandy", "coastal_wind", "seagulls"],
        visual_scene="ocean_dreams",
        palette=((12, 26, 48), (38, 86, 122), (185, 215, 240)),
    ),
    "deep_sleep": ThemePreset(
        id="deep_sleep",
        title="Deep Sleep",
        mood="Minimal, Calm, Unintrusive",
        mixing_profile="sleep",
        tempo_range=(50, 62),
        scales=["pentatonic_major", "major"],
        progressions=["sleep_minimal", "ambient_drift"],
        instruments={
            "keys": "felt_piano",
            "pad": "atmospheric_drone",
            "melody": "soft_grand_piano",
            "strings": "lush_string_pad",
        },
        environments=["gentle_window_rain", "soft_forest_wind"],
        visual_scene="deep_sleep",
        palette=((8, 12, 28), (24, 34, 68), (160, 180, 225)),
        safe_for_sleep=True,
        energy_profile="minimal",
    ),
    "mountain_stream": ThemePreset(
        id="mountain_stream",
        title="Mountain Stream",
        mood="Natural, Refreshing, Peaceful",
        mixing_profile="nature_soundscapes",
        tempo_range=(70, 84),
        scales=["major", "mixolydian"],
        progressions=["folk_morning", "ambient_drift"],
        instruments={
            "keys": "soft_grand_piano",
            "pad": "lush_string_pad",
            "melody": "soft_flute",
            "bass": "fingerpicked_acoustic",
        },
        environments=["mountain_stream", "mountain_wind", "forest_birds"],
        visual_scene="mountain_stream",
        palette=((20, 44, 52), (58, 108, 102), (225, 240, 220)),
    ),
    "desert_night": ThemePreset(
        id="desert_night",
        title="Desert Night",
        mood="Spacious, Meditative, Atmospheric",
        mixing_profile="cinematic_ambient",
        tempo_range=(60, 74),
        scales=["hijaz", "dorian"],
        progressions=["desert_modal", "nocturne"],
        instruments={
            "keys": "reverb_piano",
            "pad": "warm_analog_pad",
            "melody": "oud_plucked",
            "strings": "solo_cello",
        },
        environments=["wind_desert_dunes", "distant_earth_rumbling"],
        visual_scene="desert_night",
        palette=((16, 14, 32), (62, 42, 72), (235, 195, 140)),
    ),
    "winter_cabin": ThemePreset(
        id="winter_cabin",
        title="Winter Cabin",
        mood="Cozy, Warm, Peaceful",
        mixing_profile="chill",
        tempo_range=(64, 76),
        scales=["major", "minor"],
        progressions=["folk_morning", "cozy_jazz"],
        instruments={
            "keys": "felt_piano",
            "pad": "lush_string_pad",
            "melody": "music_box",
            "bass": "fingerpicked_acoustic",
        },
        environments=["soft_snowfall", "campfire_crackling", "wooden_cabin_ambience"],
        visual_scene="winter_cabin",
        palette=((18, 26, 44), (58, 72, 98), (255, 175, 95)),
    ),
    "night_forest": ThemePreset(
        id="night_forest",
        title="Night Forest",
        mood="Mysterious, Peaceful, Dreamlike",
        mixing_profile="sleep",
        tempo_range=(56, 68),
        scales=["minor", "dorian"],
        progressions=["nocturne", "sleep_minimal"],
        instruments={
            "keys": "reverb_piano",
            "pad": "evolving_synth_texture",
            "melody": "celeste",
            "strings": "cellos",
        },
        environments=["crickets", "owls", "soft_forest_wind", "frogs"],
        visual_scene="night_forest",
        palette=((10, 18, 28), (24, 46, 56), (175, 215, 220)),
        safe_for_sleep=True,
        energy_profile="minimal",
    ),
    "lofi_study": ThemePreset(
        id="lofi_study",
        title="Lo-Fi Study",
        mood="Relaxed, Focused, Warm",
        mixing_profile="study",
        tempo_range=(72, 86),
        scales=["dorian", "major"],
        progressions=["lofi_chill", "cozy_jazz"],
        instruments={
            "keys": "warm_rhodes",
            "pad": "warm_analog_pad",
            "melody": "clean_jazz_guitar",
            "bass": "warm_bass_guitar",
            "rhythm": "dusty_drums",
        },
        environments=["gentle_window_rain", "vinyl_crackle", "room_ambience"],
        visual_scene="lofi_study",
        palette=((22, 26, 42), (48, 62, 92), (248, 200, 120)),
    ),
    "jazz_night": ThemePreset(
        id="jazz_night",
        title="Jazz Night",
        mood="Elegant, Relaxed, Nighttime",
        mixing_profile="chill",
        tempo_range=(68, 84),
        scales=["dorian", "mixolydian"],
        progressions=["cozy_jazz", "nocturne"],
        instruments={
            "keys": "soft_grand_piano",
            "pad": "hollow_body_guitar",
            "melody": "tenor_sax",
            "bass": "upright_double_bass",
            "rhythm": "soft_boom_bap",
        },
        environments=["city_rain_ambience", "room_ambience"],
        visual_scene="jazz_night",
        palette=((14, 16, 30), (42, 34, 64), (240, 180, 90)),
    ),
}

STYLE_ALIASES: Dict[str, str] = {
    "study": "lofi_study",
    "sleep": "deep_sleep",
    "chill": "rainy_cafe",
}


def resolve_theme(name: str) -> ThemePreset:
    key = STYLE_ALIASES.get(name.lower(), name.lower())
    if key not in THEMES:
        raise ValueError(f"Unknown theme '{name}'. Available: {list(THEMES.keys())}")
    return THEMES[key]
