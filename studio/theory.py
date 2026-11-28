"""Music theory, scales, chord progressions, melody, bass, rhythm, and arrangement."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

SCALES: Dict[str, List[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "hijaz": [0, 1, 4, 5, 7, 8, 10],
}

CHORD_TEMPLATES: Dict[str, List[Tuple[int, str]]] = {
    "cozy_jazz": [(0, "maj7"), (9, "min7"), (2, "min7"), (7, "dom7")],
    "lofi_chill": [(2, "min7"), (7, "dom7"), (0, "maj7"), (9, "min7")],
    "ambient_drift": [(0, "sus2"), (5, "maj7"), (9, "min7"), (7, "sus4")],
    "sleep_minimal": [(0, "fifth"), (5, "fifth"), (7, "sus2"), (0, "fifth")],
    "folk_morning": [(0, "maj"), (7, "maj"), (9, "min"), (5, "maj")],
    "desert_modal": [(0, "min"), (1, "maj"), (0, "min"), (7, "sus4")],
    "cinematic": [(9, "min7"), (5, "maj7"), (0, "maj7"), (7, "maj")],
    "nocturne": [(0, "min9"), (8, "maj7"), (5, "min7"), (7, "sus4")],
}

CHORD_INTERVALS: Dict[str, List[int]] = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "min9": [0, 3, 7, 10, 14],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "fifth": [0, 7, 12],
}


def midi_to_hz(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


@dataclass
class NoteEvent:
    start_beat: float
    duration_beats: float
    midi: int
    velocity: float = 0.7


@dataclass
class ArrangementSection:
    name: str
    bars: int
    energy: float
    density: float
    active_layers: List[str] = field(default_factory=list)


@dataclass
class CompositionPlan:
    seed: int
    key_name: str
    root_midi: int
    scale_name: str
    tempo_bpm: int
    progression_name: str
    chord_progression: List[Tuple[str, List[int]]]
    sections: List[ArrangementSection]
    melody: List[NoteEvent]
    harmony: List[NoteEvent]
    bass: List[NoteEvent]
    rhythm_hits: List[Tuple[float, str, float]]


def build_chord(root_midi: int, interval_offset: int, quality: str) -> Tuple[str, List[int]]:
    chord_root = root_midi + interval_offset
    name = f"{NOTE_NAMES[chord_root % 12]}{quality}"
    notes = [chord_root + iv for iv in CHORD_INTERVALS.get(quality, [0, 4, 7])]
    return name, notes


def generate_composition(
    seed: int,
    tempo_range: Tuple[int, int],
    scale_choices: List[str],
    progression_choices: List[str],
    total_minutes: float,
    energy_profile: str = "balanced",
) -> CompositionPlan:
    rng = random.Random(seed)
    tempo_bpm = rng.randint(tempo_range[0], tempo_range[1])
    root_pc = rng.randint(0, 11)
    root_midi = 48 + root_pc  # C3..B3
    scale_name = rng.choice(scale_choices)
    prog_name = rng.choice(progression_choices)
    template = CHORD_TEMPLATES[prog_name]

    chord_progression = [build_chord(root_midi, offset, qual) for offset, qual in template]

    beats_per_bar = 4
    total_beats = max(16, int(total_minutes * tempo_bpm))
    total_bars = max(4, total_beats // beats_per_bar)

    # Build coherent arrangement sections
    sections: List[ArrangementSection] = []
    bars_left = total_bars
    section_cycle = [
        ("intro", 0.35, 0.35, ["pad", "keys", "env"]),
        ("verse_a", 0.65, 0.65, ["pad", "keys", "bass", "rhythm", "env"]),
        ("chorus_b", 0.85, 0.85, ["pad", "keys", "melody", "bass", "rhythm", "strings", "env"]),
        ("bridge", 0.55, 0.50, ["pad", "melody", "strings", "env"]),
        ("verse_c", 0.75, 0.75, ["pad", "keys", "melody", "bass", "rhythm", "env"]),
        ("outro", 0.30, 0.25, ["pad", "keys", "env"]),
    ]
    if energy_profile == "minimal":
        section_cycle = [
            ("intro", 0.25, 0.20, ["pad", "env"]),
            ("drift_a", 0.40, 0.30, ["pad", "keys", "env"]),
            ("drift_b", 0.45, 0.35, ["pad", "keys", "strings", "env"]),
            ("outro", 0.20, 0.15, ["pad", "env"]),
        ]

    idx = 0
    while bars_left > 0:
        name, energy, density, layers = section_cycle[idx % len(section_cycle)]
        sec_bars = min(bars_left, rng.choice([4, 8]))
        if bars_left <= 4:
            name, energy, density, layers = section_cycle[-1]
            sec_bars = bars_left
        sections.append(ArrangementSection(name=name, bars=sec_bars, energy=energy, density=density, active_layers=layers))
        bars_left -= sec_bars
        idx += 1

    scale_intervals = SCALES[scale_name]
    scale_notes = [root_midi + 12 + iv for iv in scale_intervals] + [root_midi + 24 + iv for iv in scale_intervals]

    melody: List[NoteEvent] = []
    harmony: List[NoteEvent] = []
    bass: List[NoteEvent] = []
    rhythm_hits: List[Tuple[float, str, float]] = []

    current_bar = 0
    for sec in sections:
        for b in range(sec.bars):
            bar_beat = (current_bar + b) * beats_per_bar
            _, chord_notes = chord_progression[(current_bar + b) % len(chord_progression)]

            # Harmony / Pad / Keys
            for n in chord_notes:
                harmony.append(NoteEvent(bar_beat, 3.8, n, velocity=0.42 * sec.energy + 0.2))

            # Bass
            if "bass" in sec.active_layers:
                bass_note = chord_notes[0] - 12
                bass.append(NoteEvent(bar_beat, 2.0, bass_note, velocity=0.65 * sec.energy + 0.15))
                if sec.density > 0.5 and rng.random() < 0.7:
                    bass.append(NoteEvent(bar_beat + 2.5, 1.4, bass_note + 7, velocity=0.5 * sec.energy + 0.15))

            # Melody
            if "melody" in sec.active_layers or (sec.density > 0.3 and rng.random() < sec.density):
                beat_pos = 0.0
                while beat_pos < beats_per_bar:
                    dur = rng.choice([0.5, 1.0, 1.5, 2.0])
                    if beat_pos + dur > beats_per_bar:
                        dur = beats_per_bar - beat_pos
                    if rng.random() < sec.density:
                        pitch = rng.choice(scale_notes)
                        vel = min(0.9, 0.45 + 0.35 * sec.energy + rng.uniform(-0.08, 0.08))
                        melody.append(NoteEvent(bar_beat + beat_pos, dur * 0.92, pitch, velocity=vel))
                    beat_pos += dur

            # Rhythm
            if "rhythm" in sec.active_layers:
                rhythm_hits.append((bar_beat + 0.0, "kick", 0.65 * sec.energy))
                rhythm_hits.append((bar_beat + 2.0, "kick", 0.55 * sec.energy))
                rhythm_hits.append((bar_beat + 1.0, "snare", 0.50 * sec.energy))
                rhythm_hits.append((bar_beat + 3.0, "snare", 0.50 * sec.energy))
                for h in range(8):
                    swing = 0.04 if h % 2 == 1 else 0.0
                    rhythm_hits.append((bar_beat + h * 0.5 + swing, "hat", 0.28 * sec.energy))

            current_bar += 1

    return CompositionPlan(
        seed=seed,
        key_name=f"{NOTE_NAMES[root_pc]} {scale_name}",
        root_midi=root_midi,
        scale_name=scale_name,
        tempo_bpm=tempo_bpm,
        progression_name=prog_name,
        chord_progression=chord_progression,
        sections=sections,
        melody=melody,
        harmony=harmony,
        bass=bass,
        rhythm_hits=rhythm_hits,
    )
