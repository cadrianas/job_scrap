# SPEC: config/companies.json

## Purpose
The company registry. Adding a company to the scraper means adding an entry here, nothing else.

## Format
A JSON array of objects matching the `Company` dataclass:

```json
[
  {
    "name": "Oura",
    "ats": "greenhouse",
    "identifier": "ouraring",
    "regions": ["helsinki", "nordics"],
    "tier": 1,
    "enabled": true
  },
  {
    "name": "Bolt",
    "ats": "generic",
    "identifier": "https://bolt.eu/en/careers/",
    "regions": ["tallinn", "europe"],
    "tier": 2,
    "enabled": true
  },
  {
    "name": "Novo Nordisk",
    "ats": "workday",
    "identifier": "novonordisk/careers",
    "regions": ["copenhagen", "nordics"],
    "tier": 1,
    "enabled": true
  }
]
```

## Identifier conventions per ATS
Valid `ats` values: `greenhouse`, `lever`, `workday`, `eightfold`, `generic`, plus academic sources `jobsacuk`, `jobbnorge`, `euraxess`, `mathjobs`, `academicpositions`, `varbi` (see SPEC_scraper_academic.md), plus vendor job boards `ashby`, `smartrecruiters`, `workable`, `breezyhr`, `bamboohr` (see SPEC_scraper_json_boards.md).

- `greenhouse`: the board token, i.e. the `X` in `boards.greenhouse.io/X` or `job-boards.greenhouse.io/X`
- `lever`: the site tag, i.e. the `X` in `jobs.lever.co/X`
- `workday`: `tenant/site` as found in the careers URL `X.wdY.myworkdayjobs.com/SITE` -> `"X/SITE"` (the wd instance number is normally discovered by the adapter; for a tenant confirmed to need a specific instance, `"X/SITE|wdY"` skips discovery, see SPEC_scraper_workday.md)
- `eightfold`: the careers domain, e.g. `careers.company.com`
- `generic`: the full careers page URL
- `ashby`: the board slug, i.e. the `X` in `jobs.ashbyhq.com/X`
- `smartrecruiters`: the company id, i.e. the `X` in `careers.smartrecruiters.com/X`. Verify with
  real job content before enabling, not just a 200 -- the API returns 200 for any id, valid or
  not, see SPEC_scraper_json_boards.md.
- `workable`: the account slug, i.e. the `X` in `apply.workable.com/X`. Same verify-by-content
  caveat as smartrecruiters.
- `breezyhr`: the subdomain, i.e. the `X` in `X.breezy.hr`
- `bamboohr`: the subdomain, i.e. the `X` in `X.bamboohr.com`

## Rules
- `name` must be unique (dedup keys depend on it).
- Unknown `ats` values cause the company to be skipped with a logged warning, not a crash.
- Keep the file sorted alphabetically by `name` to reduce merge noise.

## Validation
`main.py --validate` loads the file, checks uniqueness of names, checks `ats` values against known adapters, and exits nonzero on problems. Run this in CI before scraping.
