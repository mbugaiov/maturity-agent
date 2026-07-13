#!/usr/bin/env python3
"""Score a maturity assessment from evidence.yaml against framework/rubric.yaml.

Usage:
    python3 scripts/score_assessment.py projects/<slug>/assessments/<date>-<scope>

Writes score.json alongside evidence.yaml. Requires PyYAML (pip install pyyaml) or uses stdlib-only fallback.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


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


def dimension_level(signals: list, evidence: dict) -> dict:
    """Highest level L where all mandatory signals for that L pass."""
    by_level: dict[int, list] = {}
    for sig in signals:
        lvl = int(sig["min_level"])
        by_level.setdefault(lvl, []).append(sig)

    levels = sorted(by_level.keys())
    achieved = 0
    details = []

    for lvl in levels:
        mandatory = [s for s in by_level[lvl] if s.get("mandatory", True)]
        optional = [s for s in by_level[lvl] if not s.get("mandatory", True)]
        checks = mandatory + optional
        if not checks:
            continue

        passed = 0
        total = 0
        failed_ids = []
        for sig in checks:
            sid = sig["id"]
            entry = (evidence.get("signals") or {}).get(sid) or {}
            ans = entry.get("answer", "no")
            if normalize_answer(ans) == "na":
                continue
            w = answer_weight(ans)
            total += 1
            passed += w
            if w < 1.0 and sig.get("mandatory", True):
                failed_ids.append(sid)

        ratio = passed / total if total else 1.0
        mandatory_ok = not failed_ids
        if mandatory_ok and ratio >= 0.85:
            achieved = max(achieved, lvl)
            details.append({"level": lvl, "status": "pass", "ratio": round(ratio, 2)})
        else:
            details.append({
                "level": lvl,
                "status": "fail",
                "ratio": round(ratio, 2),
                "failed_mandatory": failed_ids,
            })
            break

    return {"level": achieved, "details": details}


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
        # fallback: script relative
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

    floor = min(levels) if levels else 0
    weighted = (
        sum(d["level"] * d["weight"] for d in dimensions_out) / sum(weights)
        if weights
        else 0
    )

    out = {
        "framework": rubric.get("framework"),
        "version": rubric.get("version"),
        "floor_level": floor,
        "weighted_level": round(weighted, 2),
        "dimensions": dimensions_out,
        "headline_hint": (
            "L5′ (L5 on STG)" if floor >= 5 and weighted >= 4.5
            else f"L{int(weighted)}" if weighted >= 4
            else f"L{floor} (floor)"
        ),
    }

    out_path = assess_dir / "score.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
