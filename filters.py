"""Keyword and region filtering so the digest surfaces relevant roles.

Strategy is broad-then-filter: main.py records every scraped job to
jobs_seen.csv regardless of match status. This module only decides what
a digest run surfaces, and in what order.
"""

from models import Company, Job

# "strict" hides non-matching jobs from the digest entirely (they're still
# recorded in jobs_seen.csv). "annotate" shows everything, matches sorted
# first. Strict is the default: the digest is meant to be short and
# actionable, not a browse-everything feed.
MODE = "strict"

INCLUDE = [
    # Data science
    "data scientist", "data science", "machine learning", "ml engineer",
    "ai scientist", "applied scientist", "research scientist",
    "decision scientist", "decision science",
    # Data analytics
    "data analyst", "data analytics", "analytics", "analytics engineer",
    "business intelligence", "bi analyst", "product analytics",
    # Mathematical / quantitative modelling
    "mathematical model", "mathematical modeller", "mathematical modeling",
    "mathematical modelling", "quantitative", "quant", "quantitative modeller",
    "quantitative analyst", "quantitative researcher", "quantitative research",
    "modeller", "modeler", "bayesian", "statistician", "statistical modeller",
    "operations research", "actuary", "actuarial", "risk modeller", "risk model",
    # Mathematical epidemiology / public health modelling
    "epidemiolog", "biostatistician", "infectious disease model",
    "disease modelling", "disease modeling", "outbreak model",
    "outbreak analytics", "transmission model", "compartmental model",
    "public health modelling", "public health modeling",
    "computational epidemiology", "bioinformatic", "computational biology",
    "health economist", "health economics", "population health",
]

EXCLUDE = [
    "intern", "working student", "director", "vp", "head of",
    "principal recruiter", "sales",
]

PRIORITY_REGIONS = [
    # Europe
    "helsinki", "nordics", "copenhagen", "stockholm", "oslo", "netherlands",
    "basel", "europe",
    # Canada
    "toronto", "vancouver", "montreal", "ottawa", "canada",
    # USA
    "new york", "san francisco", "seattle", "boston", "austin", "usa",
    # Australia
    "sydney", "melbourne", "canberra", "brisbane", "australia",
    # New Zealand
    "auckland", "wellington", "new zealand",
]


def matches(title: str) -> bool:
    """True if title matches an INCLUDE keyword and no EXCLUDE keyword."""
    lowered = title.lower()
    if any(term in lowered for term in EXCLUDE):
        return False
    return any(term in lowered for term in INCLUDE)


def _is_priority_region(company: Company | None) -> bool:
    if company is None:
        return False
    regions = {r.lower() for r in company.regions}
    return bool(regions & set(PRIORITY_REGIONS))


def apply(jobs: list[Job], companies: dict[str, Company]) -> list[Job]:
    """Sort (and, in strict mode, filter) jobs for the digest.

    Sort order: matching jobs first (only bites in annotate mode, since
    strict mode already filtered down to matches), then by company tier,
    then by whether the company has a priority region, then alphabetically
    for a stable, deterministic order.
    """
    if MODE == "strict":
        jobs = [job for job in jobs if matches(job.title)]

    def sort_key(job: Job) -> tuple:
        company = companies.get(job.company)
        tier = company.tier if company else 3
        match_rank = 0 if matches(job.title) else 1
        region_rank = 0 if _is_priority_region(company) else 1
        return (match_rank, tier, region_rank, job.company.lower(), job.title.lower())

    return sorted(jobs, key=sort_key)
