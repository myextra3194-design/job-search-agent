"""
Personal Job Search Agent — Streamlit App
Candidate: Muhammed Musthafa K
Run: streamlit run app.py
"""
import streamlit as st
from utils.profile_loader import load_profile
from utils.tracker import stats

st.set_page_config(
    page_title="Musthafa | Job Search Agent",
    page_icon="⚡",
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
      <h1 style='color:white;margin:0;font-size:30px'>⚡ Personal Job Search Agent</h1>
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

# ---------- NEW FEATURE highlight ----------
st.markdown(
    """
    <div style='background:linear-gradient(135deg,#2ea043,#1a6b2a);
                padding:20px 24px;border-radius:12px;margin-bottom:20px'>
      <div style='color:white;font-size:18px;font-weight:600'>
        🆕 NEW: Smart Match — Search ALL job boards by YOUR CV keywords
      </div>
      <div style='color:#d4ffe0;font-size:13px;margin-top:6px'>
        Upload your CV → app extracts every keyword → searches LinkedIn + Indeed + Naukri +
        Bayt + GulfTalent + Glassdoor + Rigzone via Google meta-search →
        scores jobs by % match → 1-click Smart Apply
      </div>
      <div style='color:#a7f3a7;font-size:12px;margin-top:8px'>
        👉 Click <b>🎯 Smart Match</b> in the left sidebar
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Nav cards ----------
st.subheader("🧭 All Tools")
nav_col = st.columns(3)
nav_items = [
    ("🎯 Smart Match", "🆕 CV keywords → search ALL boards → % match → Smart Apply"),
    ("🔍 Find Jobs", "Live search Bayt / GulfTalent / Naukri + multi-platform links"),
    ("🎯 Score a Job", "Paste any JD → 10-point match score with radar chart"),
    ("📝 Generate CV", "5 tailored CV versions + cover letter generator"),
    ("📋 Tracker", "Full pipeline tracker with KPIs, status updates, exports"),
    ("👤 Profile", "Edit contact info (experience locked)"),
]
for i, (label, desc) in enumerate(nav_items):
    with nav_col[i % 3]:
        st.markdown(
            f"""
            <div style='background:#161b22;padding:18px;border-radius:10px;
                        border:1px solid #30363d;min-height:120px;margin-bottom:12px'>
              <div style='font-size:16px;font-weight:600;color:#e6edf3'>{label}</div>
              <div style='font-size:12px;color:#8b949e;margin-top:8px'>{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# ---------- Today's briefing ----------
st.subheader("📅 Today's Briefing")
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
            f"**Today's KPI targets:** 2–3 applications · 3–5 LinkedIn connects · 1–2 recruiter messages")
with b2:
    st.success("**Honesty lock active**\n\n"
               f"✅ Max claim: {profile['honesty_rules']['max_years_claim']} years\n\n"
               f"✅ Current title: {profile['honesty_rules']['current_title_locked']}\n\n"
               "✅ LOA-authorized (KAHRAMAA)")

st.caption("👉 Use the sidebar to navigate to any tool. Your data is saved between sessions.")
