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


class TestEffectiveSignalAnswer(unittest.TestCase):
    def test_per_repo_product_wins_for_blocking_review(self):
        entry = {
            "answer": "no",
            "per_repo": {"product": "yes", "engine": "no"},
        }
        self.assertEqual(
            score.effective_signal_answer(entry, "blocking_review_ci"),
            "yes",
        )

    def test_per_repo_product_wins_for_auto_merge(self):
        entry = {
            "answer": "no",
            "per_repo": {"product": "yes", "engine": "no"},
        }
        self.assertEqual(score.effective_signal_answer(entry, "auto_merge"), "yes")

    def test_per_repo_any_yes_for_non_ci_signal(self):
        entry = {"answer": "no", "per_repo": {"a": "partial", "b": "yes"}}
        self.assertEqual(score.effective_signal_answer(entry, "other_signal"), "yes")


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


class TestHeadlineRules(unittest.TestCase):
    def test_l5_prime_rule_matches_partial_loop(self):
        dim_levels = {
            "factory_loop": 4,
            "qa_autonomy": 5,
            "dev_autonomy": 5,
            "deploy_verification": 5,
            "review_gate": 5,
        }
        evidence = {"signals": {"prod_human_gated": {"answer": "yes"}}}
        rubric = score.load_yaml(ROOT / "framework" / "rubric.yaml")
        headline = score.resolve_headline(rubric, dim_levels, evidence)
        self.assertEqual(headline["headline_hint"], "L5′ (L5 on STG)")


class TestFactoryLoopAdjustment(unittest.TestCase):
    def test_partial_scheduled_ticks_boosts_factory_loop(self):
        rubric = score.load_yaml(ROOT / "framework" / "rubric.yaml")
        factory_dim = next(d for d in rubric["dimensions"] if d["id"] == "factory_loop")
        evidence = {
            "signals": {
                "scheduled_ticks": {"answer": "partial"},
                "tick_gate": {"answer": "yes"},
            }
        }
        result = score.dimension_level(factory_dim["signals"], evidence)
        self.assertEqual(result["level"], 0)
        dims = [{"id": "factory_loop", "level": result["level"], "name": "Factory loop", "weight": 1.0, "details": result["details"]}]
        adjusted = score.apply_dimension_adjustments(dims, evidence, rubric)
        self.assertGreaterEqual(adjusted[0]["level"], 4)
        self.assertTrue(adjusted[0].get("adjusted"))


class TestScoreAssessmentIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="maturity-score-")
        self.assess_dir = Path(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run_score(self, fixture_name: str = "l4-evidence.yaml") -> dict:
        shutil.copy(FIXTURES / fixture_name, self.assess_dir / "evidence.yaml")
        orig_argv = sys.argv
        try:
            sys.argv = ["score_assessment.py", str(self.assess_dir)]
            rc = score.main()
        finally:
            sys.argv = orig_argv
        self.assertEqual(rc, 0)
        return json.loads((self.assess_dir / "score.json").read_text())

    def test_writes_score_json_with_dimensions(self):
        out = self._run_score("l4-evidence.yaml")
        self.assertIn("dimensions", out)
        self.assertGreater(len(out["dimensions"]), 0)
        self.assertIn("floor_level", out)
        self.assertIn("weighted_level", out)
        self.assertIn("operational_level", out)
        self.assertIn("headline_hint", out)
        self.assertIn("headline_rule_matched", out)

    def test_l5_prime_fixture_headline_not_floor(self):
        out = self._run_score("l5-prime-evidence.yaml")
        self.assertEqual(out["headline_hint"], "L5′ (L5 on STG)")
        self.assertGreaterEqual(out["operational_level"], 4)
        factory = next(d for d in out["dimensions"] if d["id"] == "factory_loop")
        self.assertGreaterEqual(factory["level"], 4)
        self.assertTrue(factory.get("adjusted"))
        # operational should exceed strict floor when loop is partial
        self.assertGreaterEqual(out["operational_level"], out["floor_level"])

    def test_prose_trap_per_repo_product_wins(self):
        out = self._run_score("prose-trap-evidence.yaml")
        review = next(d for d in out["dimensions"] if d["id"] == "review_gate")
        deploy = next(d for d in out["dimensions"] if d["id"] == "deploy_verification")
        # Top-level answer=no must not override per_repo.product=yes for CI signals
        self.assertGreaterEqual(review["level"], 5)
        self.assertGreaterEqual(deploy["level"], 5)
        blocking = score.signal_answer(
            score.load_yaml(self.assess_dir / "evidence.yaml"),
            "blocking_review_ci",
        )
        auto = score.signal_answer(
            score.load_yaml(self.assess_dir / "evidence.yaml"),
            "auto_merge",
        )
        self.assertEqual(blocking, "yes")
        self.assertEqual(auto, "yes")

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
        self.assertGreater(detail["ratio"], 0)
        self.assertNotIn("human_writes_tickets", detail.get("failed_mandatory", []))

    def test_missing_evidence_exits_nonzero(self):
        shutil.copy(FIXTURES / "l4-evidence.yaml", self.assess_dir / "evidence.yaml")
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
