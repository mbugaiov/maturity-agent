"""Unit tests for scripts/build_presentation.py."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
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


presentation = load_module("build_presentation", ROOT / "scripts" / "build_presentation.py")
score = load_module("score_assessment", ROOT / "scripts" / "score_assessment.py")


class TestPresentationHelpers(unittest.TestCase):
    def test_parse_report_sections(self):
        text = "## Executive summary\nLine one\n\n## Strengths\n- Item"
        sections = presentation.parse_report_sections(text)
        self.assertIn("executive summary", sections)
        self.assertIn("strengths", sections)
        self.assertIn("Item", sections["strengths"])

    def test_extract_headline(self):
        report = "**Headline level:** **L3 (Developer)**\n"
        self.assertEqual(presentation.extract_headline(report), "L3 (Developer)")

    def test_infer_current_marker(self):
        self.assertEqual(presentation.infer_current_marker("L3 (Developer)"), "L3")
        self.assertEqual(presentation.infer_current_marker("L5′ on STG"), "L5′")

    def test_next_level_label(self):
        self.assertEqual(presentation.next_level_label("L3"), "L4")
        self.assertEqual(presentation.next_level_label("L4"), "L5′")

    def test_bullets_from_section(self):
        body = "- First\n- Second\n1. Third"
        self.assertEqual(presentation.bullets_from_section(body), ["First", "Second", "Third"])

    def test_build_html_contains_reveal(self):
        ctx = {
            "title": "Fixture",
            "date": "2026-07-13",
            "assessment_id": "2026-07-13-baseline",
            "target": "fixture-proj",
            "headline": "L3 (Developer)",
            "summary_line": "Summary",
            "current_marker": "L3",
            "next_level": "L4",
            "dimensions": [{"name": "Intent", "level": 4}],
            "floor": 3,
            "operational": 3,
            "weighted": 3.2,
            "strengths": ["Spec-first"],
            "gap_bullets": ["No CI"],
            "path_rows": [["P1", "Add CI"]],
            "gap_signals": [],
            "top_actions": ["Add CI"],
            "achieved_markers": set(),
            "generated": "2026-07-13",
        }
        html = presentation.build_html(ctx)
        self.assertIn("reveal.js", html)
        self.assertIn("How we evaluated", html)
        self.assertIn("Fixture", html)


class TestPresentationIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="maturity-pres-")
        self.assess_dir = Path(self.tmp)
        shutil.copy(FIXTURES / "l4-evidence.yaml", self.assess_dir / "evidence.yaml")
        shutil.copy(FIXTURES / "sample-report.md", self.assess_dir / "report.md")
        orig_argv = sys.argv
        sys.argv = ["score_assessment.py", str(self.assess_dir)]
        score.main()
        sys.argv = orig_argv

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_main_writes_html_and_markdown(self):
        orig_argv = sys.argv
        try:
            sys.argv = ["build_presentation.py", str(self.assess_dir), "--title", "Fixture Project"]
            rc = presentation.main()
        finally:
            sys.argv = orig_argv
        self.assertEqual(rc, 0)
        html = (self.assess_dir / "presentation.html").read_text()
        md = (self.assess_dir / "presentation.md").read_text()
        self.assertIn("Reveal.initialize", html)
        self.assertIn("Slide 1", md)
        self.assertIn("Fixture Project", md)
        self.assertIn("L3 (Developer)", html)

    def test_missing_score_json_fails(self):
        (self.assess_dir / "score.json").unlink()
        orig_argv = sys.argv
        try:
            sys.argv = ["build_presentation.py", str(self.assess_dir)]
            rc = presentation.main()
        finally:
            sys.argv = orig_argv
        self.assertEqual(rc, 1)

    def test_shell_wrapper(self):
        wrapper = ROOT / "scripts" / "build_presentation.sh"
        subprocess.run(
            [str(wrapper), str(self.assess_dir), "Fixture Project"],
            check=True,
            cwd=ROOT,
        )
        self.assertTrue((self.assess_dir / "presentation.html").exists())


if __name__ == "__main__":
    unittest.main()
