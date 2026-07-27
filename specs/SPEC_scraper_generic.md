# SPEC: scrapers/generic.py

## Purpose
Last-resort adapter for companies with plain HTML careers pages and no known ATS API (e.g. Bolt's custom careers site). Deliberately dumb and low-maintenance.

## Approach
1. GET the URL in `identifier` (respect robots.txt: fetch `/robots.txt` once per domain per run, skip company with a logged warning if the careers path is disallowed).
2. Parse with BeautifulSoup.
3. Collect all `<a>` tags whose href OR text suggests a job posting:
   - href contains any of: `/job/`, `/jobs/`, `/careers/`, `/position/`, `/opening/`, `/vacanc`
   - AND link text is 4+ characters and not purely navigational (exclude: "careers", "jobs", "open positions", "apply", "learn more" as full text)
4. Build Jobs:
   - `title` = link text (stripped)
   - `url` = absolute href (urljoin with page URL)
   - `job_id` = sha1(url)
   - `location` = "" (generic adapter does not attempt location extraction in v1)
   - `posted_date` = ""

## Known limitations (accepted)
- JS-rendered pages return nothing: log a warning "0 jobs from generic adapter, page may need a dedicated adapter" so it is visible, then move on. The fix is writing a dedicated adapter or finding the underlying JSON call, never adding Selenium.
- Some noise links will slip through; dedup makes each one a one-time annoyance and title filtering (Phase 4) hides most.

## Errors -> ScraperError
- Non-200 after retries
- Empty HTML body

Note: zero extracted jobs is NOT an error (real signal, logged as warning).

## Rules
- BeautifulSoup with `html.parser` (no lxml dependency).
- Public function: `fetch_jobs(company: Company) -> list[Job]`.
- Per-domain robots.txt cache lives inside this module for the run.
