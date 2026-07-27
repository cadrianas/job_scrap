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
