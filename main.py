"""Orchestrator: loads config, dispatches each company to the right
scraper, dedupes, filters, notifies, and updates state.
"""

import argparse
import json
import logging
import sys
import time
from datetime import date

import dedup
import filters
import health
import notify
from config import paths
from models import Company, Job, ScraperError
from scrapers import academic, eightfold, generic, greenhouse, lever, workday

logger = logging.getLogger("main")

# Only ATS types with a real adapter go here. Anything else (an unknown
# ats value) is skipped, not failed -- see SPEC_main.md. All five adapters
# from PLAN.md Phase 1-3 are now implemented, plus the Phase 3b academic
# sources documented in SPEC_scraper_academic.md (academic.py dispatches
# internally on company.ats, so both keys point at the same function).
ADAPTERS = {
    "greenhouse": greenhouse.fetch_jobs,
    "lever": lever.fetch_jobs,
    "workday": workday.fetch_jobs,
    "eightfold": eightfold.fetch_jobs,
    "generic": generic.fetch_jobs,
    "euraxess": academic.fetch_jobs,
    "jobindex": academic.fetch_jobs,
}

KNOWN_ATS_VALUES = {
    "greenhouse",
    "lever",
    "workday",
    "eightfold",
    "generic",
    "euraxess",
    "jobindex",
}


def _load_companies_raw() -> list[dict]:
    with paths.COMPANIES_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate(raw_companies: list[dict]) -> list[str]:
    """Returns a list of problem descriptions. Empty list = valid."""
    problems = []

    names = [c["name"] for c in raw_companies]
    seen_names = set()
    for name in names:
        if name in seen_names:
            problems.append(f"duplicate company name: {name!r}")
        seen_names.add(name)

    for c in raw_companies:
        if c.get("ats") not in KNOWN_ATS_VALUES:
            logger.warning(
                "company %r has unknown ats value %r (will be skipped, not a validation error)",
                c.get("name"),
                c.get("ats"),
            )

    return problems


def _to_companies(raw_companies: list[dict]) -> list[Company]:
    companies = []
    for c in raw_companies:
        if not c.get("enabled", True):
            continue
        companies.append(
            Company(
                name=c["name"],
                ats=c["ats"],
                identifier=c["identifier"],
                regions=c.get("regions", []),
                tier=c.get("tier", 3),
                enabled=c.get("enabled", True),
            )
        )
    return companies


def _setup_logging() -> None:
    paths.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = paths.LOGS_DIR / f"run_{date.today().isoformat()}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stderr),
        ],
    )


def _scrape_all(companies: list[Company]) -> tuple[list[Job], dict[str, bool]]:
    """Returns (all scraped jobs from successful companies, results map)."""
    all_jobs: list[Job] = []
    results: dict[str, bool] = {}

    ordered = sorted(companies, key=lambda c: (c.tier, c.name))

    for company in ordered:
        fetch = ADAPTERS.get(company.ats)
        if fetch is None:
            logger.warning(
                "%s: no adapter implemented for ats=%r, skipping", company.name, company.ats
            )
            continue

        try:
            jobs = fetch(company)
        except ScraperError as exc:
            logger.error("%s: %s", company.name, exc.message)
            results[company.name] = False
        except Exception as exc:  # noqa: BLE001 - a single company must never kill the run
            logger.error("%s: unexpected error: %s", company.name, exc)
            results[company.name] = False
        else:
            logger.info("%s: %d jobs", company.name, len(jobs))
            results[company.name] = True
            all_jobs.extend(jobs)

        time.sleep(paths.SLEEP_BETWEEN_COMPANIES_SECONDS)

    return all_jobs, results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Daily job scraper")
    parser.add_argument("--companies", help="comma-separated company names to scrape")
    parser.add_argument("--dry-run", action="store_true", help="scrape and report, write nothing")
    parser.add_argument("--validate", action="store_true", help="validate companies.json and exit")
    args = parser.parse_args(argv)

    paths.ensure_dirs()
    _setup_logging()

    try:
        raw_companies = _load_companies_raw()
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("cannot load %s: %s", paths.COMPANIES_FILE, exc)
        return 1

    problems = _validate(raw_companies)
    if problems:
        for problem in problems:
            logger.error("companies.json invalid: %s", problem)
        return 1

    if args.validate:
        logger.info("companies.json is valid (%d entries)", len(raw_companies))
        return 0

    companies = _to_companies(raw_companies)

    if args.companies:
        wanted = {name.strip() for name in args.companies.split(",")}
        companies = [c for c in companies if c.name in wanted]

    companies_by_name = {c.name: c for c in companies}

    seen = dedup.load_seen()
    health_state = health.load_health()

    all_jobs, results = _scrape_all(companies)

    attempted = len(results)
    failed_names = [name for name, ok in results.items() if not ok]
    if attempted > 0 and len(failed_names) / attempted > 0.5:
        logger.error(
            "%d of %d attempted companies failed (>50%%), treating as systemic breakage",
            len(failed_names),
            attempted,
        )
        exit_code = 2
    else:
        exit_code = 0

    new_jobs = dedup.find_new(all_jobs, seen)
    filtered_jobs = filters.apply(new_jobs, companies_by_name)

    if not args.dry_run:
        digest_path = notify.write_digest(filtered_jobs, companies_by_name)
        if digest_path:
            logger.info("digest written to %s", digest_path)
    else:
        logger.info("--dry-run: skipping digest write and state updates")

    notify.print_summary(
        scraped=sum(1 for ok in results.values() if ok),
        failed=failed_names,
        total=len(all_jobs),
        new=len(new_jobs),
    )

    if not args.dry_run:
        try:
            dedup.update_seen(all_jobs, seen)
            health.update_health(results, health_state)
            paths.NEW_JOBS_COUNT_FILE.write_text(str(len(new_jobs)), encoding="utf-8")
        except OSError as exc:
            logger.error("failed to write state: %s", exc)
            return 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
