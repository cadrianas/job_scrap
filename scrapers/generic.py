"""Last-resort adapter for companies with a plain HTML careers page and
no known ATS API. Deliberately dumb and low-maintenance: no JS rendering,
no per-company logic. If a page needs more than this, the fix is a
dedicated adapter or finding the underlying JSON call -- never Selenium.
"""

import hashlib
import logging
import time
from datetime import date
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

logger = logging.getLogger(__name__)

_JOB_HREF_HINTS = ("/job/", "/jobs/", "/careers/", "/position/", "/opening/", "/vacanc")
_NAV_TEXT_EXCLUDE = {"careers", "jobs", "open positions", "apply", "learn more"}

# domain -> True/False (can we fetch job paths), cached for this run.
_robots_cache: dict[str, bool] = {}


def fetch_jobs(company: Company) -> list[Job]:
    url = company.identifier
    domain = urlparse(url).netloc

    if not _allowed_by_robots(domain, url):
        logger.warning(
            "%s: careers path disallowed by robots.txt for %s, skipping", company.name, domain
        )
        return []

    html = _get_html(company, url)
    soup = BeautifulSoup(html, "html.parser")

    scraped_date = _today()
    jobs = []
    seen_urls: set[str] = set()

    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if not href:
            continue

        text = anchor.get_text(strip=True)
        if not _looks_like_job_link(href, text):
            continue

        absolute_url = urljoin(url, href)
        if absolute_url in seen_urls:
            continue
        seen_urls.add(absolute_url)

        jobs.append(
            Job(
                company=company.name,
                title=text,
                location="",
                url=absolute_url,
                job_id=hashlib.sha1(absolute_url.encode("utf-8")).hexdigest(),
                posted_date="",
                scraped_date=scraped_date,
            )
        )

    if not jobs:
        logger.warning(
            "%s: 0 jobs from generic adapter, page may need a dedicated adapter", company.name
        )

    return jobs


def _looks_like_job_link(href: str, text: str) -> bool:
    href_lower = href.lower()
    if not any(hint in href_lower for hint in _JOB_HREF_HINTS):
        return False
    if len(text) < 4:
        return False
    if text.strip().lower() in _NAV_TEXT_EXCLUDE:
        return False
    return True


def _allowed_by_robots(domain: str, careers_url: str) -> bool:
    if domain in _robots_cache:
        return _robots_cache[domain]

    allowed = True
    try:
        robots_url = f"https://{domain}/robots.txt"
        response = requests.get(
            robots_url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code == 200:
            allowed = _path_allowed(response.text, urlparse(careers_url).path or "/")
    except requests.RequestException:
        allowed = True  # no robots.txt reachable -> assume allowed

    _robots_cache[domain] = allowed
    return allowed


def _path_allowed(robots_txt: str, path: str) -> bool:
    """Minimal robots.txt check: applies User-agent: * Disallow rules only."""
    applies = False
    for line in robots_txt.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field = field.strip().lower()
        value = value.strip()

        if field == "user-agent":
            applies = value == "*"
        elif applies and field == "disallow" and value:
            if path.startswith(value):
                return False

    return True


def _get_html(company: Company, url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    last_error: str = "unknown error"

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            last_error = f"request failed: {exc}"
        else:
            if response.status_code == 200:
                if not response.text.strip():
                    raise ScraperError(company.name, "empty HTML body")
                return response.text
            last_error = f"HTTP {response.status_code} from {url}"

        if attempt < MAX_RETRIES:
            time.sleep(2**attempt)

    raise ScraperError(company.name, f"failed after {MAX_RETRIES + 1} attempts: {last_error}")


def _today() -> str:
    return date.today().isoformat()
