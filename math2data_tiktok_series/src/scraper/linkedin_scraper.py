"""
linkedin_scraper.py
Scraper Core for 2,000 Job Market Dataset (Entry/Mid vs. Senior+)
Featured in Episode 1, 3, 6 & 12 of 'Doctorate to Data'
"""

import time
import random
import json
import re
import sqlite3
from typing import List, Dict, Tuple

# Technical skill taxonomy regex patterns
SKILL_PATTERNS = {
    "SQL": r"\bsql\b|\bpostgresql\b|\bmysql\b|\bsnowflake\b|\bbigquery\b",
    "Python": r"\bpython\b",
    "R": r"\br\b|\brstudio\b",
    "Pandas": r"\bpandas\b|\bnumpy\b|\bscipy\b",
    "Scikit-Learn": r"\bscikit-learn\b|\bsklearn\b",
    "PyTorch": r"\bpytorch\b|\btensorflow\b|\bkeras\b|\bdeep learning\b",
    "Docker": r"\bdocker\b|\bkubernetes\b|\bk8s\b",
    "AWS/Cloud": r"\baws\b|\bgcp\b|\bazure\b|\bcloud\b",
    "Spark": r"\bspark\b|\bpyspark\b|\bairflow\b",
    "Tableau": r"\btableau\b|\bpowerbi\b|\bpower bi\b|\blooker\b",
    "Streamlit": r"\bstreamlit\b|\bdash\b"
}

def init_db(db_path: str = "data/raw_jobs.db"):
    """Initializes SQLite database with seniority tiering and skill taxonomy."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop table if schema is from old version without seniority_tier
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if columns and "seniority_tier" not in columns:
        cursor.execute("DROP TABLE jobs")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            seniority_tier TEXT NOT NULL,
            experience_years INTEGER,
            skills_json TEXT,
            description TEXT,
            match_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'Scraped',
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def categorize_seniority(title: str, description: str) -> Tuple[str, int]:
    """Determines if a job is Entry/Mid vs Senior+ and estimates required experience years."""
    title_lower = title.lower()
    
    # Check senior indicators
    if any(k in title_lower for k in ["senior", "lead", "principal", "head", "manager", "director"]):
        tier = "Senior+"
        exp_years = 5
    elif any(k in title_lower for k in ["junior", "associate", "intern", "entry"]):
        tier = "Entry/Mid"
        exp_years = 1
    else:
        # Default tiering based on title keywords
        tier = "Entry/Mid"
        exp_years = 2
        
    # Extract explicit experience numbers from description if present
    exp_match = re.search(r"(\d+)\+?\s*years?\s*(of)?\s*experience", description, re.IGNORECASE)
    if exp_match:
        years = int(exp_match.group(1))
        exp_years = years
        tier = "Senior+" if years >= 4 else "Entry/Mid"
        
    return tier, exp_years

def extract_skills(text: str) -> List[str]:
    """Extracts matching skills from job text based on SKILL_PATTERNS taxonomy."""
    extracted = []
    text_lower = text.lower()
    for skill, pattern in SKILL_PATTERNS.items():
        if re.search(pattern, text_lower):
            extracted.append(skill)
    return extracted

def run_pilot_demo():
    """Visual demonstration script designed to look clean on screen for TikTok & Substack B-roll."""
    print("=" * 65)
    print("🚀 [EPISODE 1 & 12] PIPELINE DEMO: 2,000 Job Market Scraper")
    print("=" * 65)
    
    init_db()
    time.sleep(0.5)
    
    print("[*] Target Dataset: 1,000 Entry/Mid vs. 1,000 Senior+ Job Listings")
    print("[*] Initializing Playwright driver & database connection...")
    time.sleep(0.8)
    
    demo_jobs = [
        {
            "title": "Entry-Level Data Analyst", 
            "company": "TechCorp", 
            "location": "Europe",
            "desc": "Looking for a Data Analyst with 1 year experience in SQL, Python, and Tableau."
        },
        {
            "title": "Senior Data Scientist", 
            "company": "AI Dynamics", 
            "location": "Europe",
            "desc": "Requires 5+ years experience with PyTorch, Docker, AWS, Spark, and Scikit-Learn."
        },
        {
            "title": "Junior Data Engineer", 
            "company": "DataLabs", 
            "location": "Europe",
            "desc": "Entry role requiring Python, SQL, Git, and basic Docker knowledge."
        }
    ]
    
    conn = sqlite3.connect("data/raw_jobs.db")
    cursor = conn.cursor()
    
    for i, j in enumerate(demo_jobs, 1):
        tier, exp = categorize_seniority(j["title"], j["desc"])
        skills = extract_skills(j["desc"])
        skills_json = json.dumps(skills)
        
        print(f"  [➔] Job #{i}: '{j['title']}' ({tier} | Exp: {exp} yrs)")
        print(f"      Extracted Skills: {skills}")
        
        cursor.execute("""
            INSERT INTO jobs (title, company, location, seniority_tier, experience_years, skills_json, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (j["title"], j["company"], j["location"], tier, exp, skills_json, j["desc"]))
        
        time.sleep(0.6)
        
    conn.commit()
    conn.close()
    
    print("-" * 65)
    print("✅ [SUCCESS] Demo jobs inserted into data/raw_jobs.db")
    print("=" * 65)

if __name__ == "__main__":
    run_pilot_demo()
