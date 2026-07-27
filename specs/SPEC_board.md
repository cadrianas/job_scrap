# SPEC: board.py

## Purpose
A persistent, browsable "apply board": every job ever recorded in
`jobs_seen.csv` that matches the target role filters (`filters.py`),
regenerated in place each time it's run. This is different from
`notify.py`'s digest, which is a dated, one-shot file of *new* jobs only
-- the board is the standing "everything currently worth applying to"
view, so a posting doesn't get lost once it scrolls off a daily digest.

## Why this exists
Requested directly: the user wants an easy way to see job title, company,
and the apply link in one place, for jobs matching their target roles
(data science, data analytics, mathematical modelling, mathematical
epidemiology / public health modelling), without re-reading old digest
files.

## Inputs
- `dedup.load_seen()` -- every job ever scraped (dedup_key, company,
  title, url, first_seen, last_seen).
- `companies.json` -- for tier and region, to sort consistently with the
  digest.

## Output
Two files, both regenerated (overwritten) on every run, not appended:
- `BOARD_HTML_FILE` (`data/job_board.html`): a searchable/filterable
  HTML page. Company, title (linked to the apply URL), tier, first_seen.
  No server, no build step -- plain HTML/CSS/JS, opens directly in a
  browser.
- `BOARD_CSV_FILE` (`data/job_board.csv`): the same filtered rows as a
  flat CSV (`company,title,url,first_seen`) for anyone who'd rather
  filter/sort in a spreadsheet.

## Filtering and sorting
- A row is included only if `filters.matches(title)` is true. Rows
  representing jobs whose company no longer exists in `companies.json`
  (deleted from the registry) still count if their title matches --
  fall back to tier 3 / no region boost per `filters.apply`'s existing
  handling of an unknown company.
- Sort order: same as `filters.apply` (tier, then priority region, then
  company name) -- reuses that function directly rather than
  re-implementing sorting.

## API
- `build_board() -> None` : reads state, writes both output files.

## CLI
- `python board.py` : regenerates both files from current `jobs_seen.csv`
  state. Not wired into `main.py`'s run automatically (kept separate so a
  broken board render can never affect the scrape/digest pipeline); run
  it manually or add a second step in the GitHub Actions workflow later.

## Rules
- All paths via `config.paths`. No path literals.
- Read-only with respect to `jobs_seen.csv` and `companies.json` -- this
  script never writes scraper state, only its own two output files.
- No em dashes in any generated text, per project style rules.
