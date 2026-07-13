"""Unit tests for scripts/score_assessment.py."""
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


score = load_module("score_assessment", ROOT / "scripts" / "score_assessment.py")


class TestNormalizeAnswer(unittest.TestCase):
    def test_bool_true_is_yes(self):
        self.assertEqual(score.normalize_answer(True), "yes")

    def test_bool_false_is_no(self):
        self.assertEqual(score.normalize_answer(False), "no")

    def test_string_preserved_lower(self):
        self.assertEqual(score.normalize_answer("Partial"), "partial")


class TestAnswerWeight(unittest.TestCase):
    def test_weights(self):
        self.assertEqual(score.answer_weight("yes"), 1.0)
        self.assertEqual(score.answer_weight("partial"), 0.5)
        self.assertEqual(score.answer_weight("no"), 0.0)
        self.assertEqual(score.answer_weight("na"), 1.0)
        self.assertEqual(score.answer_weight(True), 1.0)


class TestDimensionLevel(unittest.TestCase):
    def test_all_yes_achieves_level(self):
        signals = [
            {"id": "a", "min_level": 4, "mandatory": True},
            {"id": "b", "min_level": 4, "mandatory": True},
        ]
        evidence = {"signals": {"a": {"answer": "yes"}, "b": {"answer": "yes"}}}
        result = score.dimension_level(signals, evidence)
        self.assertEqual(result["level"], 4)

    def test_partial_mandatory_fails_level(self):
        signals = [{"id": "a", "min_level": 4, "mandatory": True}]
        evidence = {"signals": {"a": {"answer": "partial"}}}
        result = score.dimension_level(signals, evidence)
        self.assertEqual(result["level"], 0)


class TestScoreAssessmentIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="maturity-score-")
        self.assess_dir = Path(self.tmp)
        shutil.copy(FIXTURES / "l4-evidence.yaml", self.assess_dir / "evidence.yaml")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_score_json_with_dimensions(self):
        # Point script at temp dir; rubric resolved via script parent fallback.
        orig_argv = sys.argv
        try:
            sys.argv = ["score_assessment.py", str(self.assess_dir)]
            rc = score.main()
        finally:
            sys.argv = orig_argv
        self.assertEqual(rc, 0)
        out = json.loads((self.assess_dir / "score.json").read_text())
        self.assertIn("dimensions", out)
        self.assertGreater(len(out["dimensions"]), 0)
        self.assertIn("floor_level", out)
        self.assertIn("weighted_level", out)

    def test_boolean_yaml_answers_score(self):
        shutil.copy(FIXTURES / "bool-evidence.yaml", self.assess_dir / "evidence.yaml")
        orig_argv = sys.argv
        try:
            sys.argv = ["score_assessment.py", str(self.assess_dir)]
            rc = score.main()
        finally:
            sys.argv = orig_argv
        self.assertEqual(rc, 0)
        out = json.loads((self.assess_dir / "score.json").read_text())
        intent = next(d for d in out["dimensions"] if d["id"] == "intent_spec")
        detail = intent["details"][0]
        # true must normalize to yes (ratio > 0); false must normalize to no
        self.assertGreater(detail["ratio"], 0)
        self.assertNotIn("human_writes_tickets", detail.get("failed_mandatory", []))

    def test_missing_evidence_exits_nonzero(self):
        (self.assess_dir / "evidence.yaml").unlink()
        orig_argv = sys.argv
        try:
            sys.argv = ["score_assessment.py", str(self.assess_dir)]
            rc = score.main()
        finally:
            sys.argv = orig_argv
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
