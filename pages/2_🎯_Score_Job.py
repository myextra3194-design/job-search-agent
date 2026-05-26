"""Page 2 \u2014 Paste a Job Description, get 10-criterion score."""
import streamlit as st
from utils.scorer import score_job
from utils.tracker import add_job
import plotly.graph_objects as go

st.set_page_config(page_title="Score a Job", page_icon="\U0001F3AF", layout="wide")
st.title("\U0001F3AF Job Description Scorer")
st.caption("Paste any job posting (title + description) \u2192 instant 10-criterion match score against Musthafa's profile.")

with st.form("score_form"):
    c1, c2 = st.columns(2)
    company = c1.text_input("Company (optional)")
    role = c2.text_input("Role title (optional)")
    c3, c4 = st.columns(2)
    location = c3.text_input("Location (optional)")
    url = c4.text_input("Job URL (optional)")
    jd_text = st.text_area(
        "Paste full job description here \u2b07\ufe0f",
        height=300,
        placeholder="Paste the complete job posting \u2014 title, location, requirements, responsibilities, years of experience\u2026",
    )
    submitted = st.form_submit_button("\u26A1 Score this Job", type="primary", use_container_width=True)

if submitted:
    if not jd_text.strip():
        st.error("Please paste a job description first.")
    else:
        full_text = f"{role} {company} {location} {jd_text}"
        result = score_job(full_text)

        # ----- summary card -----
        tier_color = {"excellent": "#2ea043", "good": "#d29922",
                      "optional": "#db6d28", "skip": "#f85149"}[result["tier_class"]]
        st.markdown(
            f"""
            <div style='background:{tier_color};padding:24px;border-radius:14px;
                        text-align:center;margin:20px 0'>
              <div style='color:white;font-size:48px;font-weight:bold'>{result['total']}/100</div>
              <div style='color:white;font-size:18px;margin-top:6px'>{result['tier']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----- radar chart -----
        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.subheader("\U0001F4CA Score Breakdown")
            categories = [b["criterion"] for b in result["breakdown"]]
            values = [b["score"] for b in result["breakdown"]]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                line=dict(color="#1f6feb"),
                fillcolor="rgba(31,111,235,0.3)",
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                showlegend=False,
                height=420,
                margin=dict(l=40, r=40, t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.subheader("\U0001F50D Per-Criterion Detail")
            for b in result["breakdown"]:
                pct = b["score"] * 10
                bar_color = "#2ea043" if b["score"] >= 7 else ("#d29922" if b["score"] >= 4 else "#f85149")
                st.markdown(
                    f"""
                    <div style='margin-bottom:10px'>
                      <div style='display:flex;justify-content:space-between'>
                        <span style='color:#e6edf3;font-size:14px'><b>{b['criterion']}</b></span>
                        <span style='color:{bar_color};font-weight:bold'>{b['score']}/10</span>
                      </div>
                      <div style='background:#30363d;border-radius:4px;height:6px;margin-top:4px'>
                        <div style='background:{bar_color};width:{pct}%;height:6px;border-radius:4px'></div>
                      </div>
                      <div style='color:#8b949e;font-size:12px;margin-top:3px'>{b['reason']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ----- recommended action -----
        st.divider()
        st.subheader("\U0001F4A1 Recommended Action")
        cv_recommendation = "CV_SUBSTATION_OAM"
        text_lc = jd_text.lower()
        if any(t in text_lc for t in ["protection", "relay", "iec 61850", "numerical relay"]):
            cv_recommendation = "CV_PROTECTION_RELAY"
        elif any(t in text_lc for t in ["commissioning", "testing", "energization", "fat", "sat"]):
            cv_recommendation = "CV_COMMISSIONING"
        elif "kahramaa" in text_lc or "qatar" in text_lc:
            cv_recommendation = "CV_QATAR_UTILITY"
        elif "saudi" in text_lc or "uae" in text_lc or "oman" in text_lc:
            cv_recommendation = "CV_GCC_GENERAL"

        st.info(f"**Suggested CV version:** `{cv_recommendation}` \u2014 generate it on the **Generate CV** page.")

        if result["total"] >= 70:
            if st.button("\U0001F4CC Save this job to Tracker", type="primary", use_container_width=True):
                add_job({
                    "company": company or "—",
                    "role_title": role or "(see notes)",
                    "location": location or "—",
                    "source_platform": "Manual",
                    "job_url": url,
                    "match_score": str(result["total"]),
                    "cv_version_used": cv_recommendation,
                    "status": "Saved",
                    "notes": jd_text[:500],
                })
                st.success("\u2705 Saved to tracker. See the **Tracker** page to update status.")
        else:
            st.warning("Low match \u2014 consider skipping or only apply if low effort (e.g. Easy Apply).")
