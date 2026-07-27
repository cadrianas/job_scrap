# SPEC: main.py

## Purpose
Orchestrator. Loads config, dispatches each company to the right scraper, dedupes, filters, notifies, updates state.

## Flow
1. `paths.ensure_dirs()`
2. Load and validate `companies.json` into `list[Company]` (skip `enabled: false`). Loading/parsing lives in `main.py` itself; there is no separate config-loader module.
3. Load seen-set from `dedup.load_seen()`.
4. For each enabled company (sorted by tier, then name):
   a. Dispatch to adapter via registry dict: `{"greenhouse": greenhouse.fetch_jobs, "lever": lever.fetch_jobs, "workday": workday.fetch_jobs, "eightfold": eightfold.fetch_jobs, "generic": generic.fetch_jobs}`. All five adapters are now implemented (Phase 1-3 complete). A company whose `ats` is `"unknown"` (or any value outside the five) is still *skipped* with a logged warning -- same treatment as an invalid `ats` value per `SPEC_companies_json.md`. Skipped companies are not scraped, not counted as failures, and excluded from the 50%-failure calculation for exit code 2 (that calculation only considers companies whose adapter was actually attempted).
   b. Catch `ScraperError` and any unexpected exception: log, increment failure count in health tracker, continue.
   c. Sleep `SLEEP_BETWEEN_COMPANIES_SECONDS` between companies whose adapter was actually attempted (no sleep for skipped companies).
5. Flatten results from successful companies, run `dedup.find_new(jobs, seen)`.
6. Run `filters.apply(new_jobs, companies_by_name)` (now a real filter/sort per `SPEC_filters.md`, not an identity function).
7. `notify.write_digest(filtered_jobs, companies_by_name)` and `notify.print_summary(...)`.
8. Unless `--dry-run`: `dedup.update_seen(all_scraped_jobs, seen)` and `health.update_health(results, health_state)`, where `all_scraped_jobs` is every job from every successful company this run (not just the new ones), matching `dedup.py`'s contract. Also writes `NEW_JOBS_COUNT_FILE` with the count of new jobs this run, as a simple handoff to the GitHub Actions commit step (`SPEC_github_workflow.md`) for its commit message -- skipped on `--dry-run` along with the rest of state writing.

## CLI
- `python main.py` : full run
- `python main.py --companies Oura,Bolt` : only listed companies
- `python main.py --dry-run` : scrape and report but do not write state (no CSV append, no digest)
- `python main.py --validate` : validate companies.json and exit

## Logging
- `logging` to stderr and to `LOGS_DIR / f"run_{date}.log"`.
- Per-company one line: name, adapter, job count or error.
- Final summary: companies scraped, failed, total jobs, new jobs.

## Exit codes
- 0: success (even with some company failures)
- 1: config invalid or catastrophic failure (cannot load companies, cannot write state)
- 2: more than 50 percent of companies failed (signals systemic breakage, makes the Actions run red so it is noticed)

## Rules
- All paths via `config.paths`. No path literals.
- Never crash on a single company failure.
