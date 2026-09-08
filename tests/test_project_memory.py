from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test_export_scorecard import load_module

ROOT = Path(__file__).resolve().parents[1]
memory = load_module("project_memory_contract", ROOT / "scripts" / "project_memory.py")


class ProjectMemoryContractTest(unittest.TestCase):
    def test_yaml_without_memory_fails_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo"
            project.mkdir()
            (project / "project.yaml").write_text("slug: demo\n")
            self.assertEqual(memory.missing_memories(Path(tmp)), [project])

    def test_bootstrap_creates_nonempty_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            projects = Path(tmp)
            project = projects / "demo"
            project.mkdir()
            (project / "project.yaml").write_text("slug: demo\n")
            created = memory.bootstrap(
                projects, ROOT / "projects" / "_template" / "project-memory.md"
            )
            self.assertEqual(created, [project / "project-memory.md"])
            self.assertTrue(memory.valid_memory(project / "project-memory.md"))

    def test_append_without_memory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "project memory"):
                memory.append_export(Path(tmp), "run-1", "L4", 4, "exports/demo/latest.json")


if __name__ == "__main__":
    unittest.main()
