"""Adapter for companies hosted on Greenhouse.

Greenhouse exposes a public, unauthenticated JSON API, so this needs
nothing but requests. One HTTP call per company, no pagination.
"""

import logging
import time
from datetime import date

import requests

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

logger = logging.getLogger(__name__)

_BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"


def fetch_jobs(company: Company) -> list[Job]:
    url = _BOARD_URL.format(token=company.identifier)
    payload = _get_json(company, url)

    if not isinstance(payload, dict) or "jobs" not in payload:
        raise ScraperError(company.name, "response missing 'jobs' key")

    scraped_date = date.today().isoformat()
    return [_to_job(company, entry, scraped_date) for entry in payload["jobs"]]


def _get_json(company: Company, url: str) -> dict:
    headers = {"User-Agent": USER_AGENT}
    last_error: str = "unknown error"

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            last_error = f"request failed: {exc}"
        else:
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as exc:
                    raise ScraperError(company.name, f"JSON decode failure: {exc}") from exc
            if response.status_code == 404:
                raise ScraperError(
                    company.name,
                    f"HTTP 404 from {url} -- likely wrong Greenhouse board token "
                    f"'{company.identifier}'",
                )
            last_error = f"HTTP {response.status_code} from {url}"

        if attempt < MAX_RETRIES:
            time.sleep(2**attempt)

    raise ScraperError(company.name, f"failed after {MAX_RETRIES + 1} attempts: {last_error}")


def _to_job(company: Company, entry: dict, scraped_date: str) -> Job:
    location = entry.get("location") or {}
    posted_date = _date_only(entry.get("first_published")) or _date_only(entry.get("updated_at"))
    return Job(
        company=company.name,
        title=entry.get("title", ""),
        location=location.get("name") or "",
        url=entry.get("absolute_url", ""),
        job_id=str(entry.get("id", "")),
        posted_date=posted_date,
        scraped_date=scraped_date,
    )


def _date_only(value: str | None) -> str:
    return value[:10] if value else ""
