# SPEC: notify.py

## Purpose
Turn the list of new jobs into human-readable output. Phase 2 target: a Markdown digest committed to the repo. Optional later: email or Slack webhook.

## API
- `write_digest(new_jobs: list[Job], companies: dict[str, Company]) -> Path | None`
  - `companies` (name -> Company) is needed to group by tier and to print each company's region tags in the header; this is a deliberate deviation from the original single-argument signature.
  - If `new_jobs` is empty: write nothing, return None.
  - Else write `DIGESTS_DIR / f"new_jobs_{YYYY-MM-DD}.md"` and return the path.
- `print_summary(scraped: int, failed: list[str], total: int, new: int) -> None`
  - The one permitted `print` in the codebase. Plain text final summary for the Actions log.

## Digest format
```markdown
# New jobs: 2026-07-10 (14 new)

## Tier 1

### Oura (helsinki, nordics)
- [Senior Data Scientist, Health Algorithms](URL) - Helsinki - posted 2026-07-09
- [Staff ML Engineer](URL) - Helsinki - posted 2026-07-10

## Tier 2
...
```

Grouped by tier, then company. Each line: linked title, location, posted date if known. Jobs posted within the last 48 hours get a "NEW" marker at the line start, since applying fast is the point.

## Optional channels (later, behind env vars)
- `SLACK_WEBHOOK` env var set -> also POST a compact message (top 10 jobs + count).
- Absent env var -> silently skip. No failure.

## Rules
- Paths via `config.paths`. No em dashes in digest text (use hyphens or restructure).
- Digest files are committed by the Actions workflow, giving a browsable history of every posting ever caught.
