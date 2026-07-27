# SPEC: filters.py (Phase 4)

## Purpose
Keyword and region filtering so digests surface relevant roles first. Strategy is broad-then-filter: the scraper stores everything, filters only affect what the digest highlights.

## Behavior
Two modes, controlled by a constant in this module:
- `mode = "strict"` (default): only matching jobs enter the digest. Everything still goes to `jobs_seen.csv` regardless of mode, so nothing is lost, but the digest itself only surfaces the four target role families below. This is deliberate: the digest is meant to be a short, actionable list, not a browse-everything feed.
- `mode = "annotate"`: all new jobs appear in the digest, but matching jobs are sorted to the top and marked. Nothing is hidden. Useful for a temporary sanity check on whether the include list is too narrow (i.e. relevant roles are being excluded), but not the day-to-day mode.

## Matching
Case-insensitive substring match on title. The include list is scoped to four target role families, broadened to catch adjacent titles that use different but related vocabulary (finance/quant-trading job titles, actuarial/insurance titles, and public-health-adjacent research titles are common enough across the company registry to be worth including):

1. **Data science**: `data scientist, data science, machine learning, ML engineer, AI scientist, applied scientist, research scientist, decision scientist, decision science`
2. **Data analytics**: `data analyst, data analytics, analytics, analytics engineer, business intelligence, BI analyst, product analytics`
3. **Mathematical / quantitative modelling**: `mathematical model, mathematical modeller, mathematical modeling, mathematical modelling, quantitative, quant, quantitative modeller, quantitative analyst, quantitative researcher, quantitative research, modeller, modeler, bayesian, statistician, statistical modeller, operations research, actuary, actuarial, risk modeller, risk model`
4. **Mathematical epidemiology / public health modelling**: `epidemiolog, biostatistician, infectious disease model, disease modelling, disease modeling, outbreak model, outbreak analytics, transmission model, compartmental model, public health modelling, public health modeling, computational epidemiology, bioinformatic, computational biology, health economist, health economics, population health`

INCLUDE (any match across all four families qualifies, flat list for the actual constant):
`data scientist, data science, machine learning, ML engineer, AI scientist, applied scientist, research scientist, decision scientist, decision science, data analyst, data analytics, analytics, analytics engineer, business intelligence, BI analyst, product analytics, mathematical model, mathematical modeller, mathematical modeling, mathematical modelling, quantitative, quant, quantitative modeller, quantitative analyst, quantitative researcher, quantitative research, modeller, modeler, bayesian, statistician, statistical modeller, operations research, actuary, actuarial, risk modeller, risk model, epidemiolog, biostatistician, infectious disease model, disease modelling, disease modeling, outbreak model, outbreak analytics, transmission model, compartmental model, public health modelling, public health modeling, computational epidemiology, bioinformatic, computational biology, health economist, health economics, population health`

EXCLUDE (overrides include):
`intern, working student, director, VP, head of, principal recruiter, sales`

Note: exclude list deliberately does NOT contain "senior" or "staff". The bare `analytics` and `quant`/`quantitative` terms are broad by design now, but EXCLUDE catches the main false-positive risk (e.g. "Sales Analytics Manager" is dropped by the `sales` exclude term even though it matches `analytics`).

## Region boost
Jobs whose company has region tags intersecting `PRIORITY_REGIONS` sort above others within the same tier. All five target regions are weighted equally, no region is boosted over another:

```python
PRIORITY_REGIONS = [
    # Europe
    "helsinki", "nordics", "copenhagen", "stockholm", "oslo", "netherlands", "basel", "europe",
    # Canada
    "toronto", "vancouver", "montreal", "ottawa", "canada",
    # USA
    "new york", "san francisco", "seattle", "boston", "austin", "usa",
    # Australia
    "sydney", "melbourne", "canberra", "brisbane", "australia",
    # New Zealand
    "auckland", "wellington", "new zealand",
]
```

This list is a starting point tied to where postings are expected to concentrate; add or remove cities as the company registry grows without changing the boost logic itself.

## API
- `apply(jobs: list[Job], companies: dict[str, Company]) -> list[Job]` : returns sorted (and possibly filtered) list.
- `matches(title: str) -> bool` : exposed for testing.

## Rules
- Keyword lists live in this module as constants for now (move to JSON config only if they start changing weekly).
- Until Phase 4, `apply` is an identity function so main.py can call it from day one.
