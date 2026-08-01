# 🛠️ Scraper Architecture Spec: 2,000 Job Market Dataset (Entry/Mid vs. Senior+)

> **Project Goal:** Automatically scrape and analyze **2,000 job postings** (1,000 Entry/Mid-Level vs. 1,000 Senior+) to extract empirical skill frequencies, tech stack demands, and experience requirements.

---

## 📌 1. Seniority Categorization Logic

Jobs will be classified into two distinct datasets during parsing based on job title keywords and experience requirements:

```
                          ┌───────────────────────────┐
                          │    Raw Job Postings       │
                          └─────────────┬─────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
    ┌───────────────────────────────┐       ┌───────────────────────────────┐
    │     Entry / Mid-Level Tier    │       │        Senior+ Tier           │
    │  (1,000 Target Postings)      │       │  (1,000 Target Postings)      │
    ├───────────────────────────────┤       ├───────────────────────────────┤
    │ • Keywords: Junior, Associate,│       │ • Keywords: Senior, Lead,     │
    │   Analyst, Data Scientist     │       │   Principal, Head of Data     │
    │ • Exp Required: 0 - 3 Years   │       │ • Exp Required: 4+ Years      │
    └───────────────────────────────┘       └───────────────────────────────┘
```

---

## 💾 2. Database Schema (`data/raw_jobs.db`)

We expand `data/raw_jobs.db` to store extracted skill vectors, experience requirements, and seniority tiers:

```sql
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    seniority_tier TEXT NOT NULL, -- 'Entry/Mid' OR 'Senior+'
    experience_years INTEGER,
    skills_json TEXT,            -- JSON array e.g. ["Python", "SQL", "Docker"]
    description TEXT,
    match_score REAL DEFAULT 0.0,
    status TEXT DEFAULT 'Scraped',
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔍 3. Skill & Tech Stack Taxonomy

The regex parser will extract matches across 5 core technical categories:

| Category | Target Keywords / Technologies |
| :--- | :--- |
| **Databases & Querying** | `SQL`, `PostgreSQL`, `MySQL`, `SQLite`, `Snowflake`, `BigQuery`, `MongoDB` |
| **Languages** | `Python`, `R`, `C++`, `Julia`, `Java`, `Scala`, `LaTeX` |
| **ML & Data Science** | `Scikit-learn`, `PyTorch`, `TensorFlow`, `Pandas`, `Numpy`, `SciPy`, `NLP`, `Time Series` |
| **Data Engineering & Cloud**| `Docker`, `Kubernetes`, `AWS`, `GCP`, `Azure`, `Spark`, `Airflow`, `Git`, `CI/CD` |
| **BI & Visualization** | `Tableau`, `PowerBI`, `Looker`, `Streamlit`, `Dash`, `Matplotlib`, `Seaborn` |

---

## 📽️ TikTok & Substack Content Integration

* **TikTok Episode 12:** *I Scraped 1,000 Entry vs 1,000 Senior Jobs: What Companies ACTUALLY Ask For*  
  * *Visual:* Side-by-side bar chart showing SQL required in 85% of Entry roles vs. Docker/System Architecture required in 75% of Senior roles.
* **Substack Deep-Dive Article:** *The 2,000 Data Job Analysis: What 5 Years of Math Research Didn't Teach Me About Senior Tech Roles.* (Includes full code & dataset download link).
