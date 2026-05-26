"""
Personal Job Search Agent \u2014 Streamlit App
Candidate: Muhammed Musthafa K
Run: streamlit run app.py
"""
import streamlit as st
from utils.profile_loader import load_profile
from utils.tracker import stats

st.set_page_config(
    page_title="Musthafa | Job Search Agent",
    page_icon="\u26A1",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Header ----------
profile = load_profile()
p = profile["personal"]

st.markdown(
    f"""
    <div style='background:linear-gradient(135deg,#1f6feb,#0d3a73);
                padding:28px 32px;border-radius:14px;margin-bottom:24px'>
      <h1 style='color:white;margin:0;font-size:30px'>\u26A1 Personal Job Search Agent</h1>
      <p style='color:#cfe2ff;margin:8px 0 0;font-size:15px'>
        Autonomous job search, scoring, CV generation & tracking for
        <b>{p['full_name']}</b> &middot; {profile['total_experience_years']} yrs Substation O&M &middot; {p['location']}
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- KPI row ----------
s = stats()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Jobs Tracked", s["total_tracked"])
c2.metric("Applied", s["applied"])
c3.metric("Interviews", s["interviews"])
c4.metric("Offers", s["offers"])
c5.metric("Response Rate", f"{s['response_rate_pct']}%")

st.divider()

# ---------- Nav cards ----------
st.subheader("\U0001F9ED Navigate")
nav_col = st.columns(5)
nav_items = [
    ("\U0001F50D Find Jobs", "Live search Bayt / GulfTalent / Naukri + multi-platform click-through links", "pages/1_\U0001F50D_Find_Jobs.py"),
    ("\U0001F3AF Score a Job", "Paste any JD \u2192 10-point match score", "pages/2_\U0001F3AF_Score_Job.py"),
    ("\U0001F4DD Generate CV", "5 tailored CV versions + cover letter", "pages/3_\U0001F4DD_Generate_CV.py"),
    ("\U0001F4CB Tracker", "Add, update, follow-up applications", "pages/4_\U0001F4CB_Tracker.py"),
    ("\U0001F464 Profile", "Edit master profile (locked rules)", "pages/5_\U0001F464_Profile.py"),
]
for col, (label, desc, _) in zip(nav_col, nav_items):
    with col:
        st.markdown(
            f"""
            <div style='background:#161b22;padding:18px;border-radius:10px;
                        border:1px solid #30363d;min-height:140px'>
              <div style='font-size:17px;font-weight:600;color:#e6edf3'>{label}</div>
              <div style='font-size:13px;color:#8b949e;margin-top:8px'>{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# ---------- Today's briefing ----------
st.subheader("\U0001F4C5 Today's Briefing")
from datetime import date
weekday = date.today().strftime("%A")
schedule = {
    "Monday": "LinkedIn + Bayt + Indeed Qatar",
    "Tuesday": "GulfTalent + NaukriGulf + Monster Gulf",
    "Wednesday": "LinkedIn + Glassdoor + Qatar Living",
    "Thursday": "Bayt + Dubizzle + Company Career Pages",
    "Friday": "LinkedIn + Energy Jobline + Rigzone",
    "Saturday": "KAHRAMAA + DEWA + SEC + PGCIL Careers",
    "Sunday": "Weekly review + setup next-week alerts",
}
b1, b2 = st.columns([2, 1])
with b1:
    st.info(f"**Today is {weekday}, {date.today().strftime('%d %B %Y')}**\n\n"
            f"**Platform schedule:** {schedule[weekday]}\n\n"
            f"**Today's KPI targets:** 2\u20133 applications \u2022 3\u20135 LinkedIn connects \u2022 1\u20132 recruiter messages")
with b2:
    st.success("**Honesty lock active**\n\n"
               f"\u2705 Max claim: {profile['honesty_rules']['max_years_claim']} years\n\n"
               f"\u2705 Current title: {profile['honesty_rules']['current_title_locked']}\n\n"
               "\u2705 LOA-authorized (KAHRAMAA)")

st.caption("\U0001F449 Use the sidebar to navigate to any tool. Your data is saved locally between sessions.")
