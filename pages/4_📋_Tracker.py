"""Page 4 \u2014 Application Tracker"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from utils.tracker import (load_jobs, add_job, update_status, delete_job,
                           STATUS_OPTIONS, stats, save_jobs)
from utils.cv_generator import CV_TEMPLATES

st.set_page_config(page_title="Tracker", page_icon="\U0001F4CB", layout="wide")
st.title("\U0001F4CB Application Tracker")

# ---------- KPI strip ----------
s = stats()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total in pipeline", s["total_tracked"])
k2.metric("Applied", s["applied"])
k3.metric("Interviews", s["interviews"])
k4.metric("Offers", s["offers"])
k5.metric("Response rate", f"{s['response_rate_pct']}%")

st.divider()

# ---------- Add new ----------
with st.expander("\u2795 Add a job manually"):
    with st.form("add_job_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("Company *")
        role = c2.text_input("Role title *")
        c3, c4 = st.columns(2)
        loc = c3.text_input("Location")
        source = c4.selectbox("Source platform",
                              ["LinkedIn", "Bayt", "GulfTalent", "NaukriGulf",
                               "Indeed", "Glassdoor", "Company Portal",
                               "Referral", "Manual"])
        c5, c6 = st.columns(2)
        url = c5.text_input("Job URL")
        match = c6.number_input("Match score", min_value=0, max_value=100, value=70)
        c7, c8 = st.columns(2)
        cv = c7.selectbox("CV version used", [""] + list(CV_TEMPLATES.keys()))
        status = c8.selectbox("Status", STATUS_OPTIONS, index=0)
        notes = st.text_area("Notes")
        if st.form_submit_button("Add to tracker", type="primary"):
            if not company or not role:
                st.error("Company and role are required.")
            else:
                add_job({
                    "company": company, "role_title": role,
                    "location": loc, "source_platform": source,
                    "job_url": url, "match_score": str(match),
                    "cv_version_used": cv, "status": status,
                    "date_applied": date.today().isoformat() if status != "Saved" else "",
                    "notes": notes,
                })
                st.success("Added \u2705 \u2014 reload page to see in table below.")

# ---------- Charts ----------
df = load_jobs()
if len(df):
    cc1, cc2 = st.columns(2)
    with cc1:
        st.subheader("Pipeline by Status")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig1 = px.bar(status_counts, x="Status", y="Count",
                      color="Status", height=320,
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig1.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig1, use_container_width=True)
    with cc2:
        st.subheader("Applications by Source")
        src_counts = df[df["source_platform"] != ""]["source_platform"].value_counts().reset_index()
        src_counts.columns = ["Source", "Count"]
        if len(src_counts):
            fig2 = px.pie(src_counts, names="Source", values="Count", hole=0.45, height=320)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No source data yet.")

# ---------- Filter + edit table ----------
st.subheader("\U0001F4D1 All Applications")

if not len(df):
    st.info("No applications tracked yet. Add some via the form above, or save from **Find Jobs** / **Score a Job** pages.")
else:
    f1, f2, f3 = st.columns([2, 2, 2])
    status_filter = f1.multiselect("Filter by status", STATUS_OPTIONS, default=STATUS_OPTIONS)
    source_filter = f2.multiselect("Filter by source",
                                   sorted(df["source_platform"].unique()),
                                   default=list(sorted(df["source_platform"].unique())))
    search_str = f3.text_input("\U0001F50D Search company / role")

    fdf = df[df["status"].isin(status_filter)]
    fdf = fdf[fdf["source_platform"].isin(source_filter)]
    if search_str:
        mask = (fdf["company"].str.contains(search_str, case=False, na=False) |
                fdf["role_title"].str.contains(search_str, case=False, na=False))
        fdf = fdf[mask]

    st.caption(f"Showing **{len(fdf)}** of {len(df)} applications")

    # editable mini-cards
    for _, row in fdf.iterrows():
        score = int(row["match_score"]) if str(row["match_score"]).isdigit() else 0
        color = "#2ea043" if score >= 85 else ("#d29922" if score >= 70 else ("#db6d28" if score >= 55 else "#f85149"))
        with st.container(border=True):
            top1, top2, top3 = st.columns([4, 1, 1])
            with top1:
                st.markdown(f"### #{row['app_id']} \u2014 {row['role_title']}")
                st.markdown(f"**{row['company']}** &middot; {row['location']} &middot; *{row['source_platform']}*")
                if row["job_url"]:
                    st.markdown(f"[\U0001F517 View posting]({row['job_url']})")
                if row["notes"]:
                    with st.expander("Notes"):
                        st.write(row["notes"])
            with top2:
                st.markdown(
                    f"<div style='background:{color};color:white;padding:10px;"
                    f"text-align:center;border-radius:8px'><b>{score}/100</b><br>"
                    f"<small>{row['status']}</small></div>",
                    unsafe_allow_html=True,
                )
            with top3:
                new_status = st.selectbox("Update", STATUS_OPTIONS,
                                          index=STATUS_OPTIONS.index(row["status"]) if row["status"] in STATUS_OPTIONS else 0,
                                          key=f"st_{row['app_id']}",
                                          label_visibility="collapsed")
                if st.button("Update", key=f"upd_{row['app_id']}", use_container_width=True):
                    extra = {}
                    if new_status == "Applied" and not row["date_applied"]:
                        extra["date_applied"] = date.today().isoformat()
                    update_status(row["app_id"], new_status, extra)
                    st.rerun()
                if st.button("\U0001F5D1\ufe0f Delete", key=f"del_{row['app_id']}", use_container_width=True):
                    delete_job(row["app_id"])
                    st.rerun()

    # ---------- Export ----------
    st.divider()
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("\u2b07\ufe0f Export full tracker as CSV", csv_bytes,
                       file_name="job_tracker_export.csv", mime="text/csv")
