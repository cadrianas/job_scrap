# 📺 Series 1: "Doctorate to Data" (22-Episode Full Arc Roadmap)

> **Creator Mindset & Strategy (Inspired by Alex Petrakieva's *One Good Series*):**  
> 1. **Do NOT quit after Episode 3 or 6:** Most creators quit right before episode 7–10 where the algorithm catches up and momentum builds.  
> 2. **People don't follow isolated posts—they follow a story:** Viewers return to see *"Will this Math PhD actually land a Data Science job using her custom Python pipeline?"*  
> 3. **Keep it real over perfect:** Show authentic struggles—learning SQL syntax on camera, terminal tracebacks, random coding B-roll, rejection emails, and degree curriculum gaps.  
> 4. **Duration:** Aim for **61–90 seconds** per episode for TikTok Creator Rewards monetization while giving code explanations room to breathe.

---

## 🎬 Narrative Arc Overview

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

## 🚀 Arc 1: The Reality Check & Unpacking the Math PhD (Ep 1–5)

### Episode 1 (PILOT): "What BSc, MSc & PhD Degrees Teach vs. What Data Science Companies ACTUALLY Want"
* **Story Goal:** Introduce your journey from Math PhD to Data Science, exposing the hilarious gap between university degree curricula and corporate SQL expectations.
* **5s Hook:** "I spent 5 years solving partial differential equations for a Math PhD, and I just got rejected from an entry-level analyst job because I don't know SQL."
* **Script / Content:**
  1. *0:00-0:08:* Math paper vs entry-level job posting requiring SQL.
  2. *0:08-0:25:* The Curriculum Breakdown:
     - **BSc in DS:** Teaches linear algebra & toy Jupyter notebooks.
     - **MSc in DS:** Teaches deep learning & clean Kaggle CSVs.
     - **PhD in STEM:** Teaches 40-page LaTeX theoretical proofs.
     - **Company reality:** `SELECT * FROM sales_data WHERE status = 'Active';`
  3. *0:25-1:10:* Terminal B-roll running Python scripts, live SQLite syntax error moment (`OperationalError`), and introducing the 22-episode series goal: building an automated Python scraper & SQL database pipeline on camera!
* **CTA:** "Follow along for Episode 2 where we start building the scraper!"

---

### Episode 2: "Translating 'Stochastic Systems' to Corporate Speak"
* **Story Goal:** Expose the ridiculous contrast between hyper-niche academic terms and corporate buzzwords.
* **5s Hook:** "Translating my 40-page math thesis into terms corporate HR recruiters actually understand."
* **Script / Content:**
  1. *0:00-0:10:* Skit: What you write ("Developed stochastic jump models for dynamic systems") vs. What HR hears ("Can you build a bar chart in Tableau?").
  2. *0:10-0:45:* Updating `data/cv_master.txt` on screen, removing LaTeX fluff, and writing plain-text bullet points focused on business impact.
  3. *0:45-1:10:* Why translating technical impact into plain English is the #1 hurdle for STEM graduates.
* **CTA:** "Drop your degree thesis topic in the comments and I'll translate it!"

---

### Episode 3: "The '3-5 Years Experience Entry-Level' Paradox"
* **Story Goal:** Address the entry-level experience trap and introduce the automated job scraper solution.
* **5s Hook:** "Looking for an entry-level Data Analyst job, but they all require 5 years of PowerBI experience."
* **Script / Content:**
  1. *0:00-0:10:* Reading absurd job descriptions requiring 5 years experience for $50k entry-level roles.
  2. *0:10-0:45:* Launching `python src/scraper/linkedin_scraper.py` on camera. Watching Playwright open Chromium (`headless=False`) and scroll through postings automatically.
  3. *0:45-1:10:* Why automating job collection beats spending 4 hours manually clicking through job boards every day.
* **CTA:** "Star the repo on GitHub—link in bio!"

---

### Episode 4: "A Day in the Life: Unemployed with a PhD & 100 Rejections"
* **Story Goal:** Vulnerable micro-vlog showing the authentic human side of job hunting while maintaining technical discipline.
* **5s Hook:** "What a realistic day looks like when you hold a doctorate but can't get past an entry-level HR filter."
* **Script / Content:**
  1. *0:00-0:10:* Drinking espresso, solving a math proof on paper for fun at 8 AM, then opening 3 rejection emails at 8:15 AM.
  2. *0:10-0:45:* Turning frustration into code: writing a basic Python script to log application statuses (`Applied`, `Rejected`, `Interview`) into `data/raw_jobs.db`.
  3. *0:45-1:10:* Encouragement for career switchers: don't let automated rejection emails make you doubt your intelligence.
* **CTA:** "Save this video for when the job search burnout hits."

---

### Episode 5: "Things Industry People Say That Confuse Mathematicians"
* **Story Goal:** Rapid-fire comedic skit exploring corporate buzzword culture.
* **5s Hook:** "Corporate jargon translated into mathematical terms."
* **Script / Content:**
  1. *0:00-0:15:* "We need a rough estimate" $\rightarrow$ Off by $10^3$.
  2. *0:15-0:45:* "Let's circle back and leverage low-hanging fruit" $\rightarrow$ Whiteboard calculation proving the fruit isn't low-hanging.
  3. *0:45-1:10:* Introducing regex text parsing in Python to strip corporate fluff from job listings.
* **CTA:** "What's the worst corporate buzzword you've heard in an interview?"

---

## ⚙️ Arc 2: Building the Scraper & Database Engine (Ep 6–10)

### Episode 6: "Automating Job Scraping Without Getting Rate-Limited"
* **Story Goal:** Technical deep dive into Playwright web automation, user agents, and polite rate-limiting.
* **5s Hook:** "How to scrape job listings in Python without getting your IP address banned."
* **Script / Content:**
  1. *0:00-0:10:* Showing Playwright browser running smoothly on screen.
  2. *0:10-0:45:* Code walkthrough of `time.sleep(random.uniform(2.5, 4.5))` and CSS selector traps in `src/scraper/linkedin_scraper.py`.
  3. *0:45-1:10:* Watching clean terminal logs print extracted job titles and locations in real time.
* **CTA:** "Save this code snippet for your next scraping project!"

---

### Episode 7: "Learning SQL Joins on Camera (The Academic Realization)"
* **Story Goal:** Authentic learning progress showing how relational databases work in practice.
* **5s Hook:** "Learning SQL Joins after 5 years of theoretical math research."
* **Script / Content:**
  1. *0:00-0:10:* Venn diagram of sets vs. SQL `INNER JOIN` & `LEFT JOIN`.
  2. *0:10-0:45:* Writing SQLite queries in terminal connecting `jobs` table with `companies` table. Show a live typo error, fix it, and watch query output print cleanly.
  3. *0:45-1:10:* Why set theory in math makes SQL logical once you get past the initial syntax hurdles.
* **CTA:** "Are you team SQL or team Python pandas for data wrangling?"

---

### Episode 8: "Cleaning Dirty Job HTML Data in Python"
* **Story Goal:** Show real-world data engineering (parsing ugly HTML, removing tags, handling missing values).
* **5s Hook:** "What real data engineering looks like: turning dirty HTML text into clean dataset columns."
* **Script / Content:**
  1. *0:00-0:10:* Raw HTML job description full of `<div>`, `<br>`, and missing salary tags.
  2. *0:10-0:45:* Writing BeautifulSoup and regex patterns to extract clean text (`title`, `requirements`, `salary`).
  3. *0:45-1:10:* Show clean pandas dataframe output on screen.
* **CTA:** "Comment 'DATA' to get my HTML cleaning regex cheat sheet."

---

### Episode 9: "The 'We Use AI' Meme vs. Real Nested `if/else` Logic"
* **Story Goal:** Humorous commentary on how tech companies package basic logic as "Artificial Intelligence".
* **5s Hook:** "When a company claims their product uses cutting-edge AI, but you open their codebase and find this."
* **Script / Content:**
  1. *0:00-0:15:* Skit: Marketing pitch ("Our AI matches candidates with 99% precision") vs. Actual Python code (`if 'SQL' in job_text: score += 10`).
  2. *0:15-0:45:* Demystifying AI marketing vs. real statistical models.
  3. *0:45-1:10:* Why fundamental data structures and logic matter 10x more than AI hype.
* **CTA:** "Share this video with a fellow coder!"

---

### Episode 10: "Database Architecture: SQLite vs PostgreSQL for Small Projects"
* **Story Goal:** Explain database choices for data projects and career portfolios.
* **5s Hook:** "Why you don't need a heavy cloud database for your first Python project."
* **Script / Content:**
  1. *0:00-0:10:* SQLite (`raw_jobs.db` single file) vs Postgres Docker container setup.
  2. *0:10-0:45:* Demonstrating why zero-config SQLite is perfect for local automation and on-camera demos.
  3. *0:45-1:10:* Milestones recap: We hit Episode 10! Database setup complete.
* **CTA:** "We made it to Episode 10! Share this series with someone transitioning to tech."

---

## 📊 Arc 3: The Matcher Engine & Streamlit Dashboard (Ep 11–15)

### Episode 11: "Coding the TF-IDF Resume Matcher in 15 Lines of Python"
* **Story Goal:** Introduce NLP vector matching now that the database and scraper are fully built.
* **5s Hook:** "How I wrote 15 lines of Python to score my resume against any job description using TF-IDF."
* **Script / Content:**
  1. *0:00-0:10:* Showing score calculation printing in terminal (`src/analytics/matcher.py`).
  2. *0:10-0:45:* Code walkthrough of `TfidfVectorizer` and `cosine_similarity` ([src/analytics/matcher.py](file:///Users/adriana-stefaniaciupeanu/Downloads/job-scraper-plan/math2data_tiktok_series/src/analytics/matcher.py)).
  3. *0:45-1:10:* Explaining the linear algebra: measuring the angle $\theta$ between CV vector and Job Description vector.
* **CTA:** "Save this video to build your own ATS resume matcher!"

---

### Episode 12: "I Scraped 1,000 Data Science Jobs: What Companies ACTUALLY Ask For"
* **Story Goal:** Empirical market data reveal using your scraper database.
* **5s Hook:** "I scraped 1,000 Data Science job postings. Here are the top 5 skills requested in 2026."
* **Script / Content:**
  1. *0:00-0:10:* Data reveal: SQL (84%), Python (79%), AWS (52%), Tableau (41%), PyTorch (18%).
  2. *0:10-0:45:* Math research skills vs. market realities: Why learning SQL & Git opens 80% more doors than specialized theoretical frameworks.
  3. *0:45-1:10:* How to prioritize study time based on hard data rather than guesswork.
* **CTA:** "Comment 'DATA' to see the full list of top 20 requested skills."

---

### Episode 13: "Building My Dark-Mode Streamlit Dashboard on Camera"
* **Story Goal:** Build a front-end interface to display metrics, match scores, and application status.
* **5s Hook:** "Turn your Python scripts into a sleek dark-mode web app in under 20 lines of code."
* **Script / Content:**
  1. *0:00-0:10:* Live Streamlit app UI preview with metric cards (`Total Scraped`, `High Match`, `Applied`).
  2. *0:10-0:45:* Code walkthrough of `src/app/dashboard.py` showing `st.metric()` and `st.dataframe()`.
  3. *0:45-1:10:* Interacting with sliders and filtering jobs with >75% match score.
* **CTA:** "Drop a star on GitHub to support the project!"

---

### Episode 14: "Data Analyst vs. Data Scientist vs. ML Engineer: What Degree Grads Need to Know"
* **Story Goal:** Breakdown of role titles, expectations, and degree alignment.
* **5s Hook:** "Data Analyst vs Data Scientist vs ML Engineer: Which one should a STEM grad actually apply for?"
* **Script / Content:**
  1. *0:00-0:10:* Streamlit scatter plot of job titles vs required tech stacks.
  2. *0:10-0:45:* Breaking down expectations: Analysts (SQL/Dashboards), Scientists (Modeling/Experimentation), Engineers (Pipelines/Docker).
  3. *0:45-1:10:* How to tailor your resume for each role without writing 3 completely different CVs.
* **CTA:** "Which of the 3 roles are you aiming for?"

---

### Episode 15: "Why Mass-Applying Fails (And How Pipeline Scoring Fixed It)"
* **Story Goal:** Compare mass cold applying vs. high-match targeted applying using your tool.
* **5s Hook:** "Why sending 500 random LinkedIn Easy Apply applications is a waste of time."
* **Script / Content:**
  1. *0:00-0:10:* Response rate chart: 1% on random applications vs 15% on high-match score applications.
  2. *0:10-0:45:* Using Streamlit filters to only apply for postings where resume match score is >75%.
  3. *0:45-1:10:* Quality over quantity in career transitions.
* **CTA:** "How many jobs do you apply to per week?"

---

## 🎯 Arc 4: The Interview Gauntlet & Real-World Results (Ep 16–22)

### Episode 16: "The Corporate Case Study: Markov Chains vs. Logistic Regression"
* **Story Goal:** Classic interview skit showing over-engineering vs. pragmatic business solutions.
* **5s Hook:** "When a Math PhD takes a corporate technical interview."
* **Script / Content:**
  1. *0:00-0:15:* Skit: Interviewer asks "How would you predict customer churn?" Candidate proposes a continuous-time Markov jump process on a compact manifold. Interviewer says "We usually just run a logistic regression."
  2. *0:15-0:45:* Technical breakdown: Always build simple baselines first before adding model complexity.
  3. *0:45-1:10:* Key interview advice for academics: lead with business value, follow with rigor.
* **CTA:** "Save this rule for your next technical interview!"

---

### Episode 17: "Translating Academic Drama into Corporate Behavioral Answers"
* **Story Goal:** Navigating tough behavioral interview questions with academic stories.
* **5s Hook:** "How to answer corporate behavioral questions when your background is academic research."
* **Script / Content:**
  1. *0:00-0:10:* Question: "Tell me about a time you managed stakeholder expectations under tight deadlines."
  2. *0:10-0:45:* Internal translation: Advisor ghosting for 3 months before a paper deadline. Corporate answer: Proactive communication, weekly progress updates, and scope management using STAR method.
  3. *0:45-1:10:* Formula for STAR method answers.
* **CTA:** "What's the hardest interview question you've been asked?"

---

### Episode 18: "Debugging Hell: When the Scraper Broke at 2 AM"
* **Story Goal:** Show real coding struggle, traceback errors, and perseverance.
* **5s Hook:** "The side of coding content creators don't show: spending 3 hours debugging a broken Playwright selector at 2 AM."
* **Script / Content:**
  1. *0:00-0:10:* Terminal traceback error flashing red on screen.
  2. *0:10-0:45:* Tracking down dynamic HTML class name changes on job boards and fixing the selector in `linkedin_scraper.py`.
  3. *0:45-1:10:* The satisfying moment when `[200 OK]` responses start scrolling again.
* **CTA:** "Relatable? Drop a 💻 in the comments."

---

### Episode 19: "Live Running My Pipeline for 30 Days: The Interview Metrics"
* **Story Goal:** Data-driven review of job search results using your custom pipeline.
* **5s Hook:** "I ran my automated job scraper and resume matcher for 30 days. Here are the exact numbers."
* **Script / Content:**
  1. *0:00-0:10:* Streamlit dashboard summary metrics: 420 Jobs Scraped $\rightarrow$ 65 High Match (>75%) $\rightarrow$ 30 Applications $\rightarrow$ 6 Recruiter Calls $\rightarrow$ 3 Technical Screens.
  2. *0:10-0:45:* Proof that targeted resume alignment beats mass untargeted applying.
  3. *0:45-1:10:* How building this open-source tool became the main talking point in technical interviews!
* **CTA:** "Want to build this yourself? Full repository link in bio."

---

### Episode 20: "First Technical Screening: What Corporate Tech Leads Asked Me"
* **Story Goal:** Real interview breakdown and technical questions faced.
* **5s Hook:** "I had my first senior technical screen for a Data Scientist role. Here is what they actually asked me."
* **Script / Content:**
  1. *0:00-0:10:* Whiteboard breakdown of interview questions (SQL joins, A/B testing setup, Python dictionary manipulation).
  2. *0:10-0:45:* How showing my GitHub repo (`math2data-pipeline`) shifted the interview from generic LeetCode to discussing real architecture.
  3. *0:45-1:10:* Tip: Building a real project is 10x more memorable than a static resume.
* **CTA:** "Follow for Episode 21!"

---

### Episode 21: "Comparing My Academic Stipend vs. First Industry Job Offer"
* **Story Goal:** Payoff moment & financial reality of the transition.
* **5s Hook:** "Comparing my PhD stipend to my first industry Data Science offer letter."
* **Script / Content:**
  1. *0:00-0:10:* Side-by-side metric cards on screen.
  2. *0:10-0:45:* Reflecting on the emotional weight of feeling underpaid in research vs being valued in industry.
  3. *0:45-1:10:* Encouragement for STEM researchers doubting their market worth.
* **CTA:** "Save this as motivation for your career pivot!"

---

### Episode 22 (SERIES FINALE): "From PhD Defense to Data Scientist: Open Source Release & Lessons Learned"
* **Story Goal:** Celebrate completing the 22-episode arc, release the final codebase, and launch your creator brand.
* **5s Hook:** "We made it. From an unemployed Math PhD to a full-time Data Scientist—and the complete open-source release of math2data-pipeline."
* **Script / Content:**
  1. *0:00-0:15:* Compilation montage of coding snippets, terminal logs, dashboard UI, and key moments from Ep 1 to Ep 21.
  2. *0:15-0:45:* Tour of the finalized GitHub repository with clean documentation, Playwright scrapers, TF-IDF matchers, and Streamlit UI ([README.md](file:///Users/adriana-stefaniaciupeanu/Downloads/job-scraper-plan/math2data_tiktok_series/README.md)).
  3. *0:45-1:10:* Thanking the community and announcing Series 2!
* **CTA:** "Fork the repository on GitHub and start your transition today!"
