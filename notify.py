"""Turns the list of new jobs into a human-readable Markdown digest, and
prints the final run summary (the one permitted `print` in the codebase).
"""

from datetime import date, datetime, timedelta
from pathlib import Path

from config.paths import DIGESTS_DIR
from models import Company, Job

_NEW_MARKER_WINDOW = timedelta(hours=48)


def write_digest(new_jobs: list[Job], companies: dict[str, Company]) -> Path | None:
    if not new_jobs:
        return None

    today = date.today()
    total_new = len(new_jobs)
    lines = [f"# New jobs: {today.isoformat()} ({total_new} new)", ""]

    by_tier: dict[int, dict[str, list[Job]]] = {}
    for job in new_jobs:
        company = companies.get(job.company)
        tier = company.tier if company else 3
        by_company = by_tier.setdefault(tier, {})
        by_company.setdefault(job.company, []).append(job)

    for tier in sorted(by_tier):
        lines.append(f"## Tier {tier}")
        lines.append("")
        for company_name in sorted(by_tier[tier]):
            company = companies.get(company_name)
            regions = ", ".join(company.regions) if company else ""
            header = f"### {company_name} ({regions})" if regions else f"### {company_name}"
            lines.append(header)
            for job in by_tier[tier][company_name]:
                lines.append(_format_line(job, today))
            lines.append("")

    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    digest_path = DIGESTS_DIR / f"new_jobs_{today.isoformat()}.md"
    digest_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return digest_path


def _format_line(job: Job, today: date) -> str:
    marker = "NEW " if _is_recent(job.posted_date, today) else ""
    location = f" - {job.location}" if job.location else ""
    posted = f" - posted {job.posted_date}" if job.posted_date else ""
    return f"- {marker}[{job.title}]({job.url}){location}{posted}"


def _is_recent(posted_date: str, today: date) -> bool:
    if not posted_date:
        return False
    try:
        posted = datetime.strptime(posted_date, "%Y-%m-%d").date()
    except ValueError:
        return False
    return (today - posted) <= _NEW_MARKER_WINDOW


def print_summary(scraped: int, failed: list[str], total: int, new: int) -> None:
    print(f"Companies scraped: {scraped}")
    print(f"Companies failed: {len(failed)}" + (f" ({', '.join(failed)})" if failed else ""))
    print(f"Total jobs seen this run: {total}")
    print(f"New jobs: {new}")
