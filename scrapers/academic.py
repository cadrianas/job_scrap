"""Academic and public job-board aggregators (Phase 3b).

Covers multiple lightweight sources that don't each warrant their own
module (see SPEC_scraper_academic.md). company.ats selects which
source's logic runs; this file still exposes exactly one public
fetch_jobs, per the adapter contract in SPEC_models.md.
"""

import logging
import time
import xml.etree.ElementTree as ET
from datetime import date
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

logger = logging.getLogger(__name__)

EURAXESS_SEARCH_URL = "https://euraxess.ec.europa.eu/jobs/search"
JOBINDEX_RSS_URL = "https://www.jobindex.dk/jobsoegning.rss"


def fetch_jobs(company: Company) -> list[Job]:
    if company.ats == "euraxess":
        return _fetch_euraxess(company)
    if company.ats == "jobindex":
        return _fetch_jobindex(company)
    raise ScraperError(company.name, f"academic.py has no handler for ats={company.ats!r}")


def _fetch_euraxess(company: Company) -> list[Job]:
    """company.identifier is the pre-encoded EURAXESS query string, e.g.
    'f%5B0%5D=job_research_field%3A78'. Only page 1 is fetched -- add more
    companies.json entries with different facets to widen coverage rather
    than paginating one entry (see SPEC_scraper_academic.md).
    """
    url = f"{EURAXESS_SEARCH_URL}?{company.identifier}"
    html = _get_text(company, url)
    soup = BeautifulSoup(html, "html.parser")

    scraped_date = _today()
    jobs = []
    for article in soup.find_all("article", class_="ecl-content-item"):
        title_link = article.select_one("h3.ecl-content-block__title a")
        href = title_link.get("href") if title_link else None
        if not title_link or not href:
            continue

        title = title_link.get_text(strip=True)
        absolute_url = urljoin(EURAXESS_SEARCH_URL, href)
        job_id = href.rstrip("/").rsplit("/", 1)[-1]

        location = ""
        location_block = article.select_one(".id-Work-Locations .ecl-text-standard")
        if location_block:
            location = location_block.get_text(strip=True)

        jobs.append(
            Job(
                company=company.name,
                title=title,
                location=location,
                url=absolute_url,
                job_id=job_id,
                posted_date="",
                scraped_date=scraped_date,
            )
        )

    if not jobs:
        logger.warning("%s: 0 jobs from EURAXESS query, check facet params still valid", company.name)
    return jobs


def _fetch_jobindex(company: Company) -> list[Job]:
    """company.identifier is the Jobindex RSS query string, e.g. 'q=data+scientist'."""
    url = f"{JOBINDEX_RSS_URL}?{company.identifier}"
    xml_text = _get_text(company, url)

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ScraperError(company.name, f"could not parse Jobindex RSS: {exc}") from exc

    scraped_date = _today()
    jobs = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue

        posted_date = ""
        pub_date = (item.findtext("pubDate") or "").strip()
        if pub_date:
            try:
                posted_date = parsedate_to_datetime(pub_date).date().isoformat()
            except (TypeError, ValueError):
                posted_date = ""

        job_id = link.rstrip("/").rsplit("/", 1)[-1]

        jobs.append(
            Job(
                company=company.name,
                title=title,
                location="",
                url=link,
                job_id=job_id,
                posted_date=posted_date,
                scraped_date=scraped_date,
            )
        )

    if not jobs:
        logger.warning("%s: 0 jobs from Jobindex RSS", company.name)
    return jobs


def _get_text(company: Company, url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    last_error = "unknown error"

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            last_error = f"request failed: {exc}"
        else:
            if response.status_code == 200:
                if not response.text.strip():
                    raise ScraperError(company.name, "empty response body")
                return response.text
            last_error = f"HTTP {response.status_code} from {url}"

        if attempt < MAX_RETRIES:
            time.sleep(2**attempt)

    raise ScraperError(company.name, f"failed after {MAX_RETRIES + 1} attempts: {last_error}")


def _today() -> str:
    return date.today().isoformat()
