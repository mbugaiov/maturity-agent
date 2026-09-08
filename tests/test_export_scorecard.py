"""Tests for latest_score.py / export_scorecard.py."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


latest = load_module("latest_score", ROOT / "scripts" / "latest_score.py")


class TestLatestScoreHelpers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="maturity-latest-")
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        self.proj = Path(self.tmp) / "projects" / "demo"
        self.assess = self.proj / "assessments" / "2026-08-16-demo"
        self.assess.mkdir(parents=True)
        score = {
            "headline_hint": "L4 (engineering team)",
            "weighted_level": 3.5,
            "operational_level": 4,
            "floor_level": 3,
            "version": "1.2",
            "dimensions": [
                {"id": "factory_loop", "level": 4},
                {"id": "defect_loop", "level": 3},
            ],
        }
        (self.assess / "score.json").write_text(json.dumps(score) + "\n", encoding="utf-8")
        (self.proj / "project-memory.md").write_text(
            "active_assessment: assessments/2026-08-16-demo\n", encoding="utf-8"
        )

    def test_resolve_and_slice(self):
        # Point helper ROOT at tmp tree
        latest.ROOT = Path(self.tmp)
        got = latest.resolve_assessment_dir("demo")
        self.assertEqual(got, self.assess)
        slice_ = latest.scorecard_slice("demo", got)
        self.assertEqual(slice_["assessmentId"], "2026-08-16-demo")
        self.assertEqual(slice_["operational_level"], 4)
        self.assertEqual(slice_["dimensions"]["defect_loop"], 3)

    def test_missing_slug_returns_none(self):
        latest.ROOT = Path(self.tmp)
        self.assertIsNone(latest.resolve_assessment_dir("nope"))


class TestExportScorecardCli(unittest.TestCase):
    def test_export_writes_tracked_json(self):
        tmp = tempfile.mkdtemp(prefix="maturity-export-")
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        # Build a mini maturity-agent root with scripts + fixture assessment
        root = Path(tmp)
        slug = "demo"
        assess = root / "projects" / slug / "assessments" / "2026-08-16-demo"
        assess.mkdir(parents=True)
        shutil.copy(ROOT / "tests" / "fixtures" / "l5-prime-evidence.yaml", assess / "evidence.yaml")
        # score via real scorer into this tree — use a pre-written score.json for isolation
        score = {
            "headline_hint": "L5′ (L5 on STG)",
            "weighted_level": 4.79,
            "operational_level": 4,
            "floor_level": 4,
            "version": "1.2",
            "dimensions": [{"id": "defect_loop", "level": 5}, {"id": "factory_loop", "level": 4}],
        }
        (assess / "score.json").write_text(json.dumps(score) + "\n", encoding="utf-8")
        (root / "projects" / slug / "project-memory.md").write_text(
            f"active_assessment: assessments/{assess.name}\n", encoding="utf-8"
        )
        scripts = root / "scripts"
        scripts.mkdir()
        for name in ("latest_score.py", "project_memory.py", "export_scorecard.py"):
            shutil.copy(ROOT / "scripts" / name, scripts / name)

        orig_argv = sys.argv
        # Patch export's ROOT by running as __main__ with cwd... export uses Path(__file__).parent.parent
        # so running the copied script is enough
        import subprocess

        rc = subprocess.run(
            [sys.executable, str(scripts / "export_scorecard.py"), "--slug", slug],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(rc.returncode, 0, rc.stderr)
        out = root / "exports" / slug / "latest.json"
        self.assertTrue(out.is_file())
        data = json.loads(out.read_text())
        self.assertEqual(data["floor_level"], 4)
        self.assertEqual(data["dimensions"]["defect_loop"], 5)
        self.assertNotIn("score_path", data)
        self.assertTrue((root / "exports" / slug / "latest.md").is_file())
        memory = (root / "projects" / slug / "project-memory.md").read_text()
        self.assertIn("## Run history", memory)
        self.assertIn("2026-08-16-demo", memory)
        self.assertIn("weighted 4.79", memory)

    def test_export_fails_without_project_memory(self):
        tmp = tempfile.mkdtemp(prefix="maturity-export-no-memory-")
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        root = Path(tmp)
        slug = "demo"
        assess = root / "projects" / slug / "assessments" / "2026-08-16-demo"
        assess.mkdir(parents=True)
        (assess / "score.json").write_text(
            json.dumps(
                {
                    "headline_hint": "L4",
                    "weighted_level": 4,
                    "operational_level": 4,
                    "floor_level": 4,
                    "dimensions": [],
                }
            )
        )
        scripts = root / "scripts"
        scripts.mkdir()
        for name in ("latest_score.py", "project_memory.py", "export_scorecard.py"):
            shutil.copy(ROOT / "scripts" / name, scripts / name)
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                str(scripts / "export_scorecard.py"),
                "--slug",
                slug,
                "--assessment",
                assess.name,
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 3)
        self.assertIn("project memory", result.stderr.lower())
        self.assertFalse((root / "exports" / slug / "latest.json").exists())


if __name__ == "__main__":
    unittest.main()
