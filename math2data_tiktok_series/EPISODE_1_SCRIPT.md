# 🎬 Episode 1 (PILOT) Detailed Script & Production Guide (Revised)

**Title:** *What BSc, MSc & PhD Degrees Teach vs. What Data Science Companies ACTUALLY Want*  
**Series:** *Doctorate to Data (Episode 1 of 22)*  
**Target Duration:** ~65–75 seconds (Optimized for TikTok Creator Rewards Monetization)  
**Format:** Hybrid Relatable Skit + Degree Comparison + Authentic Learning B-Roll + CTA  

---

## 📌 Scene Breakdown & Shot List

```
┌──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┐
│ 0:00 - 0:10                      │ 0:10 - 0:45                      │ 0:45 - 1:10                      │
│ 1. The Math PhD vs SQL Skit      │ 2. BSc vs MSc vs PhD vs Company  │ 3. Random Code + SQLite Error    │
│ (LaTeX Papers vs. Entry Job JD)  │ (Degree Curriculum Reality Check)│ (Follow for Episode 2!)          │
└──────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┘
```

---

## 🎙️ Timestamped Word-for-Word Script & Shot Table

| Time | Audio / Spoken Script | Visual / B-Roll / Action | On-Screen Text & SFX |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:08** | *"I spent 5 years solving partial differential equations for a Math PhD... and I just got rejected from an entry-level analyst job because I don't know SQL."* | **Talking head (Casual/Hoodie):** Holding a thick stack of printed math thesis papers or LaTeX PDF, looking at computer in disbelief. | **Text:** *Math PhD vs. Entry-Level SQL* 📉 <br>**SFX:** Rejection buzzer 🔊 |
| **0:08 - 0:25** | *"Here's the funny thing about higher education vs. real life:* <br>• **BSc in Data Science:** Teaches linear algebra & toy Jupyter notebooks. <br>• **MSc in Data Science:** Teaches deep learning & clean Kaggle datasets. <br>• **PhD in STEM:** Teaches 40-page LaTeX theoretical proofs. <br>• **What companies ACTUALLY want:** `SELECT * FROM sales_data WHERE status = 'Active';`"* | **Cut to Screen / On-screen Text Bubbles:** Fast graphic/text popups comparing the 3 degree levels vs the single 1-line SQL query companies ask for. | **Graphics:** <br>🎓 *BSc:* Toy Notebooks <br>🎓 *MSc:* Kaggle Datasets <br>🎓 *PhD:* 40-page Proofs <br>💼 *Company:* Basic SQL 📊 |
| **0:25 - 0:42** | *"None of our degrees teach real-world data engineering. We learn how to build complex neural networks, but nobody taught us how to query a relational database."* | **Cut to B-Roll:** Terminal in VS Code (Dark Mode). Typing random Python scripts, browsing a SQL cheat sheet on screen. | **Text:** *The Curriculum Gap* 🔍 <br>**SFX:** Keyboard typing ⌨️ |
| **0:42 - 0:55** | *"Watch this: I'm writing my first SQLite query on camera right now, and I literally forgot the semicolon on my first try."* | **Screen Recording:** Close-up of terminal showing SQLite error `OperationalError: near "FROM": syntax error`, fixing it by adding `;`, and seeing clean rows print. | **Text:** *First SQL Query Error* 💀 <br>**SFX:** Funny error pop 🔔 |
| **0:55 - 1:10** | *"Over the next 20 episodes, I'm building an automated Python scraper & SQL database pipeline on camera to teach myself real-world data engineering. Follow along for Episode 2!"* | **Talking head:** Enthusiastic cut. Pointing to follow button / bio link. | **Text:** *Follow Ep 2: Building the Scraper!* 🐍 |

---

## 📽️ Filming Directions & Props Checklist

1. **Props & Visuals:**
   * Printed math thesis / LaTeX document OR tablet showing whiteboard equations.
   * On-screen text bubbles for BSc vs MSc vs PhD vs Company.
2. **VS Code Workspace Setup:**
   * Open `math2data_tiktok_series/` in VS Code.
   * Terminal running Python/SQLite interactive shell (`sqlite3 data/raw_jobs.db`).
   * Raw SQL query: `SELECT title, company FROM jobs;`

---

## 💻 Starter Code to Run on Camera for Episode 1 (SQL Learning Moment)

```bash
cd math2data_tiktok_series

# Launch SQLite interactively on camera!
sqlite3 data/raw_jobs.db

# Type query on screen (forget semicolon first, hit enter, then add ';'!):
SELECT title, company FROM jobs
```
