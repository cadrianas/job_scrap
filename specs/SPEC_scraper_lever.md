# SPEC: scrapers/lever.py

## Purpose
Adapter for companies hosted on Lever. Second-easiest: public unauthenticated JSON API.

## Endpoint
`GET https://api.lever.co/v0/postings/{identifier}?mode=json`

where `identifier` is the site tag from companies.json (the `X` in jobs.lever.co/X).

## Response shape (relevant fields)
A JSON array (not wrapped in an object):
```json
[
  {
    "id": "a8d3-...-uuid",
    "text": "Data Analyst, Growth",
    "createdAt": 1751971200000,
    "hostedUrl": "https://jobs.lever.co/company/a8d3-...",
    "categories": {"location": "Stockholm", "team": "Analytics", "commitment": "Full-time"}
  }
]
```

## Mapping to Job
- `job_id` = id
- `title` = text
- `location` = categories.location or ""
- `url` = hostedUrl
- `posted_date` = `createdAt` (epoch milliseconds) converted to ISO date; "" if missing

## Errors -> ScraperError
- Non-200 after retries (404 = wrong site tag, hint in message)
- Response not a JSON list
- JSON decode failure

## Rules
- Same request settings from paths.py as all adapters.
- One request per company, no pagination needed.
- Public function: `fetch_jobs(company: Company) -> list[Job]`.

## Notes
- Some companies use `eu.api.lever.co` for EU-hosted instances. If the main endpoint 404s, retry once against `https://api.lever.co` replaced with `https://api.eu.lever.co` before raising. Cheap fallback, matters for European companies specifically.
