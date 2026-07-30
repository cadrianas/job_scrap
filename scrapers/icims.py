"""Adapter for iCIMS-hosted careers sites.

iCIMS uses search portals at https://{identifier}.icims.com/jobs/search
returning structured HTML tables of job listings.
"""

import re
from datetime import date
from bs4 import BeautifulSoup
import requests

from config.paths import MAX_RETRIES, REQUEST_TIMEOUT_SECONDS, USER_AGENT
from models import Company, Job, ScraperError

_PAGE_LIMIT = 50


def fetch_jobs(company: Company) -> list[Job]:
    identifier = company.identifier.strip()
    if identifier.startswith("http://") or identifier.startswith("https://"):
        base_url = identifier.rstrip("/")
    else:
        base_url = f"https://{identifier}.icims.com/jobs/search"

    headers = {"User-Agent": USER_AGENT}
    scraped_date = date.today().isoformat()
    jobs: list[Job] = []

    for page in range(0, 10):  # Scrape up to 10 pages (~500 jobs max)
        url = f"{base_url}?in_iframe=1&pr={page}"
        response = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                res = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
                if res.status_code == 200:
                    response = res
                    break
            except requests.RequestException:
                pass

        if response is None:
            if page == 0:
                raise ScraperError(company.name, f"Failed to fetch iCIMS page {page} from {url}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        job_links = soup.find_all("a", href=re.compile(r"/jobs/\d+/"))

        if not job_links and page == 0:
            # Check if page loaded but has no jobs
            if "iCIMS" not in response.text and "Job" not in response.text:
                raise ScraperError(company.name, "Response invalid or missing iCIMS content")
            break

        page_jobs_added = 0
        seen_urls_in_page = set()

        for a in job_links:
            href = a.get("href", "")
            if not href or href in seen_urls_in_page:
                continue
            seen_urls_in_page.add(href)

            match = re.search(r"/jobs/(\d+)/", href)
            if not match:
                continue

            job_id = match.group(1)
            title = a.get_text(strip=True)
            if not title or title.lower() in ("apply", "view job", "details"):
                # Try parent container for title
                parent = a.find_parent("tr") or a.find_parent("div")
                if parent:
                    title_elem = parent.find("h2") or parent.find("h3") or parent.find("strong")
                    if title_elem:
                        title = title_elem.get_text(strip=True)

            if not title:
                title = f"Job {job_id}"

            full_url = href if href.startswith("http") else f"https://{identifier}.icims.com{href}"

            jobs.append(
                Job(
                    company=company.name,
                    title=title,
                    location="",
                    url=full_url,
                    job_id=job_id,
                    posted_date="",
                    scraped_date=scraped_date,
                )
            )
            page_jobs_added += 1

        if page_jobs_added == 0:
            break

    return jobs
