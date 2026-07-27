# SPEC: models.py

## Purpose
Shared dataclasses and exceptions used by every module. Defines the adapter contract.

## Contents

### `Company` (frozen dataclass)
Loaded from `companies.json`. Fields:
- `name: str` (unique, human-readable, e.g. "Oura")
- `ats: str` (one of: `greenhouse`, `lever`, `workday`, `eightfold`, `generic`, plus academic sources per `SPEC_scraper_academic.md`)
- `identifier: str` (ATS-specific: Greenhouse board token, Lever site tag, Workday tenant+site, Eightfold domain, or full URL for generic)
- `regions: list[str]` (free tags, e.g. `["helsinki", "nordics"]`)
- `tier: int` (1 = priority, 2 = good fit, 3 = broad net; used for sorting output only)
- `enabled: bool` (default true; lets you park a broken company without deleting it)

### `Job` (frozen dataclass)
The normalized unit every scraper must return. Fields:
- `company: str`
- `title: str`
- `location: str` (best effort, may be "")
- `url: str` (direct application link, required)
- `job_id: str` (ATS-native ID if available, else sha1 of url)
- `posted_date: str` (ISO date if the ATS provides it, else "")
- `scraped_date: str` (ISO date, set by scraper)

Property: `dedup_key` returns `f"{company}:{job_id}"`.

### `ScraperError(Exception)`
Raised by adapters on any failure (HTTP error after retries, unexpected schema, empty response where jobs are expected). Carries `company_name` and a message.

## Rules
- Dataclasses are frozen (immutable) to prevent accidental mutation in the pipeline.
- No ATS-specific fields on `Job`. If an ATS gives extra data, drop it. Normalization is the point.
- `models.py` imports nothing from other project modules (bottom of the dependency graph).

## Acceptance
- Every scraper returns `list[Job]` and nothing else.
- `Job.dedup_key` is stable across runs for the same posting.
