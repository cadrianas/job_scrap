# 🎬 TikTok Master Content Strategy & Plan: "Doctorate to Data"

**Series Title:** *Doctorate to Data: Proof of Work*  
**Channel Concept:** Academic perfectionism colliding with corporate buzzwords, job-hunting realities, and building an automated Python pipeline.  
**Subfolder Root:** `math2data_tiktok_series/`  
**Format:** Hybrid Edutainment (5s Skit/Hook + 40s Technical Story/Code B-Roll + 15s Takeaway/CTA)  
**Target Duration:** **61–90 seconds** (Optimized for TikTok Creator Rewards Monetization)  

---

## 📌 Master Content Architecture & Roadmap

```
┌────────────────────────────────┐       ┌────────────────────────────────┐
│ Arc 1: The Reality Check (Ep 1-5)│ ──► │ Arc 2: The Scraper & DB (Ep 6-10)│
│ "Degree gap & SQL struggles"   │       │ "Building Playwright & SQLite" │
└────────────────────────────────┘       └────────────────────────────────┘
                                                         │
                                                         ▼
┌────────────────────────────────┐       ┌────────────────────────────────┐
│ Arc 4: The Gauntlet (Ep 16-22) │ ◄─── │ Arc 3: The Matcher (Ep 11-15)  │
│ "Case studies & Real offers"   │       │ "TF-IDF NLP & Streamlit UI"    │
└────────────────────────────────┘       └────────────────────────────────┘
```

---

## 🚀 Arc 1: The Reality Check & Unpacking the Degree Gap (Ep 1–5)

* **Episode 1 (PILOT):** *What BSc, MSc & PhD Degrees Teach vs. What Data Science Companies ACTUALLY Want*  
  * **Hook:** "I spent 5 years solving partial differential equations for a Math PhD, and I just got rejected from an entry-level analyst job because I don't know SQL."  
  * **Core Concept:** Degree curriculum gap (BSc = toy notebooks, MSc = Kaggle CSVs, PhD = LaTeX proofs vs. Company = 1-line SQL query). Live SQLite syntax error.  

* **Episode 2:** *Translating 'Stochastic Systems' to Corporate Speak*  
  * **Hook:** "Translating my 40-page math thesis into terms corporate recruiters actually understand."  
  * **Core Concept:** Converting complex research terms into plain-text business impact in `data/cv_master.txt`.  

* **Episode 3:** *The '3-5 Years Experience Entry-Level' Paradox*  
  * **Hook:** "Looking for an entry-level Data Analyst job, but they all require 5 years of PowerBI experience."  
  * **Core Concept:** Introducing the Playwright job scraper running `headless=False` in `src/scraper/linkedin_scraper.py`.  

* **Episode 4:** *A Day in the Life: Unemployed with a PhD & 100 Rejections*  
  * **Hook:** "What a realistic day looks like when you hold a doctorate but can't get past an entry-level HR filter."  
  * **Core Concept:** Vulnerable vlog: espresso, solving proofs, receiving 3 rejection emails, logging application status in `data/raw_jobs.db`.  

* **Episode 5:** *Things Industry People Say That Confuse Mathematicians*  
  * **Hook:** "Corporate buzzwords translated into mathematical terms."  
  * **Core Concept:** Rapid-fire skit ("rough estimate", "low-hanging fruit") + introducing regex text parsing to clean job posting fluff.  

---

## ⚙️ Arc 2: Building the Scraper & Database Engine (Ep 6–10)

* **Episode 6:** *Automating Job Scraping Without Getting Rate-Limited*  
  * **Hook:** "How to scrape job listings in Python without getting your IP address banned."  
  * **Core Concept:** User-agent rotation, randomized delays `time.sleep(random.uniform(2.5, 4.5))`, and CSS selector traps.  

* **Episode 7:** *Learning SQL Joins on Camera (The Academic Realization)*  
  * **Hook:** "Learning SQL Joins after 5 years of theoretical math research."  
  * **Core Concept:** Connecting set theory logic to SQL `INNER JOIN` and `LEFT JOIN` on `data/raw_jobs.db`.  

* **Episode 8:** *Cleaning Dirty Job HTML Data in Python*  
  * **Hook:** "What real data engineering looks like: turning dirty HTML text into clean dataset columns."  
  * **Core Concept:** BeautifulSoup and regex extraction to create clean pandas dataframes from raw scraped text.  

* **Episode 9:** *The 'We Use AI' Meme vs. Real Nested `if/else` Logic*  
  * **Hook:** "When a company claims their product uses cutting-edge AI, but you open their codebase and find this."  
  * **Core Concept:** Marketing hype vs. real nested conditional logic (`if 'SQL' in job_text: score += 10`).  

* **Episode 10:** *Database Architecture: SQLite vs PostgreSQL for Small Projects*  
  * **Hook:** "Why you don't need a heavy cloud database for your first Python project."  
  * **Core Concept:** Zero-config SQLite setup for local automation and on-camera demos. Episode 10 series milestone!  

---

## 📊 Arc 3: The Matcher Engine & Streamlit Dashboard (Ep 11–15)

* **Episode 11:** *Coding the TF-IDF Resume Matcher in 15 Lines of Python*  
  * **Hook:** "How I wrote 15 lines of Python to score my resume against any job description using TF-IDF."  
  * **Core Concept:** Implementing `TfidfVectorizer` and `cosine_similarity` in `src/analytics/matcher.py`.  

* **Episode 12:** *I Scraped 1,000 Data Science Jobs: What Companies ACTUALLY Ask For*  
  * **Hook:** "I scraped 1,000 Data Science job postings. Here are the top 5 skills requested in 2026."  
  * **Core Concept:** Data reveal: SQL (84%), Python (79%), AWS (52%), Tableau (41%). Prioritizing high-ROI skills.  

* **Episode 13:** *Building My Dark-Mode Streamlit Dashboard on Camera*  
  * **Hook:** "Turn your Python scripts into a sleek dark-mode web app in under 20 lines of code."  
  * **Core Concept:** Walkthrough of `src/app/dashboard.py` showing dynamic metric cards, dataframe tables, and interactive sliders.  

* **Episode 14:** *Data Analyst vs. Data Scientist vs. ML Engineer: What Degree Grads Need to Know*  
  * **Hook:** "Data Analyst vs Data Scientist vs ML Engineer: Which one should a STEM grad actually apply for?"  
  * **Core Concept:** Scatter plot analysis of role requirements and tailoring resumes effectively.  

* **Episode 15:** *Why Mass-Applying Fails (And How Pipeline Scoring Fixed It)*  
  * **Hook:** "Why sending 500 random LinkedIn Easy Apply applications is a waste of time."  
  * **Core Concept:** Comparing 1% cold apply response rate vs 15% response rate on >75% match score applications.  

---

## 🎯 Arc 4: The Interview Gauntlet & Real-World Results (Ep 16–22)

* **Episode 16:** *The Corporate Case Study: Markov Chains vs. Logistic Regression*  
  * **Hook:** "When a Math PhD takes a corporate technical interview."  
  * **Core Concept:** Over-engineering vs. simple baselines (Markov jump process vs. `scikit-learn` Logistic Regression).  

* **Episode 17:** *Translating Academic Drama into Corporate Behavioral Answers*  
  * **Hook:** "How to answer corporate behavioral questions when your background is academic research."  
  * **Core Concept:** Translating advisor ghosting and paper deadlines into STAR method behavioral answers.  

* **Episode 18:** *Debugging Hell: When the Scraper Broke at 2 AM*  
  * **Hook:** "The side of coding content creators don't show: spending 3 hours debugging a broken Playwright selector at 2 AM."  
  * **Core Concept:** Dealing with dynamic HTML class changes and fixing broken selectors under pressure.  

* **Episode 19:** *Live Running My Pipeline for 30 Days: The Interview Metrics*  
  * **Hook:** "I ran my automated job scraper and resume matcher for 30 days. Here are the exact numbers."  
  * **Core Concept:** Full pipeline review: 420 jobs scraped $\rightarrow$ 65 high match $\rightarrow$ 6 recruiter calls $\rightarrow$ 3 technical screens.  

* **Episode 20:** *First Technical Screening: What Corporate Tech Leads Asked Me*  
  * **Hook:** "I had my first senior technical screen for a Data Scientist role. Here is what they actually asked me."  
  * **Core Concept:** SQL joins, A/B testing, Python dicts, and showing your GitHub repo to bypass generic LeetCode questions.  

* **Episode 21:** *Comparing My Academic Stipend vs. First Industry Job Offer*  
  * **Hook:** "Comparing my PhD stipend to my first industry Data Science offer letter."  
  * **Core Concept:** Emotional & financial reflection on the academic-to-industry transition.  

* **Episode 22 (SERIES FINALE):** *From PhD Defense to Data Scientist: Open Source Release & Lessons Learned*  
  * **Hook:** "We made it. From an unemployed Math PhD to a full-time Data Scientist—and the complete open-source release of math2data-pipeline."  
  * **Core Concept:** Series finale montage, full GitHub repo tour, community thank you, and Series 2 announcement!  

---

## 📽️ Filming & Production Checklist

- [ ] **Video Length for Monetization:** 61–90 seconds (Required for TikTok Creator Rewards RPM).
- [ ] **Subfolder Alignment:** All scripts, code files, and SQLite databases reside in `math2data_tiktok_series/`.
- [ ] **VS Code Setup:** High contrast dark mode (Tokyo Night / One Dark Pro), 18-20px font size.
- [ ] **Audio & Pacing:** Crisp lapel mic audio; cut dead pauses while letting code explanations breathe past 60s.
