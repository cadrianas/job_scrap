"""Tracks per-company consecutive failure counts across runs. Pure
observability: a human reads HEALTH_FILE to spot a persistently broken
adapter, nothing in the pipeline reads it back.
"""

import csv
import os
from datetime import date

from config.paths import DATA_DIR, HEALTH_FILE

_FIELDNAMES = ["company", "consecutive_failures", "last_status", "last_run"]


def load_health() -> dict[str, dict]:
    if not HEALTH_FILE.exists():
        return {}
    with HEALTH_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["company"]: row for row in reader}


def update_health(results: dict[str, bool], health: dict) -> None:
    today = date.today().isoformat()

    for company_name, success in results.items():
        existing = health.get(company_name)
        prior_failures = int(existing["consecutive_failures"]) if existing else 0
        health[company_name] = {
            "company": company_name,
            "consecutive_failures": 0 if success else prior_failures + 1,
            "last_status": "ok" if success else "failed",
            "last_run": today,
        }

    _write_atomic(health)


def _write_atomic(health: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = DATA_DIR / f"{HEALTH_FILE.name}.tmp"

    rows = sorted(health.values(), key=lambda row: row["company"])

    with tmp_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    os.replace(tmp_path, HEALTH_FILE)
