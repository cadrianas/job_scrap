# SPEC: config/paths.py

## Purpose
Single source of truth for every filesystem path and global setting. Eliminates hardcoded paths across the codebase.

## Requirements
- Derive everything from `ROOT = Path(__file__).resolve().parent.parent` so the repo is location-independent (laptop, CI runner, container).
- Expose as module-level constants (typed `Path` objects):
  - `ROOT`, `CONFIG_DIR`, `DATA_DIR`, `SCRAPERS_DIR`, `LOGS_DIR`, `DIGESTS_DIR`
  - `COMPANIES_FILE`, `JOBS_SEEN_FILE`, `HEALTH_FILE`
- Expose global settings: `USER_AGENT`, `REQUEST_TIMEOUT_SECONDS`, `SLEEP_BETWEEN_COMPANIES_SECONDS`, `MAX_RETRIES`.
- Provide `ensure_dirs()` which creates `DATA_DIR`, `LOGS_DIR`, `DIGESTS_DIR` idempotently. `main.py` calls it once at startup.

## Non-requirements
- No environment-variable overrides in v1 (can be added later if a path must differ in CI).
- No reading of external config files. This module has zero imports beyond `pathlib`.

## Acceptance
- `python -c "from config.paths import ROOT; print(ROOT)"` prints the repo root from any working directory.
- Grep of the codebase for `"data/"`, `"config/"`, `Path(` outside this file returns no path literals (imports only).
