"""Unit and integration tests for AI Music Studio."""

import os
import tempfile
import unittest
import numpy as np

from studio.environments import ALL_ENVIRONMENTS, synthesize_environment_layer
from studio.instruments import ALL_INSTRUMENTS, synthesize_note
from studio.mixing import mix_master
from studio.provenance import record_provenance, search_catalog
from studio.qc import run_qc
from studio.themes import THEMES, resolve_theme
from studio.theory import generate_composition
from studio.visuals import render_scene_frame


class TestAIMusicStudio(unittest.TestCase):
    def test_all_themes_and_aliases(self):
        self.assertEqual(len(THEMES), 10)
        self.assertEqual(resolve_theme("study").id, "lofi_study")
        self.assertEqual(resolve_theme("sleep").id, "deep_sleep")
        self.assertEqual(resolve_theme("chill").id, "rainy_cafe")

    def test_composition_plan_uniqueness(self):
        p1 = generate_composition(101, (70, 80), ["major"], ["cozy_jazz"], 0.25)
        p2 = generate_composition(202, (70, 80), ["major"], ["cozy_jazz"], 0.25)
        self.assertGreater(len(p1.harmony), 0)
        self.assertGreater(len(p1.sections), 0)
        self.assertNotEqual((p1.key_name, p1.tempo_bpm, len(p1.melody)), (p2.key_name, p2.tempo_bpm, len(p2.melody)))

    def test_instruments_and_environments_catalogs(self):
        self.assertGreaterEqual(len(ALL_INSTRUMENTS), 60)
        self.assertGreaterEqual(len(ALL_ENVIRONMENTS), 50)
        note = synthesize_note("felt_piano", 440.0, 0.2, 0.7)
        self.assertGreater(len(note), 100)
        env = synthesize_environment_layer("gentle_window_rain", 4410, seed=42)
        self.assertEqual(env.shape, (4410, 2))

    def test_mixing_no_clipping(self):
        n = 44100
        music = np.random.normal(0, 0.2, (n, 2)).astype(np.float32)
        env = np.random.normal(0, 0.05, (n, 2)).astype(np.float32)
        mixed = mix_master(music, env, "study")
        self.assertLess(float(np.max(np.abs(mixed))), 0.995)

    def test_visuals_and_provenance(self):
        theme = resolve_theme("winter_cabin")
        im = render_scene_frame(theme, 0, 10, 0.5, width=1280, height=720, show_title=True)
        self.assertEqual(im.size, (1280, 720))

        with tempfile.TemporaryDirectory() as tmp:
            cat = os.path.join(tmp, "catalog.json")
            entry = record_provenance(
                cat, "t1", theme.id, 123, 72, "C major", ["Cmaj7"],
                theme.instruments, theme.environments, ["intro"], 10.0,
                "a.wav", None, "c.jpg", "m.txt", {},
            )
            self.assertEqual(entry["track_id"], "t1")
            found = search_catalog(cat, theme="winter_cabin")
            self.assertEqual(len(found), 1)


if __name__ == "__main__":
    unittest.main()
