# SPEC: scrapers/json_boards.py

## Purpose
Adapter for five vendor-hosted job board APIs that are each too small to justify their own
module: Ashby, SmartRecruiters, Workable, Breezy HR, BambooHR. All five are public,
unauthenticated JSON endpoints, so no browser automation is needed for any of them.

## Why one file for five vendors
This bends `PLAN.md` design principle 2 ("each ATS adapter is an independent module"), same
tradeoff `scrapers/academic.py` already made and documented in `SPEC_scraper_academic.md`. The
five vendors here differ only in URL template, pagination, and field names -- five near-empty
files would be pure boilerplate. `company.ats` selects which vendor's logic runs; the file still
exposes exactly one public `fetch_jobs`, per the adapter contract in `SPEC_models.md`.

## Verification before coding
Every URL pattern, response shape, and pagination behavior below was confirmed live on
2026-07-28 against real companies already found during Phase 1 triage (`RESEARCH_NOTES_companies.md`),
not copied from vendor docs. In particular: SmartRecruiters and Workable both return HTTP 200
with an empty result for a nonexistent slug -- a bare 200 does not confirm a company id is
correct. Any new `companies.json` entry for these two vendors must be confirmed by real job
content (or, if a company genuinely has zero current openings, an independent check such as the
vendor's own public careers page) before being enabled, not by status code alone.

## Vendors

### Ashby -- `ats: "ashby"`
- `GET https://api.ashbyhq.com/posting-api/job-board/{slug}`
- No pagination: the full job list comes back in one call regardless of size (confirmed at 610
  jobs for Airwallex, no cursor/hasMore field in the response).
- Response: `{"jobs": [...], "apiVersion": "..."}`.
- Per posting: `id`, `title`, `location` (plain string, e.g. `"CA - Toronto"`), `jobUrl`,
  `publishedAt` (ISO datetime).
- `identifier` = board slug, e.g. `"cohere"`, `"halter"`.

### SmartRecruiters -- `ats: "smartrecruiters"`
- `GET https://api.smartrecruiters.com/v1/companies/{company_id}/postings?limit=100&offset=N`
- Paginates: `limit` is capped at 100 server-side (a higher `limit` value is silently ignored,
  confirmed by requesting `limit=200` and still getting 100 back). Loop `offset += 100` until
  `totalFound` (from the first response) is reached, cap 500 like the other paginated adapters.
- Response: `{"offset": N, "limit": 100, "totalFound": N, "content": [...]}`.
- Per posting: `id`, `name` (title), `location.fullLocation`, `releasedDate` (ISO datetime). No
  apply URL in the postings payload; construct it as
  `https://jobs.smartrecruiters.com/{company_id}/{id}` (confirmed 200, live).
- `identifier` = the company id exactly as it appears in that URL, case-sensitive as observed
  (e.g. `"canva"`, `"Getaround"` -- SmartRecruiters itself is case-insensitive, but store the
  exact form that was verified with real content).

### Workable -- `ats: "workable"`
- `GET https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true`
- No pagination: full list in one call (confirmed at 54 jobs for Nuvei, no next-page field).
- Response: `{"name": "...", "description": ..., "jobs": [...]}`. The `name` field is the
  confirmation signal referenced above -- if it doesn't match the real company, the slug is
  wrong even though the request itself returned 200.
- Per posting: `shortcode` (job id), `title`, `url`, `city`/`country`/`state` (combine into
  location, comma-joined, skipping empties), `published_on` (already `YYYY-MM-DD`).
- `identifier` = account slug, e.g. `"nuvei"`.

### Breezy HR -- `ats: "breezyhr"`
- `GET https://{slug}.breezy.hr/json`
- No pagination: response is a bare JSON array of all postings, not wrapped in an object.
- Per posting: `id`, `name` (title), `url`, `location.name` (already a combined string like
  `"Auckland, NZ"`), `published_date` (ISO datetime).
- `identifier` = subdomain slug, e.g. `"serato-limited"`.

### BambooHR -- `ats: "bamboohr"`
- `GET https://{slug}.bamboohr.com/careers/list`
- No pagination: response is `{"meta": {"totalCount": N}, "result": [...]}` with the full list
  in `result`.
- Per posting: `id`, `jobOpeningName` (title), `location.city`/`location.state` (combine,
  comma-joined, skipping empties). **No URL or date field in the response at all** -- construct
  the URL as `https://{slug}.bamboohr.com/careers/{id}` (confirmed 200, live); `posted_date` is
  always `""` for this vendor.
- `identifier` = subdomain slug, e.g. `"gentrack"`.

## Request details (all five)
- Method: GET for all five (no POST, unlike Workday).
- Standard `USER_AGENT`, `REQUEST_TIMEOUT_SECONDS`, `MAX_RETRIES` from `config/paths.py`, same
  retry-with-backoff helper pattern as every other adapter.
- Sleep 0.5s between pagination pages for SmartRecruiters, matching `workday.py`'s convention.
  The other four vendors make exactly one request per company, so no inter-page sleep applies.

## Mapping to Job
Company-specific field names are listed per vendor above. Common rules:
- `job_id`: the vendor's own posting id, stringified. None of the five need a hash fallback --
  all five always provide a stable id.
- `posted_date`: parse to ISO date where the vendor provides one; `""` where it doesn't
  (BambooHR) or where parsing fails.
- `location`: `""` if the vendor provides no location data for a posting, never omit the field.

## Errors -> ScraperError
Same contract as every other adapter:
- Non-200 after retries, or a response that doesn't parse as JSON.
- SmartRecruiters and Workable: a 200 response is not sufficient on its own (see "Verification"
  above), but that check happens at registry-entry time, not at scrape time -- the adapter does
  not attempt to detect a wrong-but-live slug at runtime, since a genuinely correct slug with
  zero current postings looks identical to a wrong slug with zero postings from the adapter's
  point of view. Getting the slug right is a companies.json data-quality problem, not something
  the adapter can resolve per Hard Rule 4 (never let one company kill the run -- but also never
  guess).
- More than 3 consecutive failed pagination pages (SmartRecruiters only).

## companies.json integration
```json
{"name": "Cohere", "ats": "ashby", "identifier": "cohere", "regions": ["toronto", "canada"], "tier": 1, "enabled": true},
{"name": "Canva", "ats": "smartrecruiters", "identifier": "canva", "regions": ["sydney", "australia"], "tier": 1, "enabled": true},
{"name": "Nuvei", "ats": "workable", "identifier": "nuvei", "regions": ["montreal", "canada"], "tier": 2, "enabled": true},
{"name": "Serato", "ats": "breezyhr", "identifier": "serato-limited", "regions": ["auckland", "new zealand"], "tier": 2, "enabled": true},
{"name": "Gentrack", "ats": "bamboohr", "identifier": "gentrack", "regions": ["auckland", "new zealand"], "tier": 2, "enabled": true}
```
The adapter registry in `main.py` maps all five `ats` strings to `json_boards.fetch_jobs`, same
pattern as `academic.py`'s `euraxess`/`jobindex` entries both pointing at `academic.fetch_jobs`.
