# CLAUDE.md

Instructions for AI-assisted development on this repository.

## Project

Daily job scraper for data science / quant / analytics roles across Europe, Canada, the USA, Australia, and New Zealand. Runs on GitHub Actions, scrapes company career pages across multiple ATS platforms, deduplicates, and produces a digest of new postings. See `PLAN.md` for the phased plan and `specs/` for per-script specifications.

## Hard Rules

1. **Never hardcode paths.** Every file path in every script must come from `config/paths.py`. If a new path is needed, add it to `config/paths.py` first, then import it. No exceptions, including in tests and one-off scripts.

2. **Spec first.** Before writing or significantly changing a script, read its spec in `specs/`. If the change contradicts the spec, update the spec in the same commit.

3. **Adapter contract.** Every scraper in `scrapers/` must expose exactly one public function:
   `fetch_jobs(company: Company) -> list[Job]`
   It must raise `ScraperError` on failure and never return partial silent garbage. See `specs/SPEC_models.md`.

4. **Never let one company kill the run.** All per-company exceptions are caught in `main.py`, logged, and counted. Scrapers themselves should raise, not swallow.

5. **No browser automation unless a spec says so.** Prefer the JSON endpoints documented in the scraper specs. Selenium/Playwright is a last resort and currently used nowhere.

6. **State is CSV in `data/`, committed to git.** Do not introduce databases, pickles, or external storage.

7. **Rate limiting is mandatory.** Respect the sleep interval defined in `config/paths.py` (SETTINGS section). Custom User-Agent required on all requests.

8. **Python 3.11+, stdlib-first.** Allowed third-party deps: `requests`, `beautifulsoup4`. Ask before adding anything else.

## Style

- Type hints on all public functions.
- Dataclasses over dicts for structured data.
- `logging` module, never `print`, except in `main.py` final summary.
- No em dashes in any user-facing text, digests, or documentation.

## Where things live

- Paths: `config/paths.py` (the ONLY place)
- Company registry: `config/companies.json`
- Runtime data: `data/` (gitignored except `jobs_seen.csv`, `digests/*.md`, and `scraper_health.csv` -- the last is committed deliberately per `specs/SPEC_github_workflow.md` so per-company failures are visible in the repo, not just in CI logs)
- Specs: `specs/SPEC_<module>.md`

## Testing a change

Run `python main.py --companies <name>` to scrape a single company without touching state (see `specs/SPEC_main.md` for the dry-run flag).
