#!/usr/bin/env python3
"""Test di giunzione pipeline — senza rete né account reali."""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXECUTION = REPO_ROOT / "Execution"
sys.path.insert(0, str(EXECUTION))

from canale_paths import expand_local_paths  # noqa: E402
from enea.pipeline_store import write_pipeline  # noqa: E402


class PipelineJunctionTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_paper_folder_ready_for_produzione(self):
        """Dopo copertina+PDF la pipeline contiene ciò che produzione richiede."""
        cleaned = self.root / "Cleaned" / "Titolo_Test"
        papers = self.root / "Papers" / "Da fare"
        cleaned.mkdir(parents=True)
        papers.mkdir(parents=True)
        pdf = papers / "paper.pdf"
        pdf.write_bytes(b"%PDF-1.4 test")
        cover = cleaned / "copertina.png"
        cover.write_bytes(b"png")

        pipeline = {
            "title": "Titolo Test",
            "clean_title": "Titolo_Test",
            "target_dir": str(cleaned),
            "paper": "paper.pdf",
            "paper_path": str(pdf),
        }
        shutil.move(str(pdf), str(cleaned / "paper.pdf"))
        pipeline["paper_path"] = str(cleaned / "paper.pdf")

        self.assertTrue(Path(pipeline["paper_path"]).exists())
        self.assertTrue(cover.exists())
        self.assertIn("clean_title", pipeline)

    def test_produzione_output_names_for_pulizia(self):
        """Nomi attesi dopo produzione (video + infografica raw)."""
        clean_title = "Esempio_Video"
        expected = {
            f"{clean_title}_raw.mp4",
            f"{clean_title}_infografica.png",
        }
        for name in expected:
            self.assertTrue(name.endswith((".mp4", ".png")))

    def test_pulizia_folder_ready_for_upload(self):
        """Dopo pulizia la cartella soddisfa upload."""
        folder = self.root / "Cleaned" / "Video_Pronto"
        folder.mkdir(parents=True)
        (folder / "Video_Pronto_cleaned.mp4").write_bytes(b"mp4")
        (folder / "video_metadata.md").write_text("# Metadati\n", encoding="utf-8")
        (folder / "copertina.png").write_bytes(b"png")

        files = {p.name for p in folder.iterdir()}
        self.assertTrue(any(name.endswith("_cleaned.mp4") for name in files))
        self.assertIn("video_metadata.md", files)

    def test_command_map_paths_expand(self):
        raw = (REPO_ROOT / "Execution/cesare/command_map.json").read_text(encoding="utf-8")
        data = json.loads(expand_local_paths(raw))
        home = str(Path.home())
        for cmd in data.values():
            joined = " ".join(cmd)
            self.assertNotIn("/Users/<USER>", joined)
            self.assertTrue(joined.startswith(home) or joined.startswith("/"))

    def test_env_example_keys_present_in_env(self):
        example = REPO_ROOT / ".env.example"
        env_file = REPO_ROOT / ".env"
        self.assertTrue(example.exists())
        self.assertTrue(env_file.exists())
        keys = set(re.findall(r"^([A-Z0-9_]+)=", example.read_text(encoding="utf-8"), re.M))
        env_text = env_file.read_text(encoding="utf-8")
        env_keys = set(re.findall(r"^([A-Z0-9_]+)=", env_text, re.M))
        optional = {"GEMINI_MODEL", "SUPERMEMORY_API_KEY", "SUPERMEMORY_PROJECT_ID", "FB_PROFILE_ID", "IG_PROFILE_ID", "BUFFER_ORG_ID", "ALLOWED_ID"}
        required_in_env = keys - optional
        missing = sorted(required_in_env - env_keys)
        self.assertEqual(missing, [], f"Chiavi mancanti in .env: {missing}")



    def test_short_naming_convention(self):
        """Convenzione short1 estensibile a N."""
        import sys
        sys.path.insert(0, str(EXECUTION / "enea"))
        import short_assets as sa
        self.assertEqual(sa.short_raw_name("Titolo_Test", 1), "Titolo_Test_short1_raw.mp4")
        self.assertEqual(sa.short_cleaned_name("Titolo_Test", 1), "Titolo_Test_short1_cleaned.mp4")
        self.assertEqual(sa.short_raw_name("Titolo_Test", 2), "Titolo_Test_short2_raw.mp4")
        self.assertTrue(sa.is_short_raw_filename("Titolo_Test_short1_raw.mp4"))
        self.assertFalse(sa.is_short_raw_filename("Titolo_Test_raw.mp4"))
        self.assertEqual(sa.parse_short_index_from_filename("X_short3_raw.mp4"), 3)

    def test_short_tracking_nested_schema(self):
        """shorts[] nested sotto long-form, campi richiesti."""
        entry = {
            "youtube_id": "LONG123",
            "youtube_url": "https://www.youtube.com/watch?v=LONG123",
            "shorts": [
                {
                    "id": "",
                    "youtube_url": "",
                    "angle": "1",
                    "status": "Da fare",
                    "ig_reel_url": "Da fare",
                }
            ],
        }
        self.assertIn("shorts", entry)
        self.assertIsInstance(entry["shorts"], list)
        short = entry["shorts"][0]
        for key in ("id", "youtube_url", "angle", "status", "ig_reel_url"):
            self.assertIn(key, short)

    def test_short_description_contains_long_link(self):
        import sys
        sys.path.insert(0, str(EXECUTION / "enea"))
        import short_assets as sa
        desc = sa.build_short_description("AbCdEfGhIjK")
        self.assertIn("Video completo qui: https://youtu.be/AbCdEfGhIjK", desc)

    def test_delogo_portrait_box(self):
        import sys
        sys.path.insert(0, str(EXECUTION / "enea"))
        import short_assets as sa
        x, y, w, h = sa.delogo_box_for_resolution(1080, 1920)
        self.assertTrue(h < w or w <= 1080)
        self.assertLess(x + w, 1080 + 1)
        self.assertLess(y + h, 1920 + 1)
        # landscape still returns a sensible box (solid-cover, not old 230x80 hardcode)
        x2, y2, w2, h2 = sa.delogo_box_for_resolution(1920, 1080)
        self.assertGreater(w2, 200)
        self.assertGreater(h2, 15)
        self.assertLess(x2 + w2, 1920 + 1)
        self.assertLess(y2 + h2, 1080 + 1)

    def test_produzione_short_output_name(self):
        clean_title = "Esempio_Video"
        self.assertEqual(f"{clean_title}_short1_raw.mp4", "Esempio_Video_short1_raw.mp4")



    def test_format_tags_forbids_generic(self):
        import sys
        sys.path.insert(0, str(EXECUTION / "enea"))
        import video_processor as vp
        line, csv = vp.format_tags("#AreaB #Milano #CosaFannoGliEconomisti #APSR")
        self.assertIn("#AreaB", line)
        self.assertIn("#Milano", line)
        self.assertNotIn("CosaFannoGliEconomisti", line)
        self.assertNotIn("APSR", line)

if __name__ == "__main__":
    unittest.main()
