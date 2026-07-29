# Company Research Notes: Regional Expansion (Canada, USA, Australia, New Zealand)

Working notes from the research pass that populated `config/companies.json` with the first
batch of Canada/USA/Australia/New Zealand companies, plus a verification pass on the
biotech/pharma and fintech/tech tiers of the original European list. Not read by any script;
kept for whoever does the next research or coding pass. Every claim here was checked against a
live careers page or search result, not guessed, per the "verify before coding" rule in
`specs/SPEC_scraper_academic.md` applied to companies generally.

## What's in `config/companies.json` now

274 unique companies: Europe (now covering biotech/pharma, fintech/tech, consulting,
financial services/insurance, automotive/mobility, logistics, telecom, energy/utilities,
manufacturing, retail, streaming/media, startups, and space/defense), plus Canada, USA,
Australia, and New Zealand from the first research round. 190 have a confirmed or
best-effort ATS/URL and are `enabled: true`. 84 are `enabled: false` with `ats: "unknown"` --
real companies with real careers pages where the underlying platform could not be confirmed
or confirmed to be unsupported and un-scrapable even via the generic fallback.

### Important caveat on `generic` entries from this round

A large batch of `generic` entries added in the second research round (automotive, energy,
telecom, manufacturing, retail, and some consulting/insurance firms) are **not confirmed to be
plain server-rendered HTML** -- they're a verified, reachable careers URL where the research
agents could not confirm the actual ATS vendor, or confirmed a vendor known to render job
listings client-side via JavaScript (SAP SuccessFactors, Phenom People, SmartRecruiters,
TeamTailor, Oracle Taleo/Recruiting, Radancy). BeautifulSoup (the `generic` adapter's only
tool per Hard Rule 5 -- no browser automation) will likely return zero jobs from these until
someone inspects whether the page ships job data in the initial HTML or only via an XHR/JSON
call the adapter could hit directly instead. This is expected to surface as repeated
`ScraperError`s in the health tracker (Phase 4) rather than break anything, per Hard Rule 4,
but don't be surprised if a large fraction of the `generic`-tagged tier-1/2 companies
(Siemens, Shell's non-Workday-tagged listings, Allianz, Swiss Re, DHL, RWE, Vattenfall,
Rocket Internet, etc.) yield nothing without further work. Companies confirmed via a real
`greenhouse`/`lever`/`workday`/`eightfold` URL pattern (not `generic`) don't have this risk.

## Unsupported ATS platforms found in the wild

These showed up repeatedly enough that a dedicated adapter might be worth it before Phase 3/4
if key target companies live there:

- **SAP SuccessFactors** (`career5.successfactors.eu/...`, `career10.successfactors.com/...`,
  `careerX.successfactors.eu` style URLs): confirmed at Bayer, Lundbeck, SAP itself, Novo Nordisk,
  AgResearch, Bausch Health, Deloitte Australia, EY Australia, EY New Zealand, One NZ, Zespri.
  All confirmed client-rendered (zero job links in raw GET HTML) except Canal+ and Coloplast,
  whose SuccessFactors-hosted `/job/...` search pages happen to be server-rendered and are
  scraped today via `ats: "generic"` -- SuccessFactors client-vs-server rendering is inconsistent
  per tenant/template, always verify with a live curl before assuming either way.
- **Ashby** (`jobs.ashbyhq.com/...`): confirmed real boards at Ramp, Partly (slug `partly.com`),
  Lovable (`jobs.ashbyhq.com/lovable`), Halter (NZ, possibly mid-migration from Lever); Scale AI
  not confirmed (guessed slugs returned the same shell as a known-nonexistent slug). All are
  client-rendered SPAs with zero job data in raw HTML -- Ashby has no adapter in this project, so
  these stay `unknown`/disabled regardless.
- **ReachMee** (`webNNN.reachmee.com/ext/...`): University of Gothenburg (Swedish public-sector/
  academic ATS, common across Swedish universities and government agencies; not in the
  academic-source list in `SPEC_scraper_academic.md`)
- **SmartRecruiters**: confirmed real, scrapable-content boards at Deloitte New Zealand
  (`careers.smartrecruiters.com/DeloitteNZ`) and KPMG Australia (`smartrecruiters.com/ni/
  KPMGAustralia1/...`), both with real per-role links in their raw HTML -- but the links are
  off-domain / not path-routed in a way `generic`'s href filter catches, and SmartRecruiters
  itself isn't a supported `ats` value, so a dedicated adapter is the only way to use these.
  Carsales also confirmed on SmartRecruiters (domain-routed, same problem). Wise turned out to be
  self-hosted plain HTML that merely credits "SmartRecruiters Attrax" in its footer -- it's
  already scraped via `generic` today, no adapter needed.
- **Attrax** (SmartRecruiters' white-label product): Delivery Hero -- also self-hosted/server-
  rendered, already `generic`.
- **Cornerstone OnDemand** (`*.csod.com`): Trade Me (NZ) -- confirmed client-rendered SPA shell
  (`<div id="cs-root">`), zero job data in raw HTML.
- **Breezy HR**: Serato (NZ) and Plexure (rebranded "TASK", `plexure.breezy.hr/p/...`) both have
  real postings in raw HTML but the href pattern (`/p/...`) doesn't match `generic`'s hints.
- **Workable**: confirmed at Nuvei (`apply.workable.com/nuvei/`) and Timely
  (`apply.workable.com/timely/`) -- both client-rendered React shells, zero job links in raw HTML.
- **Deel Jobs** (`jobs.deel.com/...`): Klarna -- job data only inside a JSON-LD script block, no
  real `<a>` tags, client-rendered.
- **Phenom People**: Just Eat Takeaway, BCG Australia, PwC Australia (`jobs-au.pwc.com`) -- all
  confirmed client-rendered widgets, zero job links in raw HTML.
- **Avature**: Fonterra (category pages only, no individual postings), Macquarie Group and
  Spark New Zealand and Two Sigma and Woolworths Group (all confirmed Avature, but Macquarie/
  Spark/Two Sigma happen to be server-rendered and are scraped via `generic`; Woolworths'
  `/JobDetail/...` links don't match `generic`'s href hints despite being server-rendered, so it
  stays `unknown`).
- **Snaphire** (Apache Wicket-based, common in AU/NZ): ASB Bank and Tower Insurance -- both have
  real job titles in raw HTML but neither's href pattern (`/jobdetails/ajid/...`) matches
  `generic`'s hints, so both stay `unknown` despite real scrapable-looking content.
- **BambooHR**: Gentrack -- job list is fetched client-side via a WordPress admin-ajax proxy to
  `gentrack.bamboohr.com/jobs/embed2.php`; no job data in the raw GET.
- **Rippling** (`ats.rippling.com/<company>-careers/jobs`) -- newly seen vendor, confirmed at
  Zymeworks; server-rendered with real job links matching `generic`'s `/jobs/` hint out of the
  box. Worth remembering as a fingerprint for future research passes.
- **iCIMS**: Booking.com (`jobs.booking.com`, login-gated)
- **Oracle Cloud recruiting**: Hologic
- **Oracle Taleo**: UBS, BNP Paribas
- **Radancy**: Munich Re
- **TeamTailor**: Polestar, Embark Studios, Acast (Acast's tenant happens to be server-rendered,
  scraped via `generic`; LIC (NZ) is also Teamtailor and also server-rendered, `generic`), Koala
  (client-rendered for this tenant, stays `unknown`).
- **careers-page.com (custom SaaS)**: Getir
- **Magnolia CMS**: Atlassian (proprietary job-search widget, no fingerprinted vendor, client-rendered)
- **EPiServer/Optimizely**: Bain & Company Australia (React widget hitting a proprietary API)
- Confirmed genuinely federated with no single global identifier (not a research gap, just how
  the company is structured): Deloitte, Deloitte Australia, KPMG, KPMG (global)
- Confirmed merged/absorbed, no independent careers site remains: Credit Suisse (into UBS, already
  covered by the existing UBS entry), Decibel Therapeutics (into Regeneron)
- Custom/proprietary in-house portals confirmed scrapable via `generic` (server-rendered, no
  third-party ATS needed): D. E. Shaw Group, Vinted, Two Sigma (Avature, see above), Zurich
  Insurance (SuccessFactors-hosted but server-rendered)
- Custom/proprietary in-house portals confirmed NOT scrapable (client-rendered SPA, no job data
  in raw HTML, no vendor fingerprint to log): Amazon (NZ offices), Atlassian, CGI, Hologic,
  Scale AI, Sharesies, TomTom, Unity Technologies
- Blocked entirely by Cloudflare/Akamai bot-protection on a plain GET (403, even with full
  browser-style headers): Bankinter, Bayer, Citadel, Datacom, H&M, Judo Bank, Revolut
- Confirmed unreachable via HTTP (connection resets/timeouts on every attempt, not a bot-wall
  signature): Kiwibank, McKinsey & Company Australia
- No scrapable careers presence at all: Hnry (a `mailto:` link is the only "apply" mechanism),
  IAG New Zealand (relies solely on Seek/Indeed, both excluded), Sonic Healthcare (original URL
  404s, no working replacement found), WiseTech Global (server-rendered, genuinely zero current
  openings at check time, not a technical failure)

## Workday tenant/site pairs with confirmed `wdN` instance numbers

`SPEC_scraper_workday.md` has the adapter auto-discover the `wdN` instance number, but these
were observed directly during research and are worth a quick sanity check if the adapter's
discovery logic ever misses:

| Company | tenant/site | wd instance |
|---|---|---|
| Roche | roche/roche-ext | wd3 |
| Novartis | novartis/Novartis_Careers | wd3 |
| Amgen | amgen/Careers | wd1 |
| IQVIA | iqvia/IQVIA | wd1 |
| Parexel | parexel/Parexel_External_Careers | wd1 |
| Genmab | genmab/Genmab_Careers_Site | wd3 |
| Tempus | tempus/Tempus_Careers | wd5 |
| Syneos Health | syneoshealth/Syneos_Health_External_Site | wd12 |
| Zalando | zalando/ZalandoSiteWD | wd3 |
| Saxo Bank | saxobank/CareeratSaxoBank | wd3 |
| King | activision/King_External_Careers | wd1 (site lives under Activision's tenant, not a King-specific one) |
| Depop | etsy/Depop_Careers | wd5 (Depop is owned by Etsy) |
| Visa | visa/Visa | wd5 (observed once, Workday subdomain numbers can drift, confirm at runtime) |
| Vertex Pharmaceuticals | vrtx/Vertex_Careers | seen under both wd501 and wd5, confirm at runtime |
| Genentech | roche/ROG-A2O-GENE | same tenant as Roche, member of Roche group |
| Deutsche Bank | db/DBWebsite | -- |
| ING | ing/ICSNLDGEN | -- |
| BBVA | bbva/BBVA | -- |
| Santander | santander/SantanderCareers | -- |
| Maersk | maersk/Maersk_Careers | -- |
| Swisscom | swisscom/SwisscomExternalCareers | -- |
| Telia | teliacompany/Telia_careers | -- |
| Telenor | telenorgroup/TelenorGroup_careers | -- |
| Shell | shell/ShellCareers | -- |
| BP | bpinternational/bpCareers | -- |
| Iberdrola | iberdrola/Iberdrola | -- |
| Lego | lego/LEGO_External | -- |
| Sandvik | sandvik/sandvik-jobs | multiple divisional Workday sites exist (coromant-jobs, walter-jobs), not independently load-tested |
| Net-A-Porter | ynap/YNAP_Careers | -- |
| Airbus | ag/Airbus | -- |
| Thales | thales/Careers | -- |
| Philips | philips/jobs-and-careers | -- |
| ASML | asml/ASMLEXT1 | -- |
| Temenos | temenos/Temenoscareers | -- |

## Cross-region duplicates merged during compilation

A few companies appeared in more than one regional research pass and were merged into a
single `companies.json` entry with combined `regions` rather than duplicated:
- **Stripe**: had `unknown` from the EU pass, confirmed `greenhouse/stripe` from the US pass -- merged, uses the US-confirmed identifier globally.
- **Xero**: `unknown` from the Australia pass, confirmed `lever/xero` from the New Zealand pass (Xero is NZ-headquartered) -- merged.
- **Westpac**: appeared as both "Westpac" (AU) and "Westpac NZ", both pointing at the same `workday` tenant `westpacnz/Westpac_Careers` -- merged into one entry covering both regions.
- **Novartis**: same pattern applied for a later Ireland-specific careers link request -- added as a separate "Novartis Ireland" entry (regions `cork, ireland`) pointing at the same confirmed `workday` tenant `novartis/Novartis_Careers` rather than merging, since the tenant returns the full global job list either way (confirmed: 500 jobs from a single-company test run) and dedup collapses the overlap.

## Academic / job-board sources added 2026-07-26

Six sources requested: aau.dk, Jobnet.dk, Jobindex.dk, EURAXESS, ResearchGate, Nature Careers.
Full technical findings live in `specs/SPEC_scraper_academic.md` (search "2026-07-26"); summary:

- **EURAXESS** and **Jobindex.dk**: real, working, unauthenticated endpoints found (a GET-based
  facet query and an RSS feed respectively). Built `scrapers/academic.py` with `ats: "euraxess"`
  and `ats: "jobindex"` to handle them; both wired into `main.py` and enabled in
  `config/companies.json`.
- **Nature Careers**: turned out to need no new code -- its Madgex-powered listing page is plain
  server-rendered HTML that the existing `generic` adapter already handles. Added as `ats:
  "generic"`, enabled.
- **Aalborg University (aau.dk)**, **Jobnet.dk**, **ResearchGate**: each has a real technical
  barrier (client-only rendering with no found API; a WAF that 401s non-browser requests even
  with correct cookies/referer; a hard 403 bot-wall) that a `requests`-only scraper cannot get
  past without moving into actively defeating bot detection. Added as `ats: "unknown"`, `enabled:
  false` with the specifics in the spec, not silently dropped.

Note: adding Jobnet.dk/Jobindex.dk and reconsidering ResearchGate/Nature Careers required
revising `SPEC_scraper_academic.md`'s blanket exclusions for general job boards and
ResearchGate/Nature Careers -- this was an explicit user decision to accept the ToS/scraping risk
for this personal tool, not a default policy change; Seek/Indeed/LinkedIn remain excluded.

## Not yet researched

Every category from the user's original European company list has now had at least one
verification pass. Still open: a confirmed academic/postdoc job aggregator for Australia/New
Zealand was not found with confidence (see `specs/SPEC_scraper_academic.md` Tier D) -- Seek
and other general job boards were explicitly excluded for the same ToS reasons LinkedIn
scraping is excluded. Also open: whether any of the four new regions (Canada/USA/Australia/NZ)
need the same depth of coverage across consulting/finance/energy/manufacturing/etc. that
Europe now has -- so far those regions were researched with a tech/fintech/biotech/consulting
bias, not the full category breadth Europe got in the second round.

## Companies needing manual re-verification (marked `unknown`, `enabled: false`)

Updated 2026-07-26: a full live-verification pass (parallelized across 7 research agents,
findings cross-checked against `scrapers.generic._looks_like_job_link` directly rather than
trusting each agent's own characterization) resolved 23 of the ~89 previously-unknown companies
into working `workday`/`greenhouse`/`generic` entries -- see the "Unsupported ATS platforms found
in the wild" section above for exactly which vendor each remaining company runs and why it isn't
scrapable today (client-rendered SPA, bot-wall, unsupported vendor, href pattern mismatch, no
careers page at all, or genuinely federated/merged/no-current-openings). What's left, by region:

Canada: Nuvei (Workable), Bausch Health (SuccessFactors), CGI (no fingerprint)

Australia: Atlassian, Xero (merged, see above), Seek (is itself the excluded job board),
Carsales (SmartRecruiters), WiseTech Global (zero current openings), Judo Bank (Cloudflare),
Koala (Teamtailor, client-rendered), Sonic Healthcare (no working URL found),
Deloitte Australia (SuccessFactors), PwC Australia (Phenom People), EY Australia
(SuccessFactors), KPMG Australia (SmartRecruiters), McKinsey Australia (unreachable),
BCG Australia (Phenom People), Bain & Company Australia (EPiServer), Woolworths Group
(Avature, href mismatch)

New Zealand: Trade Me (Cornerstone OnDemand), Sharesies (Next.js SPA), Hnry (no ATS, mailto
only), Datacom (Cloudflare), Gentrack (BambooHR), Timely (Workable), Partly (Ashby),
Plexure/TASK (Breezy HR, href mismatch), Vend/Lightspeed NZ, Zespri (SuccessFactors),
AgResearch (SuccessFactors), One NZ (SuccessFactors), ASB Bank (Snaphire, href mismatch),
Kiwibank (unreachable), Tower Insurance (Snaphire, href mismatch), IAG New Zealand (no own
portal), EY New Zealand (SuccessFactors), Amazon (NZ offices) (proprietary), Serato (Breezy HR,
href mismatch), Deloitte New Zealand (SmartRecruiters)

USA: Scale AI (Next.js SPA, Ashby unconfirmed), Ramp (Ashby), Citadel (Cloudflare),
McKinsey & Company, Boston Consulting Group, Bain & Company

Europe (biotech/pharma + fintech/tech tiers): Bayer (Cloudflare), Novo Nordisk (SuccessFactors),
Lundbeck (SuccessFactors), Hologic (no fingerprint), H&M (Akamai), Klarna (Deel),
Unity Technologies (Next.js SPA), Booking.com (iCIMS), Just Eat Takeaway (Phenom People),
TomTom (Next.js SPA), SAP (SuccessFactors), Revolut (Cloudflare),
Stripe (merged with US entry, see above), Lovable (Ashby), University of Gothenburg (ReachMee)

Europe (second round): Deloitte (federated), KPMG (federated), Bankinter (Cloudflare),
Credit Suisse (merged into UBS, see above), KBC Bank (Adobe AEM SPA), Nordea (no fingerprint),
ASOS (ThirtyThree), Decibel Therapeutics (merged into Regeneron, see above)

Academic / job boards (2026-07-26 batch, see above): Aalborg University (client-rendered,
no API found), Jobnet.dk (real API exists but WAF-blocked), ResearchGate (hard 403 bot-wall)

## 2026-07-28: triage of the 44 companies that failed in the first real CI run

Run `30279701099` (2026-07-27) surfaced 44 failing `enabled: true` companies -- the first time
this project had real production failure data instead of pre-launch research. 12 were the
Workday `wdN` cluster (see the Phase 1 PR, `scrapers/workday.py`). This section covers the
other 32, checked live against the actual production request shape, not guessed.

### Fixed in place (existing adapters, no new code)

- **Ada**: `lever/ada` 404s. Real board is Greenhouse, `ada18` (`job-boards.greenhouse.io/ada18`,
  8 jobs). Lever token was stale, likely a pre-migration leftover.
- **Clio**: `greenhouse/goclio` 404s. Clio moved to Workday: `clio/ClioCareerSite|wd3`, 158 jobs
  (Vancouver posting confirms it's the right Clio -- there's an unrelated Greek startup also
  named "Clio" that a same-name Workable guess turned up, rejected for that reason).
- **Tyro Payments**: `lever/tyro` 404s. Real board is Workday, `tyro/Tyro|wd3`. Currently 0 open
  roles -- confirmed genuine (valid schema, empty `jobPostings`), not a wrong identifier.
- **Getir**: URL `careers-page.com/getir-2` now 404s; the company moved to a per-company
  subdomain, `getir.careers-page.com/`. Same `careers-page.com` platform, still `generic`,
  10 job links visible in raw HTML.

### Confirmed live on a vendor this project has no adapter for yet

All of the following were verified against the vendor's real API with the exact request shape
`SPEC_scraper_json_boards.md` (not yet written) would need -- not a guess, not a name match on
its own unless noted. This is the Tier 1 vendor list from `ROADMAP.md` turning out to matter a
lot more than the original ~10-company estimate: 17 companies land here, all currently `lever`
or `greenhouse` in the registry with a stale token.

**Ashby** (`api.ashbyhq.com/posting-api/job-board/{slug}`) -- 10 companies:
Cohere `cohere` (139), Airwallex `airwallex` (609), Xero `xero` (101), 1Password `1password`
(63), KOHO `koho` (13), Back Market `backmarket` (13), Top Hat `top-hat` (8, note the hyphen),
Benevity `benevity` (job content confirms Calgary HQ), Lightspeed Commerce `lightspeedhq`
(job content confirms Ottawa -- the bare slug `lightspeed` is a *different* company, an
Illinois robotics firm, rejected), and Halter `halter` (276, already known from the previous
session, repeated here because it's the same fix).

**SmartRecruiters** (`api.smartrecruiters.com/v1/companies/{id}/postings`) -- 2 companies:
Canva `canva` (230, confirmed with real content -- SmartRecruiters returns HTTP 200 with an
empty `content: []` for *any* slug, valid or not, so a bare 200 proves nothing by itself; Canva
was confirmed via non-empty postings), Getaround `Getaround` (0 jobs, confirmed genuine via the
separate public page `careers.smartrecruiters.com/Getaround`, which says "No job" -- same
false-positive-shaped API, verified through the side door instead).

**Workable** (`apply.workable.com/api/v1/widget/accounts/{slug}?details=true`) -- 5 companies,
all confirmed via the `name` field in the response matching the real company (Workable's widget
API also returns 200 for a nonexistent slug, with `jobs: []` -- the name match is what makes
these real, not the status code): Kinaxis `kinaxis`, Symend `symend`, FreshBooks `freshbooks`,
Glovo `glovo`, Linktree `linktree`. All currently show 0 open jobs.

None of these are coded yet -- `scrapers/json_boards.py` (or five separate modules, see the open
architecture decision in `ROADMAP.md`) still needs to be built before any of the 17 actually
recover. Confirming this many real companies on three vendors in one pass is a strong argument
for building Ashby first, since it alone accounts for 10 of the 17.

### Bot-walled (matches the existing do-not-pursue pattern)

Orsted, Tesla, Schneider Electric, EDF, and Tesco return 403 consistently. Uber returns 406,
same effective signature. Carrefour is inconsistent -- 403 from the GitHub Actions runner in the
real CI run, 200 from this machine's IP during research -- which reads as Cloudflare scoring
datacenter/cloud IP ranges (where Actions runs) more aggressively than others, not as the block
being lifted. Treating it as still bot-walled since production is what matters. Same policy as
the existing list in `HANDOFF.md`: getting through means defeating bot detection, which this
project deliberately does not do.

### Unresolved (need more work, left enabled so they stay visible in `scraper_health.csv`)

- **Vidyard**: not on Greenhouse (stale token, confirmed dead via 302 error-redirect), Lever,
  Ashby, SmartRecruiters, Workable, Breezy, or BambooHR. Their own `/careers/` page 403s.
  Needs a real browser session to find the current platform.
- **King** (Workday tenant `activision`): careers.king.com shows Eightfold markers in raw HTML,
  but the `domain` param `scrapers/eightfold.py` needs could not be guessed (`king.com` and
  `careers.king.com` both return `"Tenant not identified"`). Needs a live devtools capture of
  the real XHR call; attempted via the in-app browser tool this session, which became
  unresponsive before it completed.
- **Telenor** (Workday tenant `telenorgroup`): live search results point at
  `telenorgroup.wd3.myworkdayjobs.com/TelenorGroup_careers`, but that instance now returns
  HTTP 422 on the real CXS POST (not 404 -- the tenant resolves, the request is rejected for an
  unknown reason). Instances above wd150 don't even resolve in DNS for this tenant, ruling out
  "just needs a higher wdN". Current platform not identified.
- **McKinsey & Company**: connection fails outright (no response, not even a TLS handshake) from
  this machine, matching the same signature `HANDOFF.md` already recorded for the separate
  "McKinsey Australia" entry. Likely geo/network-level, not a scraper bug. Worth one retry from
  a different vantage point (e.g. the GitHub Actions runner itself) before concluding anything.

## 2026-07-29: SuccessFactors cluster (ROADMAP.md Phase 3, Tier 3)

The premise from `HANDOFF.md`/`ROADMAP.md`: SuccessFactors isn't uniformly unscrapable, since
Canal+, Coloplast, Zurich Insurance, and Scotiabank already work via `generic` because their
tenants expose a server-rendered `/search/` (or `/go/...`) page distinct from the client-rendered
SPA landing page. Checked all 10 candidates from the cluster (9 from `ROADMAP.md` plus
`One NZ (Vodafone NZ)`, already a disabled registry entry with a dead `/viewalljobs/` identifier)
for the same pattern. 6 of 10 hit.

**Fixed** (all confirmed with real job content via `scrapers.generic._looks_like_job_link`, not
just a 200 or a plausible-looking href count -- several companies' *existing* URLs returned
20-30 href matches that turned out to be nav/marketing links, e.g. "Careers in Assurance",
not real postings):
- Novo Nordisk: `careers.novonordisk.com/search/` (200 jobs)
- SAP: `jobs.sap.com/search/` -- note this is a distinct branded domain from the
  `career5.successfactors.eu/careers?company=SAP` URL already in the registry, which is the
  shared multi-tenant SuccessFactors domain and stays an SPA shell (26 jobs)
- Deloitte Australia: `jobs.deloitte.com.au/search/` (32 jobs)
- Zespri: `careers.zespri.com/search/` (8 jobs)
- AgResearch: `yourcareer.agresearch.co.nz/search/`, a newer branded domain than the
  `career10.successfactors.com` one in the old registry entry (1 job -- genuinely small company)
- One NZ (Vodafone NZ): `careers.one.nz/search/` (25 jobs). The registry already had this
  company disabled with `careers.one.nz/viewalljobs/`, which 200s but returns 0 real hits (same
  nav-link-only shape as the failures below) -- `/search/` was the fix, not a new source.

**Not fixed** (checked, no working server-rendered equivalent found):
- **Lundbeck**: still on the shared `career5.successfactors.eu` domain, same as SAP before its
  fix. Their own branded domain (`lundbeck.com/us/careers/...`) exists and 200s but only returns
  nav/marketing links ("Life at Lundbeck", "our culture and people"), not postings. No
  `careers.lundbeck.com`-style dedicated domain found (doesn't resolve).
- **EY Australia / EY New Zealand**: confirmed SuccessFactors-backed (via `careers.ey.com`), but
  every URL tried -- the country-specific `ey.com/en_au` and `en_nz` pages, the global
  `careers.ey.com/viewalljobs/`, and a guessed `careers.ey.com/ey/jobs/?country=Australia`
  filter (which 404s) -- returns only nav links or an error page. This needs real devtools
  capture of the actual search XHR, not a URL-pattern guess; matches HANDOFF's Tier 4 category
  more than Tier 3's "cheap check."
- **Bausch Health**: the registry's existing `/search` identifier and a `/go/Job-Openings-in-...`
  category page (matching the pattern that worked for Canal+) both 200 with 0 real hits. No
  working page found without deeper investigation.
