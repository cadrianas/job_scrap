"""Adapter for companies hosted on Lever.

Public, unauthenticated JSON API. One HTTP call per company, no
pagination. Some companies run EU-hosted Lever instances under a
separate domain; if the main endpoint 404s, that domain is tried once
before giving up.
"""

import time
from datetime import date, datetime, timezone

import requests

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

_POSTINGS_URL = "https://api.lever.co/v0/postings/{site}?mode=json"
_EU_POSTINGS_URL = "https://api.eu.lever.co/v0/postings/{site}?mode=json"


class _NotFound(Exception):
    """Internal signal: a 404 was hit, distinct from other failures."""


def fetch_jobs(company: Company) -> list[Job]:
    url = _POSTINGS_URL.format(site=company.identifier)
    try:
        payload = _get_json(company, url)
    except _NotFound:
        eu_url = _EU_POSTINGS_URL.format(site=company.identifier)
        try:
            payload = _get_json(company, eu_url)
        except _NotFound:
            raise ScraperError(
                company.name,
                f"HTTP 404 from both {url} and {eu_url} -- likely wrong Lever site tag "
                f"'{company.identifier}'",
            ) from None

    if not isinstance(payload, list):
        raise ScraperError(company.name, "response is not a JSON list")

    scraped_date = date.today().isoformat()
    return [_to_job(company, entry, scraped_date) for entry in payload]


def _get_json(company: Company, url: str):
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
                raise _NotFound(url)
            last_error = f"HTTP {response.status_code} from {url}"

        if attempt < MAX_RETRIES:
            time.sleep(2**attempt)

    raise ScraperError(company.name, f"failed after {MAX_RETRIES + 1} attempts: {last_error}")


def _to_job(company: Company, entry: dict, scraped_date: str) -> Job:
    categories = entry.get("categories") or {}
    return Job(
        company=company.name,
        title=entry.get("text", ""),
        location=categories.get("location") or "",
        url=entry.get("hostedUrl", ""),
        job_id=str(entry.get("id", "")),
        posted_date=_epoch_ms_to_date(entry.get("createdAt")),
        scraped_date=scraped_date,
    )


def _epoch_ms_to_date(value) -> str:
    if not value:
        return ""
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date().isoformat()
    except (TypeError, ValueError, OSError):
        return ""
