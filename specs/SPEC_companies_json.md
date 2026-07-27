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
Valid `ats` values: `greenhouse`, `lever`, `workday`, `eightfold`, `generic`, plus academic sources `jobsacuk`, `jobbnorge`, `euraxess`, `mathjobs`, `academicpositions`, `varbi` (see SPEC_scraper_academic.md).

- `greenhouse`: the board token, i.e. the `X` in `boards.greenhouse.io/X` or `job-boards.greenhouse.io/X`
- `lever`: the site tag, i.e. the `X` in `jobs.lever.co/X`
- `workday`: `tenant/site` as found in the careers URL `X.wdY.myworkdayjobs.com/SITE` -> `"X/SITE"` (the wd instance number is discovered by the adapter, see SPEC_scraper_workday.md)
- `eightfold`: the careers domain, e.g. `careers.company.com`
- `generic`: the full careers page URL

## Rules
- `name` must be unique (dedup keys depend on it).
- Unknown `ats` values cause the company to be skipped with a logged warning, not a crash.
- Keep the file sorted alphabetically by `name` to reduce merge noise.

## Validation
`main.py --validate` loads the file, checks uniqueness of names, checks `ats` values against known adapters, and exits nonzero on problems. Run this in CI before scraping.
