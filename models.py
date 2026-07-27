"""Shared dataclasses and exceptions used by every module.

Defines the adapter contract: every scraper takes a Company and returns
a list[Job], raising ScraperError on failure. Bottom of the dependency
graph -- this module imports nothing else from the project.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Company:
    """A single entry from companies.json."""

    name: str
    ats: str
    identifier: str
    regions: list[str]
    tier: int
    enabled: bool = True


@dataclass(frozen=True)
class Job:
    """The normalized unit every scraper must return."""

    company: str
    title: str
    location: str
    url: str
    job_id: str
    posted_date: str
    scraped_date: str

    @property
    def dedup_key(self) -> str:
        return f"{self.company}:{self.job_id}"


class ScraperError(Exception):
    """Raised by adapters on any failure: HTTP error after retries,
    unexpected schema, or an empty response where jobs were expected.
    """

    def __init__(self, company_name: str, message: str) -> None:
        self.company_name = company_name
        self.message = message
        super().__init__(f"{company_name}: {message}")
