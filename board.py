"""Builds a persistent, browsable "apply board": every job in
jobs_seen.csv matching the target role filters, as both an HTML page
and a CSV. Regenerated in full each run, never appended to.
"""

import csv
import json
import logging
import sys

import dedup
import filters
from config import paths
from models import Company, Job

logger = logging.getLogger("board")

_CSV_FIELDNAMES = ["company", "title", "url", "first_seen"]


def build_board() -> None:
    seen = dedup.load_seen()
    companies = _load_companies()

    jobs = [_row_to_job(row) for row in seen.values()]
    matching = [job for job in jobs if filters.matches(job.title)]
    sorted_jobs = filters.apply(matching, companies)

    _write_csv(sorted_jobs)
    _write_html(sorted_jobs, companies)


def _load_companies() -> dict[str, Company]:
    with paths.COMPANIES_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    companies = {}
    for c in raw:
        companies[c["name"]] = Company(
            name=c["name"],
            ats=c["ats"],
            identifier=c["identifier"],
            regions=c.get("regions", []),
            tier=c.get("tier", 3),
            enabled=c.get("enabled", True),
        )
    return companies


def _row_to_job(row: dict) -> Job:
    dedup_key = row["dedup_key"]
    company = row["company"]
    job_id = dedup_key[len(company) + 1 :] if dedup_key.startswith(company + ":") else dedup_key
    return Job(
        company=company,
        title=row["title"],
        location="",
        url=row["url"],
        job_id=job_id,
        posted_date=row.get("first_seen", ""),
        scraped_date=row.get("last_seen", ""),
    )


def _write_csv(jobs: list[Job]) -> None:
    with paths.BOARD_CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDNAMES)
        writer.writeheader()
        for job in jobs:
            writer.writerow(
                {
                    "company": job.company,
                    "title": job.title,
                    "url": job.url,
                    "first_seen": job.posted_date,
                }
            )


def _write_html(jobs: list[Job], companies: dict[str, Company]) -> None:
    rows_json = json.dumps(
        [
            {
                "company": job.company,
                "title": job.title,
                "url": job.url,
                "first_seen": job.posted_date,
                "tier": companies[job.company].tier if job.company in companies else 3,
                "regions": companies[job.company].regions if job.company in companies else [],
            }
            for job in jobs
        ]
    )

    html = _HTML_TEMPLATE.replace("__JOBS__", rows_json).replace("__COUNT__", str(len(jobs)))
    paths.BOARD_HTML_FILE.write_text(html, encoding="utf-8")


_HTML_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Job Board</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 900px; margin: 0 auto; padding: 24px 20px 60px; background: #f5f6f6; color: #182322; }
h1 { font-size: 20px; margin-bottom: 4px; }
.sub { color: #5c6b6a; font-size: 13px; margin-bottom: 16px; }
#search { width: 100%; box-sizing: border-box; padding: 9px 12px; font-size: 14px; border: 1px solid #dde2e2; border-radius: 6px; margin-bottom: 14px; }
table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 6px; overflow: hidden; }
th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #eceff0; font-size: 13.5px; }
th { background: #eaeeee; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: #5c6b6a; }
tr:hover td { background: #f0f3f2; }
a { color: #2f5750; text-decoration: none; font-weight: 600; }
a:hover { text-decoration: underline; }
.tier { font-size: 11px; padding: 2px 7px; border-radius: 999px; background: #dbe8e5; color: #2f5750; font-weight: 600; }
.empty { text-align: center; color: #5c6b6a; padding: 30px; }
</style>
</head>
<body>
<h1>Job Board</h1>
<p class="sub"><span id="count-shown">__COUNT__</span> of __COUNT__ jobs matching your target roles. Regenerate with <code>python board.py</code>.</p>
<input id="search" type="text" placeholder="Search title or company...">
<table id="table">
<thead><tr><th>Company</th><th>Title</th><th>Tier</th><th>First seen</th></tr></thead>
<tbody id="tbody"></tbody>
</table>
<div id="empty" class="empty" style="display:none">No jobs match your search.</div>

<script>
const JOBS = __JOBS__;

function render(filterText) {
  const tbody = document.getElementById("tbody");
  const empty = document.getElementById("empty");
  const lowered = filterText.trim().toLowerCase();

  const filtered = JOBS.filter(j =>
    !lowered || j.title.toLowerCase().includes(lowered) || j.company.toLowerCase().includes(lowered)
  );

  document.getElementById("count-shown").textContent = filtered.length;
  tbody.innerHTML = "";
  empty.style.display = filtered.length === 0 ? "block" : "none";

  filtered.forEach(j => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${j.company}</td>
      <td><a href="${j.url}" target="_blank" rel="noopener noreferrer">${j.title}</a></td>
      <td><span class="tier">Tier ${j.tier}</span></td>
      <td>${j.first_seen || ""}</td>
    `;
    tbody.appendChild(tr);
  });
}

document.getElementById("search").addEventListener("input", e => render(e.target.value));
render("");
</script>
</body>
</html>
"""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    build_board()
    logger.info("board written to %s and %s", paths.BOARD_HTML_FILE, paths.BOARD_CSV_FILE)
    sys.exit(0)
