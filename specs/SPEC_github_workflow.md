# SPEC: .github/workflows/daily_scrape.yml

## Purpose
Run the scraper daily, commit updated state and the digest back to the repo.

## Triggers
- `schedule: cron "0 6 * * *"` (06:00 UTC daily; note GitHub cron can lag 10-30 min, fine for this)
- `workflow_dispatch` (manual runs while developing)

## Steps
1. Checkout (`actions/checkout@v7`, with `fetch-depth: 1`).
2. Setup Python 3.11 with pip cache (`actions/setup-python@v7`). Both actions are pinned to
   their latest major tag; bump when a new major ships, rather than staying on an old major
   after it starts printing deprecation warnings (e.g. the Node 20 runtime warning seen on
   `checkout@v4` / `setup-python@v5`).
3. `pip install -r requirements.txt`
4. `python main.py --validate` (fail fast on broken config)
5. `python main.py`
6. Commit and push if changed:
   - `data/jobs_seen.csv`
   - `data/digests/*.md`
   - `data/scraper_health.csv`
   - Commit message: `scrape: {date} ({N} new jobs)` where N is read from a `NEW_JOBS_COUNT` file main.py writes to DATA_DIR (simplest handoff, count is the filtered/digest-eligible count per `SPEC_main.md`, not the raw pre-filter count).
   - Detect "nothing changed" explicitly with `git diff --cached --quiet` and
     `exit 0`. Do **not** guard `git commit` with `|| true`: once the
     no-op case is handled explicitly, the only thing that guard can still hide
     is a genuine failure. See "Failure visibility" below.
   - `git push` is retried up to 3 times: on rejection, `git fetch origin main` then
     `git rebase origin/main` before retrying. The full run takes 30+ minutes, so a
     manual push to `main` mid-run is a real race (it happened on the first run),
     not a hypothetical worth ignoring. A genuine rebase conflict still aborts the
     script under Actions' default `bash -e`, which is correct: that failure is real
     and must stay red.
   - Stage `data/digests/` as a directory, not a `*.md` glob. An unmatched glob
     aborts the step under Actions' default `bash -e` on days with no new digest.

## Permissions
- `permissions: contents: write` in the workflow (required for the bot commit).
- No secrets needed for v1. `SLACK_WEBHOOK` secret only if/when that channel is enabled in notify.py.

## Failure visibility
- Exit code 2 from main.py (systemic breakage, >50 percent companies failing) makes the run red. GitHub emails on workflow failure by default: that is the alerting.
- Exit code 0 with a few failed companies stays green; failures are visible in scraper_health.csv.
- A failure in the commit-and-push step makes the run red. This is deliberate. The
  alerting model here is "GitHub emails on red", so any step that silently succeeds
  while doing nothing defeats it: the repo would look healthy while producing no
  digest, and nobody finds out until they notice the absence. Prefer a false red
  over a false green.

## Concurrency
`concurrency: group: scrape, cancel-in-progress: false` to prevent overlapping manual + scheduled runs corrupting the commit step.
