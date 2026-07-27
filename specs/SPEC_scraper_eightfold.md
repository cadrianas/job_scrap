# SPEC: scrapers/eightfold.py

## Purpose
Adapter for Eightfold-hosted careers sites (used by e.g. some large European enterprises). Undocumented but stable JSON API behind the careers page.

## How Eightfold careers sites work
Careers pages live at a company domain, e.g. `https://careers.{company}.com` or `https://apply.{company}.com`, powered by Eightfold. The page calls:

`GET https://{careers_domain}/api/apply/v2/jobs?domain={company_domain}&start=0&num=10&sort_by=timestamp`

## Identifier convention
companies.json stores `identifier` as the careers domain (e.g. `careers.company.com`). The `domain` query param is derived by stripping the first subdomain label (`careers.company.com` -> `company.com`); if that guess 404s or returns zero jobs unexpectedly, retry with the identifier itself as `domain`.

**Confirmed exception (found while testing against Netflix):** some Eightfold deployments use a `domain` value that isn't derivable from the careers host by any string manipulation at all -- Netflix's careers host is `explore.jobs.netflix.net` but the working `domain` param is `netflix.com`, an unrelated apex domain. Neither guess above can produce that. For these, `identifier` may instead be written as `"{careers_domain}|{explicit_domain_param}"` (pipe-separated) to skip guessing entirely and use the explicit value. Only use this form after confirming the real `domain` value in browser devtools; don't guess a pipe value speculatively.

## Request details
- `num` max is typically 100; use `num=100`, paginate with `start += 100` until `count` reached, cap 500.
- `sort_by=timestamp` gives newest first, which matters for the apply-fast goal.
- Standard USER_AGENT and timeout from paths.py.

## Response shape (relevant fields)
```json
{
  "count": 231,
  "positions": [
    {
      "id": 563812,
      "name": "Data Scientist, Supply Chain",
      "location": "Gothenburg, Sweden",
      "t_create": 1751971200,
      "canonicalPositionUrl": "https://careers.company.com/careers/job/563812"
    }
  ]
}
```

## Mapping to Job
- `job_id` = str(id)
- `title` = name
- `location` = location or ""
- `url` = canonicalPositionUrl; if absent, `https://{identifier}/careers?pid={id}`
- `posted_date` = `t_create` (epoch seconds) to ISO date, else ""

## Errors -> ScraperError
- Non-200 after retries on both domain guesses
- Missing `positions` key / JSON decode failure

## Rules
- One file owns all Eightfold specifics.
- Public function: `fetch_jobs(company: Company) -> list[Job]`.

## Test companies for development
Confirm the `/api/apply/v2/jobs` endpoint in browser devtools for each Eightfold company before adding it to companies.json; Eightfold deployments vary more than Greenhouse/Lever.
