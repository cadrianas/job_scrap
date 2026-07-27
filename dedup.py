"""Tracks which jobs have already been seen across runs, so daily digests
only contain genuinely new postings. State lives in JOBS_SEEN_FILE (CSV,
committed to git); rows are never deleted, only added or refreshed.
"""

import csv
import os
from datetime import date

from config.paths import DATA_DIR, JOBS_SEEN_FILE
from models import Job

_FIELDNAMES = ["dedup_key", "company", "title", "url", "first_seen", "last_seen"]


def load_seen() -> dict[str, dict]:
    """Returns dedup_key -> row. Empty dict if the file doesn't exist yet."""
    if not JOBS_SEEN_FILE.exists():
        return {}
    with JOBS_SEEN_FILE.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["dedup_key"]: row for row in reader}


def find_new(jobs: list[Job], seen: dict) -> list[Job]:
    """Jobs whose dedup_key is not already in seen."""
    return [job for job in jobs if job.dedup_key not in seen]


def update_seen(all_scraped: list[Job], seen: dict) -> None:
    """Merges today's scraped jobs into seen and writes the whole file.

    New keys get first_seen = last_seen = today. Keys that already existed
    keep their original first_seen and get last_seen bumped to today.
    Rows for keys not scraped today are left untouched, never deleted.
    """
    today = date.today().isoformat()

    for job in all_scraped:
        existing = seen.get(job.dedup_key)
        if existing is None:
            seen[job.dedup_key] = {
                "dedup_key": job.dedup_key,
                "company": job.company,
                "title": job.title,
                "url": job.url,
                "first_seen": today,
                "last_seen": today,
            }
        else:
            existing["company"] = job.company
            existing["title"] = job.title
            existing["url"] = job.url
            existing["last_seen"] = today

    _write_atomic(seen)


def _write_atomic(seen: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = DATA_DIR / f"{JOBS_SEEN_FILE.name}.tmp"

    rows = sorted(seen.values(), key=lambda row: row["dedup_key"])

    with tmp_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    os.replace(tmp_path, JOBS_SEEN_FILE)
