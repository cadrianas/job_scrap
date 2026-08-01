# PROJECT HANDOFF DOCUMENT
**Project Name:** `math2data-pipeline` (Job Automation & Market Analytics Engine)  
**Target Launch Date:** Mid-September 2026  
**Primary Goal:** Automated job extraction + Portfolio proof-of-work for TikTok content series (*PhD to Data Science*).

---

## 1. System Architecture & Tech Stack

```
 ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
 │  1. Scraper Layer    │ ───► │  2. Analytics Engine │ ───► │  3. UI & Dashboard   │
 │  (Playwright/BS4)    │      │  (Pandas / TF-IDF)   │      │ (Streamlit / SQLite) │
 └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
   • Fetch job postings           • Match keyword vectors        • Application Tracker
   • Bypasses basic blocks        • Score CV vs. JD              • Market skill trends
```

* **Core Language:** Python 3.11+
* **Web Scraping:** `playwright` (for dynamic rendering) / `beautifulsoup4` + `requests`
* **Data Processing & NLP:** `pandas`, `scikit-learn` (TF-IDF vectorizer / Cosine Similarity for CV matching)
* **Storage:** `sqlite3` (lightweight, zero-config, easy to query on camera)
* **Frontend Dashboard:** `streamlit`

---

## 2. Directory Structure Setup

To make your coding sessions look clean, modular, and professional on screen, structure your repository like this:

```text
math2data-pipeline/
├── data/
│   ├── raw_jobs.db             # Local SQLite database
│   └── cv_master.txt           # Plaintext copy of your CV for embedding score
├── src/
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── linkedin_scraper.py # Primary target scraper
│   │   └── utils.py            # User-agents, rate-limiting delays
│   ├── analytics/
│   │   ├── __init__.py
│   │   └── matcher.py          # Vector similarity / Keyword extractor
│   └── app/
│       └── dashboard.py        # Streamlit interface
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 3. "Code-On-Camera" Content Staging Plan

To make it clear and engaging for TikTok that you are actively building and running this, use these pre-staged code milestones for your screen recordings and visual hooks.

### Episode 1: The Scraper Core (`src/scraper/linkedin_scraper.py`)
* **Visual Hook:** Recording your terminal as dynamic HTML logs flash by, or showing a browser window automatically navigating job boards via Playwright.
* **On-Screen Code Highlight:** Showing how you parse job titles and handle rate-limiting.

```python
import time
import random
from playwright.sync_api import sync_playwright

def fetch_job_listings(query: str, location: str, max_pages: int = 3):
    """Scrapes job postings while mimicking human delay to respect rate limits."""
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Headless=False looks great on video!
        page = browser.new_page()
        
        for page_num in range(max_pages):
            url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}&start={page_num * 25}"
            page.goto(url)
            page.wait_for_selector(".job-card-container")
            
            # Extract cards...
            print(f"[*] Page {page_num + 1}: Found postings. Cool down active...")
            time.sleep(random.uniform(2.5, 4.5)) # Polite rate-limiting
            
        browser.close()
    return results
```

---

### Episode 2: The Resume Matching Engine (`src/analytics/matcher.py`)
* **Visual Hook:** Showing a percentage score popup on screen: *"Math PhD Resume Match Score: 84%."*
* **On-Screen Code Highlight:** Simple TF-IDF cosine similarity between your resume text and scraped job descriptions.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match_score(cv_text: str, job_description: str) -> float:
    """Calculates TF-IDF cosine similarity between academic CV and Industry JD."""
    documents = [cv_text, job_description]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Cosine similarity score between doc 0 (CV) and doc 1 (JD)
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)
```

---

### Episode 3: The Dashboard Interface (`src/app/dashboard.py`)
* **Visual Hook:** A high-contrast dark-mode Streamlit dashboard showing interactive bar charts of scraped tech stacks.
* **On-Screen Code Highlight:** A 10-line Streamlit script rendering an active pipeline.

```python
import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="PhD to DS Job Tracker", layout="wide")
st.title("📊 PhD to Data Science: Pipeline Tracker")

conn = sqlite3.connect("data/raw_jobs.db")
df = pd.read_sql_query("SELECT title, company, match_score, status FROM jobs ORDER BY match_score DESC", conn)

# Display Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Jobs Scraped", len(df))
col2.metric("High Match (>70%)", len(df[df['match_score'] > 70]))
col3.metric("Applications Sent", len(df[df['status'] == 'Applied']))

st.subheader("Top Scored Job Matches")
st.dataframe(df, use_container_width=True)
```

---

## 4. B-Roll & Screen Recording Checklist for Filming

When filming your coding snippets for TikTok, capture these specific 5-second B-roll clips:

1. **Terminal Execution:** Running `python src/scraper/linkedin_scraper.py` and watching text scroll in VS Code terminal (dark mode theme highly recommended).
2. **Automated Browser in Action:** Playwright opening Chromium (`headless=False`) and scrolling through pages automatically.
3. **Dataframe Output:** Hovering your mouse over `df.head()` output or SQL table entries showing extracted salaries, tags, and job titles.
4. **Interactive Dashboard:** Toggling buttons or filtering sliders on your Streamlit web app.
5. **The "Debugging Moment":** Quick cut of looking intensely at an exception traceback error, hitting save, and rerunning the script successfully.
