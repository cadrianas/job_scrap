"""Keyword and region filtering so the digest surfaces relevant roles.

Strategy is broad-then-filter: main.py records every scraped job to
jobs_seen.csv regardless of match status. This module only decides what
a digest run surfaces, and in what order.
"""

import re
from models import Company, Job

# "strict" hides non-matching jobs from the digest entirely (they're still
# recorded in jobs_seen.csv). "annotate" shows everything, matches sorted
# first. Strict is the default: the digest is meant to be short and
# actionable, not a browse-everything feed.
MODE = "strict"

INCLUDE = [
    # Data science & AI/ML
    "data scientist", "data science", "machine learning", "ml engineer", "mlops",
    "ai scientist", "applied scientist", "research scientist",
    "decision scientist", "decision science", "nlp", "computer vision",
    "research engineer", "prompt engineer",
    # Data analytics & BI
    "data analyst", "data analytics", "analytics", "analytics engineer",
    "business intelligence", "bi analyst", "product analytics", "product analyst",
    "insights analyst",
    # Mathematical / quantitative / statistical modelling
    "mathematical model", "mathematical modeller", "mathematical modeling",
    "mathematical modelling", "quantitative", "quant", "quantitative modeller",
    "quantitative analyst", "quantitative researcher", "quantitative research",
    "modeller", "modeler", "bayesian", "statistician", "statistical modeller",
    "stochastic", "causal inference", "operations research", "actuary", "actuarial",
    "risk modeller", "risk model", "risk analyst", "risk manager", "financial engineer",
    "simulation engineer", "systems modeller", "statistical programmer",
    # Mathematical epidemiology & public health modelling (PhD Domain)
    "epidemiolog", "biostatistician", "infectious disease", "disease modelling",
    "disease modeling", "outbreak model", "outbreak analytics", "transmission model",
    "compartmental model", "public health modelling", "public health modeling",
    "computational epidemiology", "bioinformatic", "computational biology",
    "health economist", "health economics", "population health",
    "real world evidence", "real world data", "rwe", "rwd",
    "pharmacometrics", "qsp model", "clinical data scientist", "health data scientist",
    # Data engineering & platform
    "data engineer", "data architect", "data architecture", "etl engineer", "data platform",
    # Academic instruction & teaching
    "instructor", "lecturer", "teaching fellow", "assistant professor", "associate professor", "professor",
]


EXCLUDE = [
    "intern", "working student", "principal recruiter", "sales",
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

INDIA_KEYWORDS = [
    "bangalore", "bengaluru", "hyderabad", "mumbai", "pune", "gurgaon", "gurugram",
    "noida", "kolkata", "chennai", "ahmedabad", "delhi", "karnataka", "telangana",
    "maharashtra", "tamil nadu", "haryana", "west bengal", "gujarat", "manyata",
    "velankani", "salarpuria", "dlf downtown",
]

_INDIA_WORD_REGEX = re.compile(r"\bindia\b", re.IGNORECASE)
_INDIA_CITY_REGEX = re.compile(
    r"\b(?:" + "|".join(re.escape(k) for k in INDIA_KEYWORDS) + r")\b", re.IGNORECASE
)
_INDIA_PREFIX_REGEX = re.compile(r"^(?:in[-_ ]|\b(?:in|india)\b)", re.IGNORECASE)


def matches(title: str) -> bool:
    """True if title matches an INCLUDE keyword and no EXCLUDE keyword."""
    lowered = title.lower()
    if any(term in lowered for term in EXCLUDE):
        return False
    return any(term in lowered for term in INCLUDE)


def is_india_job(job: Job) -> bool:
    """Returns True if the job's location, title, or URL indicates it is located in India."""
    if _INDIA_PREFIX_REGEX.search(job.title.strip()):
        return True

    text_to_check = f"{job.title} {job.location} {job.url}"
    if _INDIA_WORD_REGEX.search(text_to_check):
        return True
    if _INDIA_CITY_REGEX.search(text_to_check):
        return True

    return False


def get_seniority_tier(title: str) -> str:
    """Categorize job title into Seniority Tiers for digest grouping."""
    lowered = title.lower()
    exec_keywords = ["director", "head of", "vp", "vice president", "chief"]
    senior_keywords = ["senior", "sr.", "sr ", "staff", "principal", "lead"]

    if any(term in lowered for term in exec_keywords):
        return "Executive / Director / Lead"
    if any(term in lowered for term in senior_keywords):
        return "Senior / Staff"
    return "Mid / Entry / General"


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
    # Exclude jobs located in India across all modes
    jobs = [job for job in jobs if not is_india_job(job)]

    if MODE == "strict":
        jobs = [job for job in jobs if matches(job.title)]

    def sort_key(job: Job) -> tuple:
        company = companies.get(job.company)
        tier = company.tier if company else 3
        match_rank = 0 if matches(job.title) else 1
        region_rank = 0 if _is_priority_region(company) else 1
        return (match_rank, tier, region_rank, job.company.lower(), job.title.lower())

    return sorted(jobs, key=sort_key)


