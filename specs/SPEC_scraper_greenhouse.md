# SPEC: scrapers/greenhouse.py

## Purpose
Adapter for companies hosted on Greenhouse. Easiest adapter: Greenhouse exposes a public, documented, unauthenticated JSON API. Build this one first.

## Endpoint
`GET https://boards-api.greenhouse.io/v1/boards/{identifier}/jobs`

where `identifier` is the board token from companies.json (e.g. `ouraring`).

Optional `?content=true` returns full descriptions; NOT used in v1 (we only need titles/links, and the payload is 10x larger).

## Response shape (relevant fields)
```json
{
  "jobs": [
    {
      "id": 4285367005,
      "title": "Senior Data Scientist",
      "updated_at": "2026-07-08T11:22:33-04:00",
      "location": {"name": "Helsinki, Finland"},
      "absolute_url": "https://boards.greenhouse.io/ouraring/jobs/4285367005"
    }
  ],
  "meta": {"total": 42}
}
```

## Mapping to Job
- `job_id` = str(id)
- `title` = title
- `location` = location.name or ""
- `url` = absolute_url
- `posted_date` = date part of `first_published` if present, else date part of `updated_at`, else ""

## Errors -> ScraperError
- Non-200 status after MAX_RETRIES (404 usually means wrong board token; include that hint in the message)
- Response missing `jobs` key
- JSON decode failure

## Rules
- `requests` with `USER_AGENT` and `REQUEST_TIMEOUT_SECONDS` from paths.py.
- One HTTP request per company. No pagination needed (endpoint returns all jobs).
- Public function: `fetch_jobs(company: Company) -> list[Job]`. Nothing else public.

## Test companies for development
Oura (`ouraring`), plus verify 2-3 more tokens by loading `boards.greenhouse.io/<token>` in a browser before adding to companies.json.
