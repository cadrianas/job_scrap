"""Adapter for Workday-hosted careers sites.

The careers page itself is a JS app, but it calls an internal JSON POST
endpoint, so no browser automation is needed. companies.json normally
stores identifier as "tenant/site"; this module discovers the wdN
instance number by trying candidates in order of prevalence and caches
the working one in memory for the run. For tenants where that fast
guess-list doesn't hit (confirmed live, not a speculative widen -- see
SPEC_scraper_workday.md), identifier may instead carry the confirmed
instance as "tenant/site|wdN" to skip probing entirely. All
Workday-specific quirks live in this one file, since this is the
adapter most likely to break when Workday changes something.
"""

import hashlib
import re
import time
from datetime import date, timedelta

import requests

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

_CANDIDATE_INSTANCES = ["wd1", "wd3", "wd5", "wd2", "wd4"]
_PAGE_LIMIT = 20
_MAX_JOBS = 2500
_MAX_CONSECUTIVE_PAGE_FAILURES = 3

# tenant -> wdN instance that worked last time, for this process's lifetime.
_instance_cache: dict[str, str] = {}


def fetch_jobs(company: Company) -> list[Job]:
    tenant, site, explicit_instance = _split_identifier(company.identifier)
    instance, first_payload = _discover_instance(company, tenant, site, explicit_instance)

    if "jobPostings" not in first_payload:
        raise ScraperError(company.name, "response missing 'jobPostings'")

    scraped_date = date.today().isoformat()
    jobs = [
        _to_job(company, tenant, site, instance, posting, scraped_date)
        for posting in first_payload["jobPostings"]
    ]

    total = first_payload.get("total")
    cap = min(total, _MAX_JOBS) if isinstance(total, int) else _MAX_JOBS

    offset = len(first_payload["jobPostings"])
    consecutive_failures = 0

    while offset < cap:
        time.sleep(0.5)
        payload = _request_page(tenant, site, instance, offset)

        if payload is None:
            consecutive_failures += 1
            if consecutive_failures > _MAX_CONSECUTIVE_PAGE_FAILURES:
                raise ScraperError(
                    company.name, "more than 3 consecutive failed pagination pages"
                )
            offset += _PAGE_LIMIT
            continue

        if "jobPostings" not in payload:
            raise ScraperError(company.name, "response missing 'jobPostings'")

        consecutive_failures = 0
        postings = payload["jobPostings"]
        if not postings:
            break

        jobs.extend(
            _to_job(company, tenant, site, instance, posting, scraped_date)
            for posting in postings
        )
        offset += len(postings)

    return jobs


def _split_identifier(identifier: str) -> tuple[str, str, str | None]:
    """"tenant/site" or "tenant/site|wdN" -> (tenant, site, explicit_instance)."""
    base, _, explicit_instance = identifier.partition("|")
    tenant, site = base.split("/", 1)
    return tenant, site, explicit_instance or None


def _discover_instance(
    company: Company, tenant: str, site: str, explicit_instance: str | None
) -> tuple[str, dict]:
    if explicit_instance is not None:
        payload = _request_page(tenant, site, explicit_instance, 0)
        if payload is not None and "jobPostings" in payload:
            _instance_cache[tenant] = explicit_instance
            return explicit_instance, payload
        raise ScraperError(
            company.name,
            f"explicit Workday instance '{explicit_instance}' for tenant '{tenant}' no longer "
            f"works -- re-confirm in browser devtools and update the identifier in "
            f"companies.json",
        )

    cached = _instance_cache.get(tenant)
    if cached is not None:
        payload = _request_page(tenant, site, cached, 0)
        if payload is not None and "jobPostings" in payload:
            return cached, payload

    for instance in _CANDIDATE_INSTANCES:
        payload = _request_page(tenant, site, instance, 0)
        if payload is not None and "jobPostings" in payload:
            _instance_cache[tenant] = instance
            return instance, payload

    raise ScraperError(
        company.name,
        f"no working Workday instance found among {_CANDIDATE_INSTANCES} for tenant "
        f"'{tenant}' -- check tenant/site identifier '{company.identifier}'",
    )


def _request_page(tenant: str, site: str, instance: str, offset: int) -> dict | None:
    url = f"https://{tenant}.{instance}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    body = {"appliedFacets": {}, "limit": _PAGE_LIMIT, "offset": offset, "searchText": ""}
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(
                url, json=body, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
            )
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


def _to_job(
    company: Company,
    tenant: str,
    site: str,
    instance: str,
    posting: dict,
    scraped_date: str,
) -> Job:
    bullet_fields = posting.get("bulletFields") or []
    external_path = posting.get("externalPath", "")
    job_id = str(bullet_fields[0]) if bullet_fields else hashlib.sha1(
        external_path.encode("utf-8")
    ).hexdigest()

    return Job(
        company=company.name,
        title=posting.get("title", ""),
        location=posting.get("locationsText") or "",
        url=f"https://{tenant}.{instance}.myworkdayjobs.com/{site}{external_path}",
        job_id=job_id,
        posted_date=_parse_posted_on(posting.get("postedOn")),
        scraped_date=scraped_date,
    )


def _parse_posted_on(value: str | None) -> str:
    if not value:
        return ""
    today = date.today()
    lowered = value.lower()
    if "today" in lowered:
        return today.isoformat()
    if "yesterday" in lowered:
        return (today - timedelta(days=1)).isoformat()
    match = re.search(r"(\d+)\+?\s*days?\s*ago", lowered)
    if match:
        return (today - timedelta(days=int(match.group(1)))).isoformat()
    return ""
