# SPEC: scrapers/workday.py

## Purpose
Adapter for Workday-hosted careers sites (most pharma, banks, industrials: Novo Nordisk, Roche, Maersk, Volvo, etc.). Hardest of the API adapters because the endpoint is undocumented and per-tenant, but it IS a JSON API, so no browser automation is needed.

## How Workday careers sites work
A careers URL looks like:
`https://{tenant}.wd{N}.myworkdayjobs.com/{site}`
e.g. `https://novonordisk.wd3.myworkdayjobs.com/nncareers`

The page is a JS app that calls an internal JSON endpoint:
`POST https://{tenant}.wd{N}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs`

with JSON body:
```json
{"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}
```

## Identifier convention
companies.json stores `identifier` as `"{tenant}/{site}"`. By default the `wd{N}` instance number
is NOT stored; the adapter discovers it by trying wd1, wd3, wd5, wd2, wd4 (in that order of
prevalence) and caching the working one in memory for the run. A 404 or non-200 on the POST means
wrong instance; try next.

**Explicit instance override.** For a tenant where the fast 5-candidate guess doesn't hit,
`identifier` may instead be written as `"{tenant}/{site}|wd{N}"` (pipe-separated, matching the
`eightfold.py` convention for its explicit-domain override -- see `SPEC_scraper_eightfold.md`).
This skips probing entirely for that tenant, both the successful instance in the fast list and
any wider guessing. Only add this after confirming the instance actually responds with a live
request (curl or browser devtools), never speculatively: some tenants sit well outside the fast
5-candidate range (Vertex Pharmaceuticals is `wd501`), so a wider blind guess-and-check loop
baked into the adapter would multiply requests on every run for no benefit once the real value is
known. Do the discovery once, write the confirmed value into companies.json, and the adapter
never has to guess for that tenant again.

If a tenant migrates its careers site to a different tenant/site entirely, rather than just
changing its `wd{N}` number, update `identifier`'s `{tenant}/{site}` portion too (with a fresh
explicit instance). Example: Net-A-Porter's original tenant `ynap/YNAP_Careers` was retired after
a 2025 acquisition; the group's postings, including Net-A-Porter's, now live under
`luxexperience/LuxExperience_Careers|wd103`.

If the explicit instance ever stops working (Workday re-platforms the tenant again), the adapter
raises `ScraperError` naming the stale instance rather than silently falling back to guessing --
see "Errors" below. That failure is the signal to re-run discovery and update the identifier.

## Request details
- Method: POST, `Content-Type: application/json`, `Accept: application/json`, standard USER_AGENT.
- Pagination: `limit` max is 20. Loop offset += 20 until `total` (from first response) is reached or a safety cap of 500 jobs.
- Optional optimization (Phase 4): pass `searchText: "data"` to cut volume for giant tenants; v1 fetches everything to keep broad-then-filter intact.

## Response shape (relevant fields)
```json
{
  "total": 1342,
  "jobPostings": [
    {
      "title": "Senior Data Scientist",
      "externalPath": "/job/Copenhagen/Senior-Data-Scientist_JR123456",
      "locationsText": "Copenhagen, Denmark",
      "postedOn": "Posted 3 Days Ago",
      "bulletFields": ["JR123456"]
    }
  ]
}
```

## Mapping to Job
- `job_id` = bulletFields[0] if present else sha1(externalPath)
- `title` = title
- `location` = locationsText or ""
- `url` = `https://{tenant}.wd{N}.myworkdayjobs.com/{site}{externalPath}`
- `posted_date` = "" (postedOn is a fuzzy string like "Posted 3 Days Ago"; parse "Posted Today"/"Posted Yesterday"/"Posted N Days Ago" into an ISO date, else "")

## Errors -> ScraperError
- No wd instance works (all candidates 404): message must say "check tenant/site identifier"
- JSON decode failure or missing jobPostings
- More than 3 consecutive failed pagination pages

## Rules
- Sleep 0.5s between pagination pages (in addition to the between-company sleep).
- This adapter is the most likely to break when Workday updates. Keep ALL endpoint logic in this one file.

## Test companies for development
Verify the cxs endpooint manually in browser devtools (Network tab, filter "jobs") for 2 companies before coding, and record the exact tenant/site pairs in companies.json.
