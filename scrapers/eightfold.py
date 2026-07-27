"""Adapter for Eightfold-hosted careers sites.

Undocumented but stable JSON API behind the careers page. companies.json
stores the careers domain as identifier; the `domain` query param the API
actually wants is guessed by stripping the first subdomain label, with a
fallback to the identifier itself if that guess looks wrong.

Some deployments (confirmed: Netflix) use a `domain` value that isn't
derivable from the careers host at all. For those, identifier can be
written as "{careers_domain}|{explicit_domain_param}" to skip guessing.
"""

import time
from datetime import date, datetime, timezone

import requests

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

_PAGE_SIZE = 100
_MAX_JOBS = 500


def fetch_jobs(company: Company) -> list[Job]:
    careers_domain, explicit_domain = _split_identifier(company.identifier)

    if explicit_domain is not None:
        first_payload = _request_page(careers_domain, explicit_domain, 0, _PAGE_SIZE)
        if first_payload is None or "positions" not in first_payload:
            raise ScraperError(
                company.name,
                f"non-200 or invalid response using explicit domain '{explicit_domain}'",
            )
        domain_param = explicit_domain
    else:
        guessed_domain = _strip_first_label(careers_domain)
        domain_param, first_payload = _discover_domain(company, careers_domain, guessed_domain)

    if "positions" not in first_payload:
        raise ScraperError(company.name, "response missing 'positions'")

    scraped_date = date.today().isoformat()
    jobs = [
        _to_job(company, careers_domain, posting, scraped_date)
        for posting in first_payload["positions"]
    ]

    count = first_payload.get("count")
    cap = min(count, _MAX_JOBS) if isinstance(count, int) else _MAX_JOBS

    start = len(first_payload["positions"])
    while start < cap:
        payload = _request_page(careers_domain, domain_param, start, _PAGE_SIZE)
        if payload is None:
            raise ScraperError(company.name, f"failed to fetch page at start={start}")
        if "positions" not in payload:
            raise ScraperError(company.name, "response missing 'positions'")

        positions = payload["positions"]
        if not positions:
            break

        jobs.extend(_to_job(company, careers_domain, p, scraped_date) for p in positions)
        start += len(positions)

    return jobs


def _discover_domain(company: Company, careers_domain: str, guessed_domain: str) -> tuple[str, dict]:
    guess_payload = _request_page(careers_domain, guessed_domain, 0, _PAGE_SIZE)
    guess_ok = guess_payload is not None and "positions" in guess_payload
    if guess_ok and guess_payload["positions"]:
        return guessed_domain, guess_payload

    fallback_payload = _request_page(careers_domain, careers_domain, 0, _PAGE_SIZE)
    fallback_ok = fallback_payload is not None and "positions" in fallback_payload
    if fallback_ok and fallback_payload["positions"]:
        return careers_domain, fallback_payload

    # Neither guess had jobs; prefer whichever was at least a structurally
    # valid response (zero open jobs is a real possibility, not an error).
    if guess_ok:
        return guessed_domain, guess_payload
    if fallback_ok:
        return careers_domain, fallback_payload

    raise ScraperError(
        company.name,
        f"non-200 or invalid response from both domain guesses "
        f"('{guessed_domain}', '{careers_domain}')",
    )


def _split_identifier(identifier: str) -> tuple[str, str | None]:
    if "|" in identifier:
        careers_domain, explicit_domain = identifier.split("|", 1)
        return careers_domain, explicit_domain
    return identifier, None


def _strip_first_label(domain: str) -> str:
    parts = domain.split(".", 1)
    return parts[1] if len(parts) == 2 else domain


def _request_page(careers_domain: str, domain_param: str, start: int, num: int) -> dict | None:
    url = f"https://{careers_domain}/api/apply/v2/jobs"
    params = {"domain": domain_param, "start": start, "num": num, "sort_by": "timestamp"}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
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


def _to_job(company: Company, careers_domain: str, posting: dict, scraped_date: str) -> Job:
    position_id = posting.get("id")
    url = posting.get("canonicalPositionUrl") or f"https://{careers_domain}/careers?pid={position_id}"
    return Job(
        company=company.name,
        title=posting.get("name", ""),
        location=posting.get("location") or "",
        url=url,
        job_id=str(position_id),
        posted_date=_epoch_to_date(posting.get("t_create")),
        scraped_date=scraped_date,
    )


def _epoch_to_date(value) -> str:
    if not value:
        return ""
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc).date().isoformat()
    except (TypeError, ValueError, OSError):
        return ""
