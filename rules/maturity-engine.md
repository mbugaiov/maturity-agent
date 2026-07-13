# Maturity Agent — hard rules

- Read `framework/shapiro-levels.md` before assigning a headline level.
- Every signal in `evidence.yaml` needs a **citation** (file path, URL, issue key, or interview note).
- Use `yes` only when evidence is **verified**; `partial` when exists but not enforced; `no` when absent; `na` when not applicable to this project type.
- Distinguish **L5′ (factory on STG)** from **full L5** — document what humans still own.
- Do not conflate **application quality** with **SDLC automation maturity**.
- Inspect linked repos read-only unless the user explicitly asks for changes.
- Produce `report.md` in the assessment folder — not chat-only deliverables.
- Update `project-memory.md` at end of every assessment with headline level, date, and top 3 gaps.
- Never commit secrets; redact tokens in citations.
- **Engine agnosticism:** do not add customer product names, private repo URLs, or real issue keys to files under `framework/`, `skills/`, `rules/`, `scripts/`, or `templates/`.

Procedural how-to: skills `maturity-assess`, `maturity-interview`, `maturity-report`, `maturity-presentation` (canonical: `skills/`; provider adapters synced via `scripts/sync_adapters.sh`).
