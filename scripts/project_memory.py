#!/usr/bin/env python3
"""Project-memory contract for Metis assessments and exports."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
TEMPLATE = PROJECTS / "_template" / "project-memory.md"


def configured_projects(projects: Path) -> list[Path]:
    return sorted(
        path.parent
        for path in projects.glob("*/project.yaml")
        if path.parent.name != "_template"
    )


def valid_memory(path: Path) -> bool:
    return path.is_file() and bool(path.read_text(encoding="utf-8").strip())


def missing_memories(projects: Path) -> list[Path]:
    return [
        project
        for project in configured_projects(projects)
        if not valid_memory(project / "project-memory.md")
    ]


def bootstrap(projects: Path, template: Path) -> list[Path]:
    body = template.read_text(encoding="utf-8")
    created: list[Path] = []
    for project in configured_projects(projects):
        memory = project / "project-memory.md"
        if not memory.exists():
            memory.write_text(
                body.replace("<Project Name>", project.name).replace("<slug>", project.name),
                encoding="utf-8",
            )
            created.append(memory)
    return created


def append_export(
    project: Path,
    assessment_id: str,
    headline: str,
    weighted_level: object,
    artifact: str,
    date: str | None = None,
) -> None:
    memory = project / "project-memory.md"
    if not valid_memory(memory):
        raise ValueError(f"missing or empty project memory: {memory}")
    fields = [assessment_id, headline, str(weighted_level), artifact]
    if any(not field.strip() for field in fields):
        raise ValueError("assessment, headline, weighted level, and artifact are required")
    text = memory.read_text(encoding="utf-8")
    prefix = "" if text.endswith("\n") else "\n"
    if "## Run history" not in text:
        prefix += "\n## Run history\n\n"
    row = (
        f"- {date or dt.date.today().isoformat()} | {assessment_id} | "
        f"{headline}; weighted {weighted_level} | `{artifact}`\n"
    )
    with memory.open("a", encoding="utf-8") as handle:
        handle.write(prefix + row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects", type=Path, default=PROJECTS)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap", action="store_true")
    args = parser.parse_args()
    if args.bootstrap:
        for path in bootstrap(args.projects, args.template):
            print(f"created {path}")
    if args.check or args.bootstrap:
        missing = missing_memories(args.projects)
        if missing:
            for project in missing:
                print(f"missing project-memory.md: {project}", file=sys.stderr)
            return 1
        print("project memory check passed")
        return 0
    parser.error("choose --check or --bootstrap")


if __name__ == "__main__":
    raise SystemExit(main())
