# Handoff

Working notes for picking this project up in a fresh session. Rewritten 2026-07-29 (previous
version, written 2026-07-27, was superseded by everything below: the whole `ROADMAP.md`
four-phase plan it referenced has since been completed and merged, so that file has been folded
into this one and removed rather than kept as a second, overlapping document).

Read `CLAUDE.md` first (hard rules), then `PLAN.md` (phases). This file covers only what is
true *right now* and what to do next.

## Current state

The automation goal ("wake up to a digest") is live and working. Repo is
`cadrianas/job_scrap`, **private**, on GitHub Actions with `.github/workflows/daily_scrape.yml`
running daily at 06:00 UTC plus `workflow_dispatch` for manual runs. The last several scheduled
runs have succeeded and pushed real state back to `main`. A run takes about 33 minutes.

`config/companies.json`: **284 entries, 234 enabled, 50 disabled.**

Enabled breakdown by adapter:

| ats | count |
|---|---|
| workday | 71 |
| generic | 78 |
| greenhouse | 40 |
| lever | 15 |
| ashby | 13 |
| workable | 6 |
| smartrecruiters | 5 |
| breezyhr | 2 |
| bamboohr | 1 |
| eightfold | 1 |
| euraxess | 1 |
| jobindex | 1 |

`data/jobs_seen.csv` is primed with real state (~29k rows) from live runs, not the placeholder
193-row file from before the pipeline went live. Digests land in `data/digests/` and are
committed by the workflow; `main.py --validate` passes.

The 50 disabled entries are all `ats: "unknown"` with a documented reason in
`RESEARCH_NOTES_companies.md`, which also documents every vendor found and why each remaining
company is not scrapable -- read that file before re-investigating something, since roughly half
of what looks like "still broken" has already been checked and ruled out for a specific reason.

## What happened, phase by phase (2026-07-27 through 2026-07-29)

**Phase 0 (PR #2):** Made the daily loop trustworthy. Fixed `main.py` reporting the pre-filter
job count instead of the post-filter count in the digest/commit message (a run could say "24452
new jobs" while the digest held a handful). Added a `git pull --rebase` retry to the workflow's
push step so a human push to `main` mid-run doesn't lose that run's digest -- this had actually
happened on the very first real run. Bumped `actions/checkout` and `actions/setup-python` to
their current major versions.

**Phase 1 (PRs #3, #4):** Fixed Workday instance discovery, which turned out to affect 12
tenants (14 registry entries), not just Accenture as originally suspected. 9 tenants got an
explicit `"tenant/site|wdN"` override (new identifier convention, see
`specs/SPEC_scraper_workday.md`) after live-confirming the real instance number, including
Vertex Pharmaceuticals at `wd501` -- well outside any reasonable guess-list range. Net-A-Porter's
`ynap` tenant had moved entirely to `luxexperience/LuxExperience_Careers` after a 2025
acquisition. Then triaged the other 32 of the original 44 CI failures: 4 fixed in place with
adapters already in the codebase (Ada, Clio, Tyro Payments, Getir), 6 confirmed bot-walled,
3 left genuinely unresolved (see "Still open" below), and 17 confirmed live on vendor platforms
this project had no adapter for -- which fed directly into Phase 2.

**Phase 2 (PR #5):** Built `scrapers/json_boards.py`, one file covering five vendor APIs (Ashby,
SmartRecruiters, Workable, Breezy HR, BambooHR) that dispatch internally on `company.ats`,
following the `scrapers/academic.py` precedent rather than five near-empty files. Every vendor's
request shape was verified live before coding -- notably, SmartRecruiters and Workable both
return HTTP 200 with an empty result for a nonexistent slug, so a bare 200 never confirms an
identifier is correct; real job content (or an independent check) does, and that rule is written
into `specs/SPEC_scraper_json_boards.md` as an ongoing requirement for future entries, not just a
one-time note. 27 companies fixed or newly enabled, well above the original ~10-company estimate.

**Phase 3 (PR #6):** Checked the SuccessFactors cluster on the premise that it isn't uniformly
unscrapable -- some tenants (Canal+, Coloplast, Zurich Insurance, Scotiabank, already working)
expose a server-rendered `/search/` page distinct from the client-rendered SPA landing page.
6 of 10 candidates had the same server-rendered equivalent and got fixed with no new adapter,
just a corrected `generic` identifier. The other 4 (Lundbeck, EY Australia, EY New Zealand,
Bausch Health) only turned up nav/marketing links, not real postings, at every URL guessed --
confirmed via `scrapers.generic._looks_like_job_link` directly, not by eyeballing href counts,
which is what caught the false positives in the first place.

## Still open

**7 companies need real browser devtools work, not another URL guess.** All were checked this
session and none can be resolved by guessing at endpoints:
- **Vidyard**: not on Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Breezy, or BambooHR.
  Their own `/careers/` page 403s.
- **King** (Workday tenant `activision`): `careers.king.com` shows Eightfold markers in raw
  HTML, but the `domain` param `scrapers/eightfold.py` needs could not be guessed -- both
  `king.com` and `careers.king.com` return `"Tenant not identified"`.
- **Telenor** (Workday tenant `telenorgroup`): resolves but returns HTTP 422 on the real CXS
  POST, not 404. Instances above wd150 don't resolve in DNS for this tenant at all.
- **Lundbeck**: on the shared multi-tenant `career5.successfactors.eu` domain (the same one SAP
  was on before its fix); their own branded domain is nav-links-only.
- **EY Australia / EY New Zealand**: confirmed SuccessFactors-backed, but every URL tried
  (country pages, global `viewalljobs`, a guessed country filter that 404s) returns only nav
  links or an error page.
- **Bausch Health**: both the registry's `/search` identifier and a `/go/` category page
  (matching the pattern that worked for Canal+) return zero real hits.

An attempt to use the in-app browser tool to capture King's real XHR call was made this session
and the tool became unresponsive before completing. Worth retrying, or doing manually in a real
browser and handing the captured request over.

**Tier 4: case-by-case API discovery (~13 companies), not started.** Atlassian, TomTom, Unity
Technologies, Sharesies, CGI, KBC Bank, Nordea, ASOS, Booking.com (iCIMS), Trade Me, and the
Phenom People cluster (Just Eat Takeaway, BCG Australia, PwC Australia). Same devtools
requirement as above. Two data points already collected: Trade Me's Cornerstone endpoint returns
401 (auth required), and a guessed Phenom widget payload returned `{"status":"failure"}` -- not
disproven, but needs a real captured request.

**GitHub Actions minutes:** at ~33 min/day, daily runs consume roughly 1,000 of the 2,000 free
monthly minutes for a private repo (about 50%), which is not actually tight despite earlier
concern that it might be. Deliberately deferred rather than acted on -- check real usage
**mid-August 2026** before doing anything. If it turns out to matter, the two options already
scoped are (a) split into a public code/workflow repo plus a private data repo pushed to via a
PAT (solves both the minutes budget and privacy, but is a real architecture change), or (b) add
concurrency with per-domain rate limiting to the existing single private repo (stays private,
needs a deliberate spec decision since it touches Hard Rule 7). **Do not make the repo public**
without re-confirming first -- that was tried once this session and reverted immediately, because
`data/digests/*.md` and `WATCHLIST.md` reveal which companies and roles are being watched, which
the user did not want publicly visible.

**`main.py`'s 50%-failure threshold for exit code 2** has not been revisited since the fixes
above. Worth checking whether it's still the right number now that the real failure rate is much
lower than the 20% it was calibrated against.

## Do not pursue

**Bot-walled (13): Bayer, Citadel, Judo Bank, Revolut, Bankinter, Datacom, H&M, Orsted, Tesla,
Schneider Electric, EDF, Tesco, Uber.** These return 403 (or 406 for Uber) from Cloudflare or
Akamai on a plain GET, and keep doing so with full browser-style headers. Carrefour is
inconsistent -- 403 from the GitHub Actions runner in a real run, 200 from other vantage points --
which reads as Cloudflare scoring datacenter IP ranges harder, not as the wall coming down;
treated as still bot-walled since production is what matters. Getting through any of these means
TLS-fingerprint spoofing or CAPTCHA handling, which is actively defeating bot detection rather
than reading a public source. That is a deliberate line this project should not cross, and Hard
Rule 5 blocks the usual browser-automation workaround anyway.

**Structurally unresolvable (~10):**
- Deloitte, KPMG (global): genuinely federated per-country networks, no unified board exists. The
  real fix is per-country entries, not an adapter.
- Credit Suisse, Decibel Therapeutics: merged into UBS and Regeneron respectively, both already
  covered by existing entries. Kept disabled rather than deleted, deliberately.
- Hnry: a `mailto:` link is the only apply mechanism. No job board exists.
- IAG New Zealand: no own careers portal, relies entirely on Seek/Indeed (both excluded).
- Seek: is itself the general job board excluded on ToS grounds.
- WiseTech Global: server-rendered and working, just genuinely zero openings at check time.
  Nothing to fix, may start working on its own.
- Sonic Healthcare: original URL 404s, no working replacement found.

Kiwibank and McKinsey Australia (and, separately, McKinsey & Company's main entry) were
unreachable entirely -- connection resets/timeouts, not a bot-wall signature. Possibly transient
or geo-related, worth one retry later from a different vantage point (e.g. the GitHub Actions
runner itself, not a local machine).

## Conventions and gotchas

- **Always test with `--dry-run`.** `python main.py --companies "Name"` without it writes to
  `data/jobs_seen.csv`, `data/scraper_health.csv`, `data/digests/`, and `data/NEW_JOBS_COUNT`.
  This has been learned the hard way more than once and required a manual revert each time.
- **Do not trust "this page looks scrapable."** Verify a candidate `generic` entry by running its
  URL through `scrapers.generic._looks_like_job_link` directly, not by eyeballing an href count.
  Several companies in the SuccessFactors cluster had 20-30 href matches on their existing URL
  that turned out to be nav/marketing links ("Careers in Assurance"), not real postings -- the
  function call is what caught it, a grep for job-shaped hrefs was not enough.
- **SmartRecruiters and Workable both return HTTP 200 for a nonexistent slug.** Same trap as
  above, one level deeper: a bare 200 (or even a company-name match, for Workable) is not proof
  an identifier is right if the result set is empty. Confirm with real job content, or an
  independent check like the vendor's own public careers page, before enabling.
- Hard Rule 1: every path comes from `config/paths.py`. No exceptions, including tests.
- Hard Rule 2: spec first. If a change contradicts a spec, update the spec in the same commit.
- Style: no em dashes in documentation, digests, or any user-facing text.
- The venv at `.venv/` has `requests` and `beautifulsoup4`. Activate it before running anything,
  otherwise `main.py` fails on `ModuleNotFoundError: requests`.
