#!/usr/bin/env python3
"""Score a maturity assessment from evidence.yaml against framework/rubric.yaml.

Usage:
    python3 scripts/score_assessment.py projects/<slug>/assessments/<date>-<scope>

Writes score.json alongside evidence.yaml. Requires PyYAML (pip install pyyaml).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

# Dimensions that define routine factory operation on the target environment.
OPERATIONAL_DIMS = frozenset({
    "dev_autonomy",
    "review_gate",
    "deploy_verification",
    "qa_autonomy",
    "defect_loop",
    "factory_loop",
})

# Signals where per-repo product CI is authoritative when present.
PER_REPO_SIGNALS = frozenset({
    "blocking_review_ci",
    "auto_merge",
    "auto_deploy_nonprod",
    "buildid_gate",
})


def load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        raise SystemExit("PyYAML required: pip install pyyaml")
    return yaml.safe_load(text) or {}


def normalize_answer(ans) -> str:
    if isinstance(ans, bool):
        return "yes" if ans else "no"
    return str(ans).lower()


def answer_weight(ans) -> float:
    return {"yes": 1.0, "partial": 0.5, "no": 0.0, "na": 1.0}.get(normalize_answer(ans), 0.0)


def effective_signal_answer(entry: dict | None, signal_id: str | None = None) -> str:
    """Resolve signal answer; per_repo.product wins for shipping-repo signals."""
    if not entry:
        return "no"
    per_repo = entry.get("per_repo") or {}
    top = normalize_answer(entry.get("answer", "no"))
    if per_repo:
        if signal_id in PER_REPO_SIGNALS:
            if "product" in per_repo:
                return normalize_answer(per_repo["product"])
            return top
        weights = [
            answer_weight(v)
            for v in per_repo.values()
            if normalize_answer(v) != "na"
        ]
        if not weights:
            return top
        if max(weights) >= 1.0:
            return "yes"
        if max(weights) >= 0.5:
            return "partial"
        return "no"
    return top


def dimension_level(signals: list, evidence: dict) -> dict:
    """Highest level L where all mandatory signals for that L pass."""
    by_level: dict[int, list] = {}
    for sig in signals:
        lvl = int(sig["min_level"])
        by_level.setdefault(lvl, []).append(sig)

    levels = sorted(by_level.keys())
    achieved = 0
    details = []

    def score_signals(checks: list) -> tuple[float, float, list]:
        passed = 0.0
        total = 0
        failed_mandatory = []
        for sig in checks:
            sid = sig["id"]
            entry = (evidence.get("signals") or {}).get(sid) or {}
            ans = effective_signal_answer(entry, sid)
            if ans == "na":
                continue
            w = answer_weight(ans)
            total += 1
            passed += w
            if w < 1.0 and sig.get("mandatory", True):
                failed_mandatory.append(sid)
        return passed, total, failed_mandatory

    for lvl in levels:
        mandatory = [s for s in by_level[lvl] if s.get("mandatory", True)]
        optional = [s for s in by_level[lvl] if not s.get("mandatory", True)]

        if mandatory:
            m_passed, m_total, failed_mandatory = score_signals(mandatory)
            if failed_mandatory:
                ratio = m_passed / m_total if m_total else 0.0
                details.append({
                    "level": lvl,
                    "status": "fail",
                    "ratio": round(ratio, 2),
                    "failed_mandatory": failed_mandatory,
                })
                break
            achieved = max(achieved, lvl)
            o_passed, o_total, _ = score_signals(optional)
            total = m_total + o_total
            passed = m_passed + o_passed
            ratio = passed / total if total else 1.0
            details.append({"level": lvl, "status": "pass", "ratio": round(ratio, 2)})
        elif optional:
            o_passed, o_total, _ = score_signals(optional)
            ratio = o_passed / o_total if o_total else 1.0
            if ratio >= 0.85:
                achieved = max(achieved, lvl)
            details.append({
                "level": lvl,
                "status": "pass" if ratio >= 0.85 else "optional-incomplete",
                "ratio": round(ratio, 2),
                "failed_mandatory": [],
            })
        else:
            achieved = max(achieved, lvl)
            details.append({"level": lvl, "status": "pass", "ratio": 1.0})

    return {"level": achieved, "details": details}


def signal_answer(evidence: dict, signal_id: str) -> str:
    entry = (evidence.get("signals") or {}).get(signal_id) or {}
    return effective_signal_answer(entry, signal_id)


def apply_dimension_adjustments(dimensions: list[dict], evidence: dict, rubric: dict) -> list[dict]:
    """Post-process dimension levels using rubric scoring_adjustments."""
    adjustments = rubric.get("scoring_adjustments") or {}
    dim_by_id = {d["id"]: d for d in dimensions}
    signals = evidence.get("signals") or {}

    # factory_loop: partial armed loop + tick gate still counts as operational L5′
    factory_adj = adjustments.get("factory_loop") or {}
    if "factory_loop" in dim_by_id:
        scheduled = signal_answer(evidence, "scheduled_ticks")
        tick_gate = signal_answer(evidence, "tick_gate")
        backlog = signal_answer(evidence, "factory_backlog_complete")
        min_partial = int(factory_adj.get("partial_with_tick_gate_min_level", 4))
        min_backlog = int(factory_adj.get("backlog_complete_with_tick_gate_min_level", 4))

        boost = dim_by_id["factory_loop"]["level"]
        if scheduled in ("yes", "partial") and tick_gate == "yes":
            boost = max(boost, min_partial)
        if backlog == "yes" and tick_gate == "yes":
            boost = max(boost, min_backlog)
        if scheduled == "yes" and tick_gate == "yes":
            boost = max(boost, 5)

        if boost != dim_by_id["factory_loop"]["level"]:
            dim_by_id["factory_loop"]["level"] = boost
            dim_by_id["factory_loop"]["adjusted"] = True
            dim_by_id["factory_loop"]["adjustment_reason"] = (
                f"scheduled_ticks={scheduled}, tick_gate={tick_gate}, "
                f"factory_backlog_complete={backlog}"
            )

    return list(dim_by_id.values())


def eval_headline_condition(condition: str, dim_levels: dict[str, int], evidence: dict) -> bool:
    """Evaluate rubric level_headline_rules condition strings."""
    parts = [p.strip() for p in condition.split(" AND ") if p.strip()]
    for part in parts:
        ge_match = re.match(r"^(\w+)\s*>=\s*(\d+)$", part)
        if ge_match:
            dim_id, min_lvl = ge_match.group(1), int(ge_match.group(2))
            if dim_levels.get(dim_id, 0) < min_lvl:
                return False
            continue

        eq_match = re.match(r"^(\w+)\s*==\s*(yes|no|partial|na)$", part)
        if eq_match:
            sig_id, expected = eq_match.group(1), eq_match.group(2)
            if signal_answer(evidence, sig_id) != expected:
                return False
            continue

        return False
    return True


def resolve_headline(rubric: dict, dim_levels: dict[str, int], evidence: dict) -> dict:
    """Pick headline from level_headline_rules; return hint + matched rule."""
    for rule in rubric.get("level_headline_rules") or []:
        if "condition" not in rule:
            continue
        if eval_headline_condition(rule["condition"], dim_levels, evidence):
            return {
                "headline_hint": rule["headline"],
                "headline_rule_matched": rule["condition"],
            }

    fallback = next(
        (r.get("fallback") for r in rubric.get("level_headline_rules") or [] if "fallback" in r),
        None,
    )
    operational = min(
        (dim_levels.get(d, 0) for d in OPERATIONAL_DIMS),
        default=0,
    )
    weighted_floor = min(dim_levels.values()) if dim_levels else 0

    if operational >= 5:
        hint = "L5′ (L5 on STG)" if signal_answer(evidence, "prod_human_gated") == "yes" else "L5"
    elif operational >= 4:
        hint = f"L{operational} (operational)"
    else:
        hint = f"L{weighted_floor} (floor)"

    return {
        "headline_hint": hint,
        "headline_rule_matched": fallback or "computed fallback",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: score_assessment.py <assessment-dir>", file=sys.stderr)
        return 1

    assess_dir = Path(sys.argv[1]).resolve()
    if not assess_dir.is_dir():
        print(f"Not a directory: {assess_dir}", file=sys.stderr)
        return 1

    root = assess_dir
    while root.name != "maturity-agent" and root.parent != root:
        root = root.parent
    if root.name != "maturity-agent":
        root = Path(__file__).resolve().parent.parent

    rubric_path = root / "framework" / "rubric.yaml"
    evidence_path = assess_dir / "evidence.yaml"
    if not evidence_path.exists():
        print(f"Missing {evidence_path}", file=sys.stderr)
        return 1

    rubric = load_yaml(rubric_path)
    evidence = load_yaml(evidence_path)

    dimensions_out = []
    levels = []
    weights = []

    for dim in rubric.get("dimensions", []):
        result = dimension_level(dim.get("signals", []), evidence)
        w = float(dim.get("weight", 1.0))
        dimensions_out.append({
            "id": dim["id"],
            "name": dim["name"],
            "level": result["level"],
            "weight": w,
            "details": result["details"],
        })
        levels.append(result["level"])
        weights.append(w)

    dimensions_out = apply_dimension_adjustments(dimensions_out, evidence, rubric)
    dim_levels = {d["id"]: d["level"] for d in dimensions_out}
    levels = [d["level"] for d in dimensions_out]

    floor = min(levels) if levels else 0
    weighted = (
        sum(d["level"] * d["weight"] for d in dimensions_out) / sum(weights)
        if weights
        else 0
    )
    operational = min(
        (dim_levels.get(d, 0) for d in OPERATIONAL_DIMS),
        default=0,
    )

    headline = resolve_headline(rubric, dim_levels, evidence)

    out = {
        "framework": rubric.get("framework"),
        "version": rubric.get("version"),
        "floor_level": floor,
        "operational_level": operational,
        "weighted_level": round(weighted, 2),
        "dimensions": dimensions_out,
        **headline,
    }

    out_path = assess_dir / "score.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
