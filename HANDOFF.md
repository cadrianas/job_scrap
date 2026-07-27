# Handoff

Working notes for picking this project up in a fresh session. Written 2026-07-27.

Read `CLAUDE.md` first (hard rules), then `PLAN.md` (phases). This file covers only what is
true *right now* and what to do next.

## Current state

`config/companies.json`: **284 entries, 218 enabled, 66 disabled.**

Enabled breakdown by adapter:

| ats | count |
|---|---|
| workday | 69 |
| generic | 72 |
| greenhouse | 46 |
| lever | 28 |
| eightfold | 1 |
| euraxess | 1 |
| jobindex | 1 |

Everything on the `PLAN.md` file map exists and is real code (no stubs). `python main.py --validate`
passes. The 66 disabled entries are all `ats: "unknown"` with a documented reason in
`RESEARCH_NOTES_companies.md`.

**The automation goal is still blocked: this directory is not a git repository.**
`.github/workflows/daily_scrape.yml` exists and looks correct, but there is no `.git`, no remote,
and nothing to push to. Until someone runs `git init` and creates a GitHub remote, the daily
scrape cannot actually run. This is the single biggest open item if the goal is "wake up to a
digest."

## Known bugs (both real, both verified)

1. **Workday instance discovery misses high `wdN` numbers.**
   `scrapers/workday.py` hardcodes `_CANDIDATE_INSTANCES = ["wd1", "wd3", "wd5", "wd2", "wd4"]`.
   Accenture's tenant is actually on **wd103** (confirmed live at
   `accenture.wd103.myworkdayjobs.com/AccentureCareers`), so both the `Accenture` and
   `Accenture New Zealand` entries fail every run with "no working Workday instance found".
   Fixing this needs care: naively widening the range multiplies requests per company. Consider
   a fallback pass after the fast list fails, or caching a discovered instance per tenant in
   `companies.json`. Update `specs/SPEC_scraper_workday.md` in the same commit (Hard Rule 2).

2. **Halter's Lever board is dead and the entry is silently failing.**
   `Halter` is enabled as `lever` / `halter`, but that board now returns 404 from both the US and
   EU Lever APIs. Halter has migrated to Ashby: `api.ashbyhq.com/posting-api/job-board/halter`
   returns **276 live jobs**. The entry is a tier-1 NZ company currently contributing nothing.
   It gets fixed for free once an Ashby adapter exists (see below).

**Worth doing because of #2:** a full health pass over all 218 enabled entries to find other
silently-dead boards. Halter was only caught by accident. Something like
`python main.py --dry-run` (full run, no `--companies` filter) and then reading
`data/logs/run_*.log` for errors and for companies returning 0 jobs. Budget several minutes
because of the 1.5s inter-company sleep.

## Next work: verified and ready to build

All endpoints below were **live-verified on 2026-07-27** (real HTTP calls, real job counts).
They are public, unauthenticated JSON APIs and need no browser automation. This satisfies the
"verify before coding" rule already, so it is safe to build directly against them.

### Tier 1: five vendor JSON adapters (~10 companies, plus fixes Halter)

| Vendor | Endpoint | identifier convention | Unlocks (verified job counts) |
|---|---|---|---|
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{slug}` | board slug | Ramp `ramp` (118), Partly `partly.com` (47), Lovable `lovable` (67), **Halter `halter` (276, fixes bug #2)** |
| SmartRecruiters | `https://api.smartrecruiters.com/v1/companies/{id}/postings` | company id | Deloitte NZ `DeloitteNZ` (128), KPMG Australia `KPMGAustralia1` (79), Carsales `carsales` (25) |
| Workable | `https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true` | account slug | Nuvei `nuvei` (58). Timely `timely` returns 0 -- genuinely no openings, not a failure |
| Breezy HR | `https://{slug}.breezy.hr/json` | subdomain | Serato `serato-limited` (11), Plexure `plexure` (5) |
| BambooHR | `https://{slug}.bamboohr.com/careers/list` | subdomain | Gentrack `gentrack` (16) |

Notes:
- SmartRecruiters paginates (`limit`/`offset`, `totalFound` in the response).
- Plexure has rebranded to "TASK" but the Breezy slug is still `plexure`.
- Scale AI was **not** confirmed on Ashby. Guessed slugs returned the same shell as a known-bad
  slug, so do not add it without finding the real slug first.

**Architecture suggestion.** These five differ only in URL template and field mapping, so the
cheapest shape is one `scrapers/json_boards.py` with a per-vendor config table dispatching on
`company.ats`, following the `scrapers/academic.py` precedent. Each future vendor then costs
about ten lines of config. The tradeoff: this bends `PLAN.md` design principle 2 ("each ATS
adapter is an independent module"). Five separate files matching `greenhouse.py` is equally
valid, just more boilerplate. Either way:
- write the spec first (Hard Rule 2), e.g. `specs/SPEC_scraper_json_boards.md`
- add the new `ats` values to **both** `ADAPTERS` and `KNOWN_ATS_VALUES` in `main.py`
- add the identifier conventions to `specs/SPEC_companies_json.md`

### Tier 2: widen the generic adapter's href patterns (3 companies, one-line change)

`scrapers/generic.py` has `_JOB_HREF_HINTS = ("/job/", "/jobs/", "/careers/", "/position/",
"/opening/", "/vacanc")`. Adding `jobdetail`, `ajid=`, and `/vacancy` was tested and rescues
three currently-disabled companies that already serve real job links in raw HTML:

- ASB Bank (`https://careers.asbgroup.co.nz/search`) -- 10 links
- Tower Insurance (`https://careers.tower.co.nz/search`) -- 3 links
- Woolworths Group (`https://careers.woolworthsgroup.com.au/en_GB/apply/search-jobs`) -- 12 links

Update `specs/SPEC_scraper_generic.md` in the same commit. Re-run a few existing `generic`
companies afterwards to confirm the wider patterns do not pull in navigation junk.

**JSON-LD parsing** was also evaluated as a generic enhancement. It is worth having in general,
but it does **not** rescue Klarna as hoped: Deel's JSON-LD is a bare `ItemList` containing only
`url` and `position`, with no titles, and the URLs are UUIDs with no slug to derive a title
from. Klarna needs per-job fetches or a different endpoint.

## Lower-confidence work

**Tier 3: SuccessFactors cluster (~10 companies).** Novo Nordisk, SAP, Lundbeck, EY Australia,
EY New Zealand, Deloitte Australia, One NZ, Zespri, AgResearch, Bausch Health. Important nuance:
SuccessFactors is *not* uniformly unscrapable. Canal+, Coloplast, Zurich Insurance, and
Scotiabank all run it and already work via `generic`, because their tenants expose
server-rendered `/search` or `/go/...` pages. So the play is not a new adapter, it is checking
whether each client-rendered tenant has an equivalent server-rendered search URL. Cheap per
company, uncertain hit rate.

**Tier 4: case-by-case API discovery (~13 companies).** Atlassian, TomTom, Unity Technologies,
Sharesies, CGI, KBC Bank, Nordea, ASOS, Booking.com (iCIMS), Trade Me, and the Phenom People
cluster (Just Eat Takeaway, BCG Australia, PwC Australia). These need browser devtools work of
the kind that cracked Lovable and EURAXESS. Two data points already collected: Trade Me's
Cornerstone endpoint returns **401 (auth required)**, and a guessed Phenom widget payload
returned `{"status":"failure"}` -- not disproven, but it needs a real request captured from a
browser session.

## Do not pursue

**Bot-walled (7): Bayer, Citadel, Judo Bank, Revolut, Bankinter, Datacom, H&M.** These return
403 from Cloudflare or Akamai on a plain GET, and keep doing so with full browser-style headers.
Getting through means TLS-fingerprint spoofing or CAPTCHA handling, which is actively defeating
bot detection rather than reading a public source. That is a deliberate line this project should
not cross, and Hard Rule 5 blocks the usual browser-automation workaround anyway. Also a losing
maintenance battle.

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

Kiwibank and McKinsey Australia were unreachable entirely (connection resets/timeouts, not a
bot-wall signature). Possibly transient or geo-related, worth one retry later.

## What happened in the previous session (2026-07-26/27)

1. **Added 4 companies on request:** Embark Studios (`generic`, 18 jobs), Novartis Ireland
   (`workday`, same tenant as existing Novartis entry, 500 jobs), plus Lovable and University of
   Gothenburg as disabled (Ashby and ReachMee respectively, neither supported).
2. **Added 6 academic/job-board sources on request.** Built `scrapers/academic.py` with two new
   adapters: `euraxess` (10 jobs) and `jobindex` (20 jobs), both wired into `main.py`. Nature
   Careers needed no new code and went in as `generic` (78 jobs). Aalborg University, Jobnet.dk,
   and ResearchGate went in disabled, each with a specific technical blocker.
   This required revising `specs/SPEC_scraper_academic.md`, which had blanket exclusions for
   general job boards and for ResearchGate/Nature Careers. **That was an explicit user decision
   to accept the ToS risk for this personal tool, not a default policy change.** Seek, Indeed,
   and LinkedIn remain excluded.
3. **Ran a 7-way parallel ATS research pass over 86 unknown companies, resolving 23 into working
   entries** (4 workday, 1 greenhouse, 18 generic). Registry went 195 -> 218 enabled.
   `WATCHLIST.md` and `RESEARCH_NOTES_companies.md` were both updated; the latter now documents
   every vendor found and exactly why each remaining company is not scrapable.

## Conventions and gotchas

- **Always test with `--dry-run`.** `python main.py --companies "Name"` without it writes to
  `data/jobs_seen.csv`, `data/scraper_health.csv`, `data/digests/`, and `data/NEW_JOBS_COUNT`.
  This was learned the hard way and required a manual revert.
- **Do not trust "this page looks scrapable."** Verify a candidate `generic` entry by running its
  URL through `scrapers.generic._looks_like_job_link` directly. During the research pass this
  caught two false positives where real job content existed but the href patterns did not match,
  which would have produced silently-empty scrapes.
- Hard Rule 1: every path comes from `config/paths.py`. No exceptions, including tests.
- Hard Rule 2: spec first. If a change contradicts a spec, update the spec in the same commit.
- Style: no em dashes in documentation, digests, or any user-facing text.
- The venv at `.venv/` has `requests` and `beautifulsoup4`. Activate it before running anything,
  otherwise `main.py` fails on `ModuleNotFoundError: requests`.
