# \u26A1 Personal Job Search Agent \u2014 Streamlit App
**For: Muhammed Musthafa K** \u2014 Substation O&M Engineer (Qatar)

A full working web app that searches live job boards, scores postings against your profile, generates tailored CVs & cover letters, and tracks your entire application pipeline.

---

## \U0001F3AF What it does

| Feature | Description |
|---|---|
| **\U0001F50D Find Jobs** | Live scrape of Bayt, GulfTalent, NaukriGulf + one-click search URLs for LinkedIn, Indeed, Glassdoor, Monster, Rigzone |
| **\U0001F3AF Score Job** | Paste any JD \u2192 10-criterion match score (Role, Experience, Location, Employer, Tech, Voltage, Salary, Growth, Visa, Application Ease) with radar chart |
| **\U0001F4DD Generate CV** | 5 tailored CV versions: Substation O&M / Protection Relay / Qatar Utility / Commissioning / GCC General + tailored cover letters |
| **\U0001F4CB Tracker** | Full CSV-backed application tracker with KPIs, status updates, source analysis charts, follow-up dates |
| **\U0001F464 Profile** | Edit contact info (email/phone/LinkedIn); honesty-locked experience/title fields (never inflate beyond 7 years) |

---

## \U0001F680 Run locally (3 steps)

```bash
# 1. Install Python 3.9+ if not already
# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
streamlit run app.py
```

Open the URL it prints (usually `http://localhost:8501`).

---

## \u2601\ufe0f Deploy free to Streamlit Cloud

1. Push this `job_search_app/` folder to a new **GitHub repo** (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** \u2192 select your repo \u2192 main branch \u2192 `app.py`.
4. Deploy. You'll get a public URL like `https://musthafa-jobsearch.streamlit.app`.
5. Access from any device, including your phone.

**Free tier limits:** 1 GB RAM, sleeps after 7 days of inactivity (instant wake on visit).

---

## \U0001F4C1 Project structure

```
job_search_app/
\u251c\u2500\u2500 app.py                          # Home page (dashboard + KPIs)
\u251c\u2500\u2500 requirements.txt
\u251c\u2500\u2500 .streamlit/config.toml          # Dark theme
\u251c\u2500\u2500 pages/
\u2502   \u251c\u2500\u2500 1_\U0001F50D_Find_Jobs.py
\u2502   \u251c\u2500\u2500 2_\U0001F3AF_Score_Job.py
\u2502   \u251c\u2500\u2500 3_\U0001F4DD_Generate_CV.py
\u2502   \u251c\u2500\u2500 4_\U0001F4CB_Tracker.py
\u2502   \u2514\u2500\u2500 5_\U0001F464_Profile.py
\u251c\u2500\u2500 utils/
\u2502   \u251c\u2500\u2500 profile_loader.py          # Load/save profile JSON
\u2502   \u251c\u2500\u2500 scorer.py                  # 10-point job evaluation matrix
\u2502   \u251c\u2500\u2500 cv_generator.py            # 5 CV templates + cover letter
\u2502   \u251c\u2500\u2500 job_search.py              # Bayt/GulfTalent/Naukri scrapers
\u2502   \u2514\u2500\u2500 tracker.py                 # CSV-backed pipeline
\u2514\u2500\u2500 data/
    \u251c\u2500\u2500 profile.json               # Locked candidate profile
    \u251c\u2500\u2500 keywords.json              # Search keyword library
    \u2514\u2500\u2500 jobs.csv                   # Live tracker data (persisted)
```

---

## \U0001F510 Honesty Rules (hard-coded, cannot be bypassed)

- Max experience claim: **7 years**
- Current title: **Substation Technical Assistant** (never "Senior Engineer")
- Employer: via **KEIC**, not direct KAHRAMAA
- No P.Eng / PE / CEng claims
- Trainee role always labelled

These are enforced inside `data/profile.json` + CV templates.

---

## \u26A0\ufe0f About live scraping

- **Bayt / GulfTalent / NaukriGulf**: scraped via public HTML \u2014 may fail occasionally if they change layout. Fallback = one-click search URL.
- **LinkedIn / Indeed / Glassdoor**: heavy anti-bot \u2014 only one-click URLs (you'll see results in browser).
- All scraping is polite (single request per source, 8s timeout, proper User-Agent).

---

## \U0001F4DA First-run checklist

1. \u2705 Open the **Profile** page \u2192 add your **email / phone / LinkedIn URL**
2. \u2705 Open **Find Jobs** \u2192 try keyword "Substation Engineer" + Qatar
3. \u2705 Open **Generate CV** \u2192 create `CV_QATAR_UTILITY` \u2192 download
4. \u2705 Apply to 2-3 jobs today \u2192 save them in **Tracker**
5. \u2705 Update statuses as responses come in

Good luck, Musthafa \U0001F680
