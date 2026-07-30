# SPEC: scrapers/icims.py

## Purpose
Adapter for companies hosted on iCIMS career portals (e.g. Booking.com, enterprise employers).

## Endpoint & Format
iCIMS portals accept requests at:
`https://{identifier}.icims.com/jobs/search?in_iframe=1&pr={page}`

where `identifier` is the tenant name from companies.json (e.g. `careers-booking`).

The endpoint returns HTML containing `.iCIMS_JobsTable` or JSON metadata listing available roles.

## Mapping to Job
- `job_id`: Extracted from job URL regex `/jobs/(\d+)/`
- `title`: Job posting link text or `data-title` attribute
- `location`: Location text from `.iCIMS_JobHeader` or `data-location`
- `url`: `https://{identifier}.icims.com/jobs/{job_id}/job`
- `posted_date`: Extracted ISO date if present, else ""

## Errors -> ScraperError
- Non-200 status after retries (404/403)
- Parse error or missing job table structure

## Rules
- Uses `requests` with standard `USER_AGENT` and timeout from `config/paths.py`.
- Exposes exactly one public function: `fetch_jobs(company: Company) -> list[Job]`.
