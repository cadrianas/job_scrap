# SPEC: dedup.py

## Purpose
Track which jobs have already been seen across runs so daily digests only contain genuinely new postings.

## State file
`JOBS_SEEN_FILE` (from paths.py), CSV with header:
`dedup_key,company,title,url,first_seen,last_seen`

- `first_seen`: date the job first appeared
- `last_seen`: date the job most recently appeared (updated every run it still exists; lets you detect removed/filled postings later)

## API
- `load_seen() -> dict[str, dict]` : dedup_key -> row. Returns empty dict if file missing (first run).
- `find_new(jobs: list[Job], seen: dict) -> list[Job]` : jobs whose `dedup_key` is not in seen.
- `update_seen(all_scraped: list[Job], seen: dict) -> None` : add new keys with first_seen=today, bump last_seen=today for every key scraped today, then write the whole file atomically (write temp file in DATA_DIR, then rename).

## Rules
- Atomic writes only. A killed Actions run must not corrupt the CSV.
- Never delete rows in v1 (history is cheap and useful; a job disappearing and reappearing should not re-alert... its key is still present).
- File stays sorted by dedup_key for clean git diffs.

## Edge cases
- Same job posted in multiple locations: Greenhouse/Lever give distinct job IDs per posting, so they are treated as distinct. Acceptable.
- ATS migration (company moves Greenhouse -> Workday): job_ids change, everything re-alerts once. Acceptable, self-heals after one run.
