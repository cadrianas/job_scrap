# SPEC: health.py

## Purpose
Tracks per-company consecutive failure counts across runs, so a persistently
broken adapter/company is visible without ever breaking the run itself.
Referenced by `main.py` (step 8: `health.write(...)`) but was not fully
specified alongside it; this fills that gap before the code is written, per
the project's spec-first rule.

## State file
`HEALTH_FILE` (from paths.py), CSV with header:
`company,consecutive_failures,last_status,last_run`

- `last_status`: `ok` or `failed` for the most recent run that attempted this company
- `last_run`: ISO date of that attempt

## API
- `load_health() -> dict[str, dict]` : company name -> row. Empty dict if file missing.
- `update_health(results: dict[str, bool], health: dict) -> None`
  - `results` maps company name -> success (`True`) or failure (`False`) for companies whose adapter was actually attempted this run (skipped companies, e.g. an unimplemented `ats`, are not included).
  - On success: `consecutive_failures` resets to 0, `last_status = "ok"`.
  - On failure: `consecutive_failures` increments by 1, `last_status = "failed"`.
  - Companies not in `results` (not attempted this run) are left untouched.
  - Writes the whole file atomically (temp file in `DATA_DIR`, then rename), sorted by company name.

## Rules
- Never used to stop a company from being scraped again; it's observability only, read by a human, not the pipeline.
- Atomic writes, same pattern as `dedup.py`.
