# 📊 math2data-pipeline (TikTok Series Codebase)

> **Series Title:** *Doctorate to Data: Proof of Work*  
> **Host / Creator:** Math PhD $\rightarrow$ Data Scientist Transition  
> **Goal:** Automated Job Scraping, Resume Vector Matching & Market Analytics Engine built live on TikTok!

---

## 📁 Subfolder Structure

```text
math2data_tiktok_series/
├── EPISODE_1_SCRIPT.md          # Full 65s script & shot list for Episode 1 (Pilot)
├── README.md                    # Project overview & series documentation
├── requirements.txt             # Python dependencies
├── data/
│   ├── cv_master.txt            # Plain-text academic CV for TF-IDF matching
│   └── raw_jobs.db              # SQLite database (created on first run)
└── src/
    ├── scraper/
    │   └── linkedin_scraper.py  # Playwright job scraper core (Ep 1 & 3)
    ├── analytics/
    │   └── matcher.py           # TF-IDF Cosine Similarity engine (Ep 6 & 7)
    └── app/
        └── dashboard.py         # Streamlit dark-mode tracking interface (Ep 13)
```

---

## ⚡ Quick Start for Filming

To record Episode 1 terminal output on camera:

```bash
# Navigate to the series subfolder
cd math2data_tiktok_series

# Run the pilot scraper demonstration script
python src/scraper/linkedin_scraper.py
```
