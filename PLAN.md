# Job Scraper: Project Plan

## Goal

A Python job scraper that runs daily via GitHub Actions, checks ~150-200 company career pages across Europe, Canada, the USA, Australia, and New Zealand, spanning multiple ATS platforms (Greenhouse, Lever, Workday, Eightfold, plus a generic fallback), deduplicates against previous runs, and surfaces new postings matching data science / quant / analytics roles.

## Design Principles

1. No hardcoded paths anywhere. All paths come from `config/paths.py`.
2. Each ATS adapter is an independent module with an identical interface, so adding a new ATS is a one-file change.
3. Fail per-company, never per-run. One broken site must not kill the daily job.
4. State lives in the repo (CSV committed by the Actions bot). No external database.
5. Config-driven: adding a company means editing `companies.json`, not code.

## Phases

### Phase 1: Skeleton and easy wins (target: first working run)
- `config/paths.py` (central path definitions)
- `config/companies.json` with an initial 20-30 companies, biased toward Greenhouse and Lever (both have public, stable JSON APIs and need no browser automation)
- `models.py` (the Job dataclass, shared by everything)
- `scrapers/greenhouse.py` and `scrapers/lever.py`
- `dedup.py` and `main.py`
- Output: new jobs printed to console and appended to CSV
- Milestone: run locally, see real jobs from ~25 companies

### Phase 2: Automation
- `.github/workflows/daily_scrape.yml` (cron at 06:00 UTC + manual dispatch)
- `notify.py` (start with a GitHub-committed Markdown digest file, e.g. `new_jobs_YYYY-MM-DD.md`; add email or Slack webhook later if wanted)
- Commit-back step for `jobs_seen.csv`
- Milestone: wake up to a fresh digest in the repo

### Phase 3: Harder ATS platforms
- `scrapers/workday.py` (uses Workday's internal JSON endpoint `/wday/cxs/...`; no browser needed if the endpoint is discovered per company, which the spec covers)
- `scrapers/eightfold.py` (public careers API, JSON)
- `scrapers/generic.py` (BeautifulSoup fallback for plain HTML careers pages)
- Expand `companies.json` toward the full list
- Milestone: full company list covered

### Phase 3b: Academic and math job boards
- `scrapers/academic.py`: jobs.ac.uk (RSS), Jobbnorge (Norwegian universities), EURAXESS (EU-wide), MathJobs, academicpositions.com, Academic Jobs Online (global, strong in North America), HigherEdJobs and HERC (USA), University Affairs and CAUT (Canada)
- `scrapers/varbi.py`: Swedish universities (KI, KTH, Uppsala, Gothenburg, Umea) via their uniform Varbi subdomains
- Universities are covered via aggregators, never scraped individually
- Australia/New Zealand academic aggregators are not yet identified with confidence; treat as a follow-up research item rather than guessing at URLs
- See `specs/SPEC_scraper_academic.md`
- Milestone: postdoc and academic postings flow through the same pipeline as industry jobs

### Phase 4: Filtering and quality of life
- `filters.py`: keyword include/exclude lists scoped to four target role families (data science, data analytics, mathematical/quantitative modelling, mathematical epidemiology and public health modelling), strict mode by default so the digest only surfaces matching roles; region tags across all five target regions (Europe, Canada, USA, Australia, New Zealand) treated as equal priority
- Posting-date tracking to flag jobs less than 48 hours old (apply-fast advantage)
- Per-company health report (`health.py`): consecutive failure counts, so dead adapters are visible
- `board.py`: persistent, regenerable "apply board" (HTML + CSV) of every matching job in `jobs_seen.csv`, so a posting doesn't get lost once it scrolls off a daily digest -- see `specs/SPEC_board.md`

## What we are explicitly NOT building (for now)

- Auto-apply functionality
- LinkedIn scraping (against ToS, brittle; revisit only as manual fallback)
- A database (CSV in git is enough at this scale)
- A web UI

## Rate limiting and etiquette

- 1-2 second sleep between companies
- Custom User-Agent identifying the tool
- Respect robots.txt for generic HTML scraping (Greenhouse/Lever/Eightfold public APIs are intended for this use)
- Retry once with backoff on 5xx, skip on repeated failure

## File Map

```
job-scraper/
├── CLAUDE.md                      # instructions for AI-assisted development
├── PLAN.md                        # this file
├── config/
│   ├── paths.py                   # ALL paths defined here
│   └── companies.json             # company registry
├── specs/                         # one spec per script, written before code
│   ├── SPEC_paths.md
│   ├── SPEC_models.md
│   ├── SPEC_companies_json.md
│   ├── SPEC_main.md
│   ├── SPEC_dedup.md
│   ├── SPEC_health.md
│   ├── SPEC_notify.md
│   ├── SPEC_filters.md
│   ├── SPEC_board.md
│   ├── SPEC_scraper_greenhouse.md
│   ├── SPEC_scraper_lever.md
│   ├── SPEC_scraper_workday.md
│   ├── SPEC_scraper_eightfold.md
│   ├── SPEC_scraper_generic.md
│   ├── SPEC_scraper_academic.md
│   └── SPEC_github_workflow.md
├── scrapers/                      # greenhouse, lever, workday, eightfold, generic
├── data/                          # jobs_seen.csv, scraper_health.csv, digests/, job_board.html/csv (created at runtime)
├── main.py
├── models.py
├── dedup.py
├── health.py
├── notify.py
├── filters.py
├── board.py
└── requirements.txt
```
