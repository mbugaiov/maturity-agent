#!/usr/bin/env python3
"""Publish a TRACKED scorecard snapshot for factory consumers (DO / Pantheon).

Unlike projects/*/assessments/**/score.json (gitignored), exports/<slug>/latest.json
is committed so remote hosts can fetch without a local assessment tree.

Usage:
    python3 scripts/export_scorecard.py --slug pantheon-qa
    python3 scripts/export_scorecard.py --slug pantheon-qa --assessment 2026-08-16-defect-l5
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Reuse latest_score helpers
sys.path.insert(0, str(Path(__file__).resolve().parent))
from latest_score import resolve_assessment_dir, scorecard_slice  # noqa: E402
from project_memory import append_export, valid_memory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument(
        "--assessment",
        help="Assessment folder name under projects/<slug>/assessments/ (default: latest)",
    )
    args = parser.parse_args()

    proj = ROOT / "projects" / args.slug
    if not proj.is_dir():
        print(f"Unknown slug: {args.slug}", file=sys.stderr)
        return 1
    memory = proj / "project-memory.md"
    if not valid_memory(memory):
        print(f"Missing or empty project memory: {memory}", file=sys.stderr)
        return 3

    if args.assessment:
        assess_dir = proj / "assessments" / args.assessment
        if not (assess_dir / "score.json").is_file():
            print(f"Missing score.json: {assess_dir}", file=sys.stderr)
            return 2
    else:
        assess_dir = resolve_assessment_dir(args.slug)
        if assess_dir is None:
            print(f"No score.json for {args.slug}", file=sys.stderr)
            return 2

    slice_ = scorecard_slice(args.slug, assess_dir)
    payload = {
        **slice_,
        "exportedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "maturity-agent",
        "note": (
            "Tracked export for factory consumers (DigitalOcean / Pantheon). "
            "Local assessments under projects/ remain gitignored."
        ),
    }
    # Drop host-local absolute path from published artifact
    payload.pop("score_path", None)

    out_dir = ROOT / "exports" / args.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "latest.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_path = out_dir / "latest.md"
    dims = payload.get("dimensions") or {}
    dim_lines = "\n".join(f"| `{k}` | {v} |" for k, v in sorted(dims.items()))
    md_path.write_text(
        f"""# {args.slug} — latest Metis export

| Field | Value |
|-------|-------|
| Assessment | `{payload.get("assessmentId")}` |
| Assessed | {payload.get("assessedOn")} |
| Headline | {payload.get("headline_hint")} |
| Weighted | {payload.get("weighted_level")} |
| Operational | {payload.get("operational_level")} |
| Floor | {payload.get("floor_level")} |
| Exported | {payload.get("exportedAt")} |

## Dimensions

| Id | Level |
|----|-------|
{dim_lines}

Pull (DO / CI):

```bash
curl -fsSL https://raw.githubusercontent.com/<org>/maturity-agent/<branch>/exports/{args.slug}/latest.json
```
""",
        encoding="utf-8",
    )

    append_export(
        proj,
        str(payload.get("assessmentId") or ""),
        str(payload.get("headline_hint") or ""),
        payload.get("weighted_level", ""),
        str(out_path.relative_to(ROOT)),
    )
    print(str(out_path))
    print(f"memory_updated=true project={args.slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
