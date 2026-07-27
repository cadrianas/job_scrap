# SPEC: .github/workflows/daily_scrape.yml

## Purpose
Run the scraper daily, commit updated state and the digest back to the repo.

## Triggers
- `schedule: cron "0 6 * * *"` (06:00 UTC daily; note GitHub cron can lag 10-30 min, fine for this)
- `workflow_dispatch` (manual runs while developing)

## Steps
1. Checkout (with `fetch-depth: 1`).
2. Setup Python 3.11 with pip cache.
3. `pip install -r requirements.txt`
4. `python main.py --validate` (fail fast on broken config)
5. `python main.py`
6. Commit and push if changed:
   - `data/jobs_seen.csv`
   - `data/digests/*.md`
   - `data/scraper_health.csv`
   - Commit message: `scrape: {date} ({N} new jobs)` where N is read from a `NEW_JOBS_COUNT` file main.py writes to DATA_DIR (simplest handoff).
   - Use `|| true` guard so "nothing changed" does not fail the job.

## Permissions
- `permissions: contents: write` in the workflow (required for the bot commit).
- No secrets needed for v1. `SLACK_WEBHOOK` secret only if/when that channel is enabled in notify.py.

## Failure visibility
- Exit code 2 from main.py (systemic breakage, >50 percent companies failing) makes the run red. GitHub emails on workflow failure by default: that is the alerting.
- Exit code 0 with a few failed companies stays green; failures are visible in scraper_health.csv.

## Concurrency
`concurrency: group: scrape, cancel-in-progress: false` to prevent overlapping manual + scheduled runs corrupting the commit step.
