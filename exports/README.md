# Tracked Metis scorecard exports

Machine assessments live under `projects/<slug>/assessments/` (often gitignored).
Factory hosts (DigitalOcean Kairos/Hephaestus) and Pantheon `/metis` sync **must**
consume these committed snapshots — not invent Shapiro levels.

```bash
python3 scripts/export_scorecard.py --slug pantheon-qa
# → exports/pantheon-qa/latest.json
```

Fetch without a local checkout:

```bash
curl -fsSL https://raw.githubusercontent.com/<org>/maturity-agent/<branch>/exports/<slug>/latest.json
```
