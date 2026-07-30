# SPEC: scrapers/phenom.py

## Purpose
Adapter for companies hosted on Phenom People career portals (e.g. BCG, PwC, Just Eat Takeaway).

## Endpoint & Format
Phenom People portals expose a search endpoint at:
`https://{domain}/refine_search?from={offset}&size=50`

where `identifier` is the domain name from companies.json (e.g. `careers.justeattakeaway.com`).

The endpoint returns JSON structured as:
```json
{
  "refineSearch": {
    "jobGridModel": [
      {
        "jobId": "12345",
        "title": "Senior Data Scientist",
        "city": "Amsterdam",
        "country": "Netherlands",
        "postedDate": "2026-07-20T10:00:00.000Z",
        "applyUrl": "https://careers.justeattakeaway.com/global/en/job/12345"
      }
    ],
    "totalHits": 120
  }
}
```

## Mapping to Job
- `job_id`: str(jobId)
- `title`: title
- `location`: city, country
- `url`: applyUrl or `https://{domain}/job/{jobId}`
- `posted_date`: ISO date string parsed from postedDate

## Errors -> ScraperError
- Non-200 status after retries
- Missing `refineSearch` or `jobGridModel` key in payload

## Rules
- Uses `requests` with standard `USER_AGENT` and timeout from `config/paths.py`.
- Exposes exactly one public function: `fetch_jobs(company: Company) -> list[Job]`.
