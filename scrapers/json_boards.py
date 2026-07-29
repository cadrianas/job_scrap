"""Adapter for five small vendor-hosted job board APIs: Ashby, SmartRecruiters,
Workable, Breezy HR, BambooHR. Grouped in one file because each is a public,
unauthenticated JSON endpoint differing only in URL template, pagination, and
field names -- see SPEC_scraper_json_boards.md for why this bends PLAN.md's
one-module-per-adapter principle, following the scrapers/academic.py
precedent. company.ats selects which vendor's logic runs; this file still
exposes exactly one public fetch_jobs, per the adapter contract in
SPEC_models.md.
"""

import logging
import time
from datetime import date

import requests

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

logger = logging.getLogger(__name__)

_ASHBY_URL = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
_SMARTRECRUITERS_URL = "https://api.smartrecruiters.com/v1/companies/{company_id}/postings"
_SMARTRECRUITERS_JOB_URL = "https://jobs.smartrecruiters.com/{company_id}/{job_id}"
_SMARTRECRUITERS_PAGE_LIMIT = 100
_SMARTRECRUITERS_MAX_JOBS = 500
_WORKABLE_URL = "https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true"
_BREEZY_URL = "https://{slug}.breezy.hr/json"
_BAMBOOHR_URL = "https://{slug}.bamboohr.com/careers/list"
_BAMBOOHR_JOB_URL = "https://{slug}.bamboohr.com/careers/{job_id}"


def fetch_jobs(company: Company) -> list[Job]:
    if company.ats == "ashby":
        return _fetch_ashby(company)
    if company.ats == "smartrecruiters":
        return _fetch_smartrecruiters(company)
    if company.ats == "workable":
        return _fetch_workable(company)
    if company.ats == "breezyhr":
        return _fetch_breezyhr(company)
    if company.ats == "bamboohr":
        return _fetch_bamboohr(company)
    raise ScraperError(company.name, f"json_boards.py has no handler for ats={company.ats!r}")


def _fetch_ashby(company: Company) -> list[Job]:
    url = _ASHBY_URL.format(slug=company.identifier)
    payload = _get_json(company, url)

    if "jobs" not in payload:
        raise ScraperError(company.name, "response missing 'jobs'")

    scraped_date = _today()
    return [
        Job(
            company=company.name,
            title=posting.get("title", ""),
            location=posting.get("location") or "",
            url=posting.get("jobUrl", ""),
            job_id=str(posting.get("id", "")),
            posted_date=_iso_datetime_to_date(posting.get("publishedAt")),
            scraped_date=scraped_date,
        )
        for posting in payload["jobs"]
    ]


def _fetch_smartrecruiters(company: Company) -> list[Job]:
    company_id = company.identifier
    scraped_date = _today()

    first = _get_json(
        company,
        _SMARTRECRUITERS_URL.format(company_id=company_id),
        params={"limit": _SMARTRECRUITERS_PAGE_LIMIT, "offset": 0},
    )
    if "content" not in first:
        raise ScraperError(company.name, "response missing 'content'")

    total = first.get("totalFound")
    cap = min(total, _SMARTRECRUITERS_MAX_JOBS) if isinstance(total, int) else _SMARTRECRUITERS_MAX_JOBS

    jobs = [_to_smartrecruiters_job(company, company_id, posting, scraped_date) for posting in first["content"]]

    offset = len(first["content"])
    consecutive_failures = 0

    while offset < cap:
        time.sleep(0.5)
        payload = _get_json_or_none(
            company,
            _SMARTRECRUITERS_URL.format(company_id=company_id),
            params={"limit": _SMARTRECRUITERS_PAGE_LIMIT, "offset": offset},
        )

        if payload is None:
            consecutive_failures += 1
            if consecutive_failures > 3:
                raise ScraperError(company.name, "more than 3 consecutive failed pagination pages")
            offset += _SMARTRECRUITERS_PAGE_LIMIT
            continue

        if "content" not in payload:
            raise ScraperError(company.name, "response missing 'content'")

        consecutive_failures = 0
        postings = payload["content"]
        if not postings:
            break

        jobs.extend(_to_smartrecruiters_job(company, company_id, posting, scraped_date) for posting in postings)
        offset += len(postings)

    return jobs


def _to_smartrecruiters_job(company: Company, company_id: str, posting: dict, scraped_date: str) -> Job:
    job_id = str(posting.get("id", ""))
    location = (posting.get("location") or {}).get("fullLocation") or ""
    return Job(
        company=company.name,
        title=posting.get("name", ""),
        location=location,
        url=_SMARTRECRUITERS_JOB_URL.format(company_id=company_id, job_id=job_id),
        job_id=job_id,
        posted_date=_iso_datetime_to_date(posting.get("releasedDate")),
        scraped_date=scraped_date,
    )


def _fetch_workable(company: Company) -> list[Job]:
    url = _WORKABLE_URL.format(slug=company.identifier)
    payload = _get_json(company, url)

    if "jobs" not in payload:
        raise ScraperError(company.name, "response missing 'jobs'")

    scraped_date = _today()
    jobs = []
    for posting in payload["jobs"]:
        location = ", ".join(
            part for part in (posting.get("city"), posting.get("state"), posting.get("country")) if part
        )
        jobs.append(
            Job(
                company=company.name,
                title=posting.get("title", ""),
                location=location,
                url=posting.get("url", ""),
                job_id=str(posting.get("shortcode", "")),
                posted_date=posting.get("published_on") or "",
                scraped_date=scraped_date,
            )
        )
    return jobs


def _fetch_breezyhr(company: Company) -> list[Job]:
    url = _BREEZY_URL.format(slug=company.identifier)
    payload = _get_json(company, url)

    if not isinstance(payload, list):
        raise ScraperError(company.name, "response is not a JSON list")

    scraped_date = _today()
    jobs = []
    for posting in payload:
        location = (posting.get("location") or {}).get("name") or ""
        jobs.append(
            Job(
                company=company.name,
                title=posting.get("name", ""),
                location=location,
                url=posting.get("url", ""),
                job_id=str(posting.get("id", "")),
                posted_date=_iso_datetime_to_date(posting.get("published_date")),
                scraped_date=scraped_date,
            )
        )
    return jobs


def _fetch_bamboohr(company: Company) -> list[Job]:
    slug = company.identifier
    url = _BAMBOOHR_URL.format(slug=slug)
    payload = _get_json(company, url)

    if "result" not in payload:
        raise ScraperError(company.name, "response missing 'result'")

    scraped_date = _today()
    jobs = []
    for posting in payload["result"]:
        job_id = str(posting.get("id", ""))
        loc = posting.get("location") or {}
        location = ", ".join(part for part in (loc.get("city"), loc.get("state")) if part)
        jobs.append(
            Job(
                company=company.name,
                title=posting.get("jobOpeningName", ""),
                location=location,
                url=_BAMBOOHR_JOB_URL.format(slug=slug, job_id=job_id),
                job_id=job_id,
                posted_date="",
                scraped_date=scraped_date,
            )
        )
    return jobs


def _get_json(company: Company, url: str, params: dict | None = None):
    payload = _get_json_or_none(company, url, params)
    if payload is None:
        raise ScraperError(company.name, f"failed after {MAX_RETRIES + 1} attempts: request to {url} failed")
    return payload


def _get_json_or_none(company: Company, url: str, params: dict | None = None):
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException:
            if attempt < MAX_RETRIES:
                time.sleep(2**attempt)
                continue
            return None

        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return None

        if response.status_code >= 500 and attempt < MAX_RETRIES:
            time.sleep(2**attempt)
            continue

        return None

    return None


def _iso_datetime_to_date(value: str | None) -> str:
    """"2026-01-06T19:12:32.093+00:00" -> "2026-01-06"; anything not shaped
    like an ISO datetime (missing, too short, wrong separators) -> "".
    """
    if not value or len(value) < 10 or value[4] != "-" or value[7] != "-":
        return ""
    return value[:10]


def _today() -> str:
    return date.today().isoformat()
