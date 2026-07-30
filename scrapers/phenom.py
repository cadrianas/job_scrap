"""Adapter for Phenom People-hosted careers portals.

Phenom portals use a JSON search endpoint at
https://{domain}/refine_search?from={offset}&size=50
"""

from datetime import date, datetime
import requests

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

_PAGE_SIZE = 50
_MAX_JOBS = 1000


def fetch_jobs(company: Company) -> list[Job]:
    domain = company.identifier.strip()
    if domain.startswith("http://") or domain.startswith("https://"):
        base_url = domain.rstrip("/")
    else:
        base_url = f"https://{domain}"

    endpoint = f"{base_url}/refine_search"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    scraped_date = date.today().isoformat()
    jobs: list[Job] = []
    offset = 0

    while offset < _MAX_JOBS:
        params = {"from": offset, "size": _PAGE_SIZE}
        payload = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                res = requests.get(endpoint, params=params, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
                if res.status_code == 200:
                    try:
                        payload = res.json()
                        break
                    except ValueError:
                        pass
            except requests.RequestException:
                pass

        if payload is None:
            if offset == 0:
                raise ScraperError(company.name, f"Failed to fetch Phenom jobs payload from {endpoint}")
            break

        refine = payload.get("refineSearch", {})
        postings = refine.get("jobGridModel", [])
        if not postings and offset == 0:
            raise ScraperError(company.name, "Response missing 'refineSearch.jobGridModel'")

        if not postings:
            break

        for item in postings:
            job_id = str(item.get("jobId", ""))
            title = item.get("title", "")
            city = item.get("city", "")
            country = item.get("country", "")
            location = ", ".join(filter(None, [city, country]))
            url = item.get("applyUrl") or f"{base_url}/job/{job_id}"
            posted_raw = item.get("postedDate", "")
            posted_date = _parse_date(posted_raw)

            if job_id and title:
                jobs.append(
                    Job(
                        company=company.name,
                        title=title,
                        location=location,
                        url=url,
                        job_id=job_id,
                        posted_date=posted_date,
                        scraped_date=scraped_date,
                    )
                )

        offset += len(postings)

    return jobs


def _parse_date(value: str) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.date().isoformat()
    except (ValueError, AttributeError):
        return ""
