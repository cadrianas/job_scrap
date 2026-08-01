# SPEC: filters.py (Phase 4)

## Purpose
Keyword and region filtering so digests surface relevant roles first. Strategy is broad-then-filter: the scraper stores everything, filters only affect what the digest highlights.

## Behavior
Two modes, controlled by a constant in this module:
- `mode = "strict"` (default): only matching jobs enter the digest. Everything still goes to `jobs_seen.csv` regardless of mode, so nothing is lost.
- `mode = "annotate"`: all new jobs appear in the digest, but matching jobs are sorted to the top and marked.

## Matching
Case-insensitive substring match on title. The include list spans core Data Science, Data Analytics, Mathematical/Statistical Modelling (including specialized Infectious Disease Modelling, Biostatistics, RWE/RWD, and Computational Epidemiology), AI/ML, and Quantitative Finance across all seniority levels:

1. **Data science & AI/ML**: `data scientist, data science, machine learning, ml engineer, mlops, ai scientist, applied scientist, research scientist, decision scientist, decision science, nlp, computer vision, research engineer, prompt engineer`
2. **Data analytics**: `data analyst, data analytics, analytics, analytics engineer, business intelligence, bi analyst, product analytics, product analyst, insights analyst`
3. **Mathematical / quantitative / statistical modelling**: `mathematical model, mathematical modeller, mathematical modeling, mathematical modelling, quantitative, quant, quantitative modeller, quantitative analyst, quantitative researcher, quantitative research, modeller, modeler, bayesian, statistician, statistical modeller, stochastic, causal inference, operations research, actuary, actuarial, risk modeller, risk model, risk analyst, risk manager, financial engineer, simulation engineer, systems modeller, statistical programmer`
4. **Mathematical epidemiology & public health modelling**: `epidemiolog, biostatistician, infectious disease, disease modelling, disease modeling, outbreak model, outbreak analytics, transmission model, compartmental model, public health modelling, public health modeling, computational epidemiology, bioinformatic, computational biology, health economist, health economics, population health, real world evidence, real world data, rwe, rwd, pharmacometrics, qsp model, clinical data scientist, health data scientist`
5. **Data engineering & architecture**: `data engineer, data architect, data architecture, etl engineer, data platform`
6. **Academic instruction & teaching**: `instructor, lecturer, teaching fellow, assistant professor, associate professor, professor`

EXCLUDE (overrides include):
`intern, working student, principal recruiter, sales`

Note: `director`, `head of`, `vp`, `lead`, `principal`, and `senior` are explicitly NOT excluded, ensuring career progression up to leadership levels is surfaced.

## Location Exclusions
Jobs located in India are explicitly excluded from the digest (even if the company is headquartered in target regions like Europe, USA, etc.).
A job is treated as located in India if `is_india_job(job)` evaluates to `True`:
- Country / Country Codes: standalone word `\bindia\b`, or title/location prefixes such as `IN-`, `IN_`, `IN -`.
- Indian Tech Cities / Hubs: `bangalore`, `bengaluru`, `hyderabad`, `mumbai`, `pune`, `gurgaon`, `gurugram`, `noida`, `kolkata`, `chennai`, `ahmedabad`, `delhi`.
- Indian States & Tech Parks: `karnataka`, `telangana`, `maharashtra`, `tamil nadu`, `haryana`, `west bengal`, `gujarat`, `manyata`, `velankani`, `salarpuria`, `dlf downtown`.

## Seniority Tiering
`get_seniority_tier(title: str) -> str` classifies job titles into 3 tiers for digest grouping:
- **Executive & Leadership**: `director`, `head of`, `vp`, `vice president`, `chief`, `lead`
- **Senior & Staff**: `senior`, `staff`, `principal`, `lead` (if not director), `sr`
- **Mid & Entry / General**: All other matched titles

## Region boost
Jobs whose company has region tags intersecting `PRIORITY_REGIONS` sort above others within the same tier. All five target regions are weighted equally.

## API
- `apply(jobs: list[Job], companies: dict[str, Company]) -> list[Job]` : returns sorted (and possibly filtered) list. Excludes India-located jobs.
- `matches(title: str) -> bool` : exposed for testing title inclusion/exclusion.
- `is_india_job(job: Job) -> bool` : returns True if job location, title, or URL indicates location in India.
- `get_seniority_tier(title: str) -> str` : returns tier label for digest grouping.


