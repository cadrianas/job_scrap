# SPEC: scrapers/academic.py (Phase 3b)

## Purpose
Adapters for academic and math job boards, covering Europe, Canada, the USA, Australia, and New Zealand. Universities are NOT scraped individually: nearly all universities in these regions post through a handful of aggregators, several with RSS or structured feeds. One adapter per aggregator covers hundreds of institutions.

## Sources and access methods

### Tier A: structured feeds (build first)

**jobs.ac.uk** (UK universities, Bristol/Oxford/Cambridge/Imperial etc.)
- RSS feeds per category: e.g. `https://www.jobs.ac.uk/feeds/...` for mathematics-and-statistics, computer-science, health-and-medical.
- Verify current feed URLs on their site (they publish an RSS index page).
- Parse with stdlib `xml.etree.ElementTree`. Fields: title, link, pubDate, description (location often embedded in description; best-effort extract, else "").

**jobbnorge.no** (nearly ALL Norwegian universities: Oslo, NTNU, Bergen, Tromso)
- Public search with structured listing pages; check for RSS/JSON before falling back to HTML parsing.

**EURAXESS** (EU-wide research jobs portal, includes Finnish and Danish universities)
- Confirmed 2026-07-26: `/jobs/search` is server-rendered Drupal (no JS needed). Despite the visible `<form method="post">` for the facet UI, the site's own schema.org `SearchAction` reveals a plain GET deep-link format that works standalone, with no session or cookies: `GET https://euraxess.ec.europa.eu/jobs/search?f[0]=<facet>:<value>&f[1]=<facet>:<value>&page=N` (URL-encode brackets/colons: `f%5B0%5D=keywords%3Adata+scientist`). Confirmed facets: `keywords` (free text), `job_research_field` (numeric taxonomy ID, e.g. `78` = Computer science), `job_country` (numeric taxonomy ID, e.g. `757` = Denmark). IDs are read off the `<select>` option values on the search page and are not guessed.
- Job cards are `<article class="ecl-content-item">`; title+link at `h3.ecl-content-block__title a`, location at `.id-Work-Locations .ecl-text-standard`. Only page 1 (10 results) is fetched per run, matching the simplicity of the other adapters -- broaden coverage by adding more `companies.json` entries with different facet combinations rather than paginating one entry.
- Filter server-side by research field, country, and/or keyword to keep volume sane (unfiltered is ~9000 results).

**Jobindex.dk** (Denmark's largest general job board)
- Normally out of scope as a general job board (see "General job boards" below), but approved 2026-07-26 as a named exception for Danish coverage.
- Confirmed 2026-07-26: publishes a plain RSS 2.0 feed per search query, no auth, no bot protection: `GET https://www.jobindex.dk/jobsoegning.rss?q=<query>`. Parse with stdlib `xml.etree.ElementTree` exactly like jobs.ac.uk. `q` ORs the space-separated terms (Jobindex's own search semantics), so expect some noise -- same broad-then-filter tradeoff as any keyword search, tightened downstream by `filters.py`.

### Tier B: HTML parsing (build second)

**mathjobs.org** (AMS, global math positions incl. European)
- Plain HTML listing at `/jobs`. Stable, low-churn markup. Parse institution, title, deadline.
- Deadline is valuable: map it into the digest line.

**academicpositions.com** (strong Nordic/Benelux coverage)
- HTML listing pages with country filters, e.g. /jobs/country/finland. Paginated.

**Varbi / ReachMee hosted pages** (many Swedish universities: KI, KTH, Gothenburg, Umea)
- Swedish universities each have a Varbi subdomain (e.g. `uu.varbi.com`). These are uniform enough that one Varbi adapter with the subdomain as `identifier` works like an ATS adapter. Treat as its own small adapter: `scrapers/varbi.py`.

### Tier C: North America

**Academic Jobs Online** (academicjobsonline.org)
- Global aggregator with particularly strong coverage of US and Canadian math/stats/economics/CS positions. Structured listing pages, filterable by discipline. Reuses the same `academicjobsonline` adapter type regardless of which country's postings are being pulled; region comes from `regions` in `companies.json`, not from the source.

**HigherEdJobs** (higheredjobs.com)
- Large, general US higher-ed job board. Publishes category-based RSS feeds (check their feeds page for current URLs, e.g. a "Data Science" or "Science - Math/Statistics" category). Parse like jobs.ac.uk.

**HERC** (Higher Education Recruitment Consortium, hercjobs.org)
- US regional consortia (e.g. HERC Northern California, HERC Upper Midwest) aggregate postings from member universities. Check whether a combined national search exists with a structured endpoint before adding per-region entries.

**University Affairs** (universityaffairs.ca)
- The main Canadian academic job board; publishes an RSS feed of new postings. Good primary source for Canadian university roles.

**CAUT Job Board** (caut.ca, Canadian Association of University Teachers)
- Secondary Canadian source; cross-check against University Affairs for overlap before adding both.

### Tier D: Australia / New Zealand -- needs research before coding
No aggregator here is confirmed with the same confidence as the sources above. Candidates to verify manually (structured feed or stable JSON/HTML, not a general job board covered by a ToS like Seek): university-consortium job boards, discipline-specific mailing-list-turned-webpage boards (common in AU/NZ math and stats departments), and whether academicpositions.com or Academic Jobs Online have meaningful AU/NZ coverage already. Do not add an `ats` value or companies.json entries for this region until a real source is confirmed, per the verification rule below.

### Individual university pages
Default posture is still to prefer aggregators over per-university entries -- one university adds one company's worth of coverage for a lot of upkeep, and nearly all institutions already post through the aggregators above. That said, an individual university can be added on explicit request if there's a real reason to want that specific institution's listings directly.
- **Aalborg University (aau.dk)**: investigated 2026-07-26. The listing at `vacancies.aau.dk` is a Next.js page whose vacancy cards are fetched entirely client-side after load -- confirmed by diffing a plain `requests`-style fetch (no job data, only nav/CMS content) against the browser-rendered page (full list with titles/deadlines). No underlying JSON endpoint was found in the shipped JS bundles or via network inspection after a real effort to locate one. Per Hard Rule 5 (no browser automation), this stays `ats: "unknown"`, `enabled: false` until someone finds the real data source (or AAU's postings show up via EURAXESS instead, which already indexes Danish universities).

### General job boards
Default posture is still to skip general job boards (Seek.com.au, Indeed, LinkedIn) -- they actively police scraping and a personal job-search tool has no standing to contest that. **Named exceptions below have been individually reviewed and approved; this is not a blanket policy change.**
- **Jobindex.dk**: approved 2026-07-26, see Tier A above (clean public RSS feed, no bot protection).
- **Jobnet.dk** (Danish public employment service): approved 2026-07-26 in principle, but investigated and found technically blocked: it has a real public JSON API (`jobnet.dk/bff/FindJob/Search`, discovered via browser devtools) but every request -- including ones replaying the exact cookies and Referer a browser sends -- gets a `401` from its `myracloud` WAF. This isn't a `requests`-vs-fetch header difference we can fix; it looks like bot-mitigation keyed on something (TLS fingerprint, a JS challenge) that a plain HTTP client can't reproduce. Getting past that would mean actively defeating bot detection, which is a different and more aggressive thing than scraping a public feed, so this stays `ats: "unknown"`, `enabled: false`.

### ResearchGate and Nature Careers
- **ResearchGate**: approved 2026-07-26 in principle, but `researchgate.net/jobs` returns `403` to a plain `requests` GET (confirmed 2026-07-26) -- it's actively bot-walled on top of the ToS restriction, not just a policy call on our side. Stays `ats: "unknown"`, `enabled: false`.
- **Nature Careers**: approved 2026-07-26. Turns out not to need a dedicated adapter at all -- `nature.com/naturecareers/jobs/` (Madgex-powered) is plain server-rendered HTML with job links matching the existing `generic` adapter's href pattern (`/naturecareers/job/<id>/<slug>/`) out of the box. Added with `ats: "generic"`, same as Polestar/Embark Studios.

## companies.json integration
Academic boards are entries like any company, with new `ats` values:
```json
{"name": "jobs.ac.uk - Maths & Stats", "ats": "jobsacuk", "identifier": "<feed-url-or-category>", "regions": ["uk"], "tier": 1, "enabled": true},
{"name": "Jobbnorge", "ats": "jobbnorge", "identifier": "<search-or-feed>", "regions": ["norway", "nordics"], "tier": 1, "enabled": true},
{"name": "EURAXESS - Math/Stats", "ats": "euraxess", "identifier": "f%5B0%5D=job_research_field%3A78", "regions": ["europe"], "tier": 1, "enabled": true},
{"name": "Jobindex - Data Science", "ats": "jobindex", "identifier": "q=data+scientist", "regions": ["denmark"], "tier": 2, "enabled": true},
{"name": "MathJobs", "ats": "mathjobs", "identifier": "https://www.mathjobs.org/jobs", "regions": ["global"], "tier": 2, "enabled": true},
{"name": "Uppsala University", "ats": "varbi", "identifier": "uu.varbi.com", "regions": ["sweden", "nordics"], "tier": 1, "enabled": true},
{"name": "Academic Jobs Online - Math/Stats/CS", "ats": "academicjobsonline", "identifier": "<discipline-query>", "regions": ["usa", "canada", "global"], "tier": 1, "enabled": true},
{"name": "HigherEdJobs - Data Science", "ats": "higheredjobs", "identifier": "<feed-url>", "regions": ["usa"], "tier": 2, "enabled": true},
{"name": "University Affairs", "ats": "universityaffairs", "identifier": "<feed-url>", "regions": ["canada"], "tier": 1, "enabled": true}
```
The adapter registry in main.py maps each new ats string to its module. No changes to Job, dedup, notify, or the pipeline: an academic posting is just a Job whose `company` is the board or university name.

## Mapping notes
- `posted_date`: RSS pubDate -> ISO date. Where only a deadline exists (mathjobs), leave posted_date "" and append the deadline to the title as " [deadline YYYY-MM-DD]" so it survives into the digest without schema changes.
- `location`: country/city where the feed provides it, else "".

## Volume control
Academic boards are high-volume. Unlike company adapters (broad-then-filter), academic adapters SHOULD filter at source where the board supports it (category feeds, field facets, country params). Source-side filtering by field is not a violation of the broad-then-filter principle; it is equivalent to choosing which companies to scrape.

## Errors -> ScraperError
Same contract as all adapters. Feed schema changes are the main risk; a zero-result parse on a board that yielded results yesterday should log a loud warning (health tracker makes this visible).

## Verification before coding
Each source's exact feed/endpoint URL must be confirmed manually (browser devtools or the site's RSS index) and recorded in companies.json. Do not code against the illustrative URLs in this spec.
