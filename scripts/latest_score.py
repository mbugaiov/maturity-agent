#!/usr/bin/env python3
"""Print the latest scorecard slice for a maturity-agent project.

Usage:
    python3 scripts/latest_score.py --slug pantheon-qa [--json]

Exit codes:
    0  score found
    1  usage / bad args
    2  no assessment or missing score.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def resolve_assessment_dir(slug: str) -> Path | None:
    """Prefer project-memory active_assessment; else newest assessments/* with score.json."""
    proj = ROOT / "projects" / slug
    if not proj.is_dir():
        return None

    mem = proj / "project-memory.md"
    if mem.exists():
        m = re.search(r"^active_assessment:\s*(\S+)", mem.read_text(encoding="utf-8"), re.M)
        if m:
            candidate = proj / m.group(1).rstrip("/")
            if (candidate / "score.json").is_file():
                return candidate

    assessments = proj / "assessments"
    if not assessments.is_dir():
        return None
    scored = [
        d for d in assessments.iterdir() if d.is_dir() and (d / "score.json").is_file()
    ]
    if not scored:
        return None
    return max(scored, key=lambda p: p.stat().st_mtime)


def scorecard_slice(slug: str, assess_dir: Path) -> dict:
    score = json.loads((assess_dir / "score.json").read_text(encoding="utf-8"))
    dims = {d["id"]: d["level"] for d in score.get("dimensions") or []}
    assessment_id = assess_dir.name
    assessed_on = assessment_id[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", assessment_id) else ""
    return {
        "slug": slug,
        "assessmentId": assessment_id,
        "assessedOn": assessed_on,
        "headline_hint": score.get("headline_hint"),
        "weighted_level": score.get("weighted_level"),
        "operational_level": score.get("operational_level"),
        "floor_level": score.get("floor_level"),
        "version": score.get("version"),
        "dimensions": dims,
        "score_path": str(assess_dir / "score.json"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, help="Project slug under projects/")
    parser.add_argument("--json", action="store_true", help="Force JSON (default)")
    args = parser.parse_args()

    assess_dir = resolve_assessment_dir(args.slug)
    if assess_dir is None:
        print(
            f"No score.json for slug={args.slug!r} under projects/{args.slug}/assessments/",
            file=sys.stderr,
        )
        return 2

    out = scorecard_slice(args.slug, assess_dir)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
