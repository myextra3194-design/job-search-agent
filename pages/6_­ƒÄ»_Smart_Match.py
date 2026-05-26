"""Page 6 — Smart Match
The flagship feature: extract YOUR CV keywords, search jobs across all
major boards via Google meta-search, score each job by % match to YOUR
keywords, and offer 1-click Smart Apply.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from utils.profile_loader import load_profile
from utils.cv_parser import (
    extract_keywords_from_profile,
    extract_keywords_from_text,
    parse_uploaded_file,
    merge_keywords,
)
from utils.keyword_matcher import score_job_vs_keywords, tier_from_pct
from utils.google_search import google_meta_search, JOB_SITES
from utils.job_search import scrape_bayt, scrape_gulftalent, scrape_naukrigulf
from utils.smart_apply import build_apply_kit
from utils.tracker import add_job
from utils.scorer import score_job  # for combined scoring

st.set_page_config(page_title="Smart Match", page_icon="🎯", layout="wide")
st.title("🎯 Smart Match — Find Jobs That Match YOUR CV")
st.caption(
    "Upload your CV → app extracts every keyword → searches all major boards → "
    "scores each job by % match → 1-click Smart Apply."
)

profile = load_profile()

# ============================================================
# STEP 1 — Build keyword profile (cached in session)
# ============================================================
st.subheader("Step 1️⃣ — Build your keyword profile")

with st.expander("📄 Upload your CV (optional but recommended)", expanded=False):
    st.caption("Supported: PDF, DOCX, TXT, MD. The app extracts keywords from your actual CV "
               "on top of the structured profile data.")
    uploaded_cv = st.file_uploader(
        "Upload CV file",
        type=["pdf", "docx", "txt", "md"],
        help="Your real CV — exact title, exact tech, exact projects."
    )
    use_profile = st.checkbox(
        "Also include keywords from structured profile (Profile page)",
        value=True,
    )

# Build keyword set
if st.button("🔬 Extract My Keywords", type="primary", use_container_width=True):
    sources = []
    if use_profile:
        sources.append(extract_keywords_from_profile(profile))
    if uploaded_cv:
        cv_text = parse_uploaded_file(uploaded_cv)
        if cv_text and len(cv_text) > 30:
            sources.append(extract_keywords_from_text(cv_text))
            st.success(f"✅ Extracted from uploaded CV ({len(cv_text)} chars)")
        else:
            st.warning("⚠️ Could not read CV file — using profile only.")
    if not sources:
        sources.append(extract_keywords_from_profile(profile))
    merged = merge_keywords(*sources)
    st.session_state["cv_keywords"] = merged
    st.success(f"🎯 Found **{len(merged['all_keywords'])}** unique keywords "
               f"({len(merged['technical_phrases'])} technical phrases).")

# Display keywords if extracted
if "cv_keywords" in st.session_state:
    kw = st.session_state["cv_keywords"]
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🔧 Top Technical Phrases** _(high-weight matchers)_")
        if kw["technical_phrases"]:
            top_tech = kw["technical_phrases"][:15]
            df_tech = pd.DataFrame(top_tech, columns=["Phrase", "Count"])
            st.dataframe(df_tech, hide_index=True, use_container_width=True)
        else:
            st.info("No technical phrases found.")
    with col_b:
        st.markdown("**📌 Top Single Keywords**")
        if kw["single_words"]:
            top_single = kw["single_words"][:15]
            df_single = pd.DataFrame(top_single, columns=["Word", "Count"])
            st.dataframe(df_single, hide_index=True, use_container_width=True)

    with st.expander("👀 See ALL extracted keywords"):
        st.write(sorted(kw["all_keywords"]))

st.divider()

# ============================================================
# STEP 2 — Search jobs across all boards
# ============================================================
st.subheader("Step 2️⃣ — Search jobs across all boards")

if "cv_keywords" not in st.session_state:
    st.info("👆 Click **Extract My Keywords** above first.")
    st.stop()

c1, c2, c3 = st.columns([2, 1, 1])
search_kw = c1.text_input(
    "Job title / role keywords (comma-separated)",
    value="Substation Engineer, Protection Relay Engineer, HV Engineer",
    help="2-3 role titles. The app will search each across all boards.",
)
location = c2.selectbox(
    "Location",
    ["Qatar", "UAE", "Saudi Arabia", "Oman",
     "Kuwait", "Bahrain", "India", "GCC", "Middle East"],
    index=0,
)
min_pct = c3.slider("Minimum % match to show", 0, 100, 30, 5,
                    help="Hide jobs below this CV match %.")

# Source selector
sel = st.multiselect(
    "Boards to search (via Google meta-search)",
    list(JOB_SITES.keys()),
    default=list(JOB_SITES.keys()),
    help="More boards = wider search but slower.",
)

also_scrape = st.checkbox(
    "Also scrape direct (Bayt + GulfTalent + NaukriGulf) for extra results",
    value=True,
)

# ---------- Search button ----------
if st.button("🚀 SMART SEARCH ACROSS ALL BOARDS", type="primary", use_container_width=True):
    keywords_list = [k.strip() for k in search_kw.split(",") if k.strip()]
    if not keywords_list:
        st.error("Enter at least one keyword.")
        st.stop()

    all_results = []
    with st.spinner("🌐 Searching across boards via Google meta-search..."):
        # Google/DDG meta-search (one query per keyword set)
        meta = google_meta_search(keywords_list, location, sel, try_scrape=True)
        for r in meta["results"]:
            r["search_method"] = "Google/DDG"
            all_results.append(r)

        # Direct scrape boards (still useful — gives fresher snippets)
        if also_scrape:
            for kw_term in keywords_list[:2]:  # only top 2 to save time
                try:
                    for r in scrape_bayt(kw_term, location.lower(), 8):
                        r["search_method"] = "Bayt direct"
                        all_results.append(r)
                except Exception:
                    pass
                try:
                    for r in scrape_gulftalent(kw_term, location.lower(), 8):
                        r["search_method"] = "GulfTalent direct"
                        all_results.append(r)
                except Exception:
                    pass
                try:
                    for r in scrape_naukrigulf(kw_term, location.lower(), 8):
                        r["search_method"] = "NaukriGulf direct"
                        all_results.append(r)
                except Exception:
                    pass

    # Deduplicate by URL
    seen = set()
    deduped = []
    for r in all_results:
        u = r.get("url", "")
        if u and u not in seen:
            seen.add(u)
            deduped.append(r)

    # Score each result
    cv_kw = st.session_state["cv_keywords"]
    scored = []
    for r in deduped:
        text_for_match = " ".join([
            r.get("title", ""), r.get("snippet", ""),
            r.get("company", ""), r.get("location", ""),
            r.get("source", "")
        ])
        match = score_job_vs_keywords(text_for_match, cv_kw)
        # Also run the original 10-criterion scorer
        rubric = score_job(text_for_match)
        r["cv_match_pct"] = match["match_pct"]
        r["matched_terms"] = match["matched_technical"] + match["matched_singles"][:5]
        r["missing_critical"] = match["missing_critical"]
        r["rubric_score"] = rubric["total"]
        r["rubric_tier"] = rubric["tier"]
        scored.append(r)

    # Sort by CV match %
    scored.sort(key=lambda x: x["cv_match_pct"], reverse=True)

    # Filter by min %
    visible = [r for r in scored if r["cv_match_pct"] >= min_pct]

    st.session_state["smart_results"] = scored
    st.session_state["smart_visible"] = visible
    st.session_state["smart_meta_urls"] = meta["google_urls"]

# ---------- Show one-click search URLs (always) ----------
if "smart_meta_urls" in st.session_state:
    with st.expander("🌐 Open the same search directly on each board (one-click)"):
        urls = st.session_state["smart_meta_urls"]
        url_cols = st.columns(4)
        for i, (label, link) in enumerate(urls.items()):
            with url_cols[i % 4]:
                st.link_button(label, link, use_container_width=True)

# ============================================================
# STEP 3 — Results
# ============================================================
if "smart_visible" in st.session_state:
    scored = st.session_state["smart_results"]
    visible = st.session_state["smart_visible"]

    st.divider()
    st.subheader(f"Step 3️⃣ — Results: {len(visible)} matching jobs (of {len(scored)} found)")

    # Quick stats
    if scored:
        avg_match = round(sum(r["cv_match_pct"] for r in scored) / len(scored), 1)
        top_match = scored[0]["cv_match_pct"] if scored else 0
        sources_count = len(set(r.get("source", "Web") for r in scored))
        kc1, kc2, kc3, kc4 = st.columns(4)
        kc1.metric("Jobs found", len(scored))
        kc2.metric("Above threshold", len(visible))
        kc3.metric("Top match %", f"{top_match}%")
        kc4.metric("Boards covered", sources_count)

        # Distribution chart
        df_chart = pd.DataFrame([
            {"Source": r.get("source", "Web"), "Match %": r["cv_match_pct"]}
            for r in scored
        ])
        if len(df_chart):
            fig = px.histogram(df_chart, x="Match %", color="Source",
                               nbins=20, height=240, opacity=0.85)
            fig.update_layout(margin=dict(l=20, r=20, t=10, b=20),
                              plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    # Results list
    if not visible:
        st.warning(f"No jobs above {min_pct}% match. Try lowering threshold or "
                   f"using more boards / different keywords.")
    else:
        for idx, r in enumerate(visible[:50]):
            tier = tier_from_pct(r["cv_match_pct"])
            with st.container(border=True):
                col_left, col_right = st.columns([4, 1.3])
                with col_left:
                    st.markdown(f"### {r.get('title','(no title)')}")
                    meta_parts = []
                    if r.get("company") and r["company"] != "—":
                        meta_parts.append(f"**{r['company']}**")
                    if r.get("location"):
                        meta_parts.append(r["location"])
                    meta_parts.append(f"_{r.get('source', 'Web')}_")
                    meta_parts.append(f"_{r.get('search_method', '')}_")
                    st.markdown(" · ".join(meta_parts))
                    if r.get("snippet"):
                        st.caption(r["snippet"][:300])
                    st.markdown(f"**🎯 Matched:** {', '.join(r['matched_terms'][:8]) or 'none'}")
                    if r.get("missing_critical"):
                        st.caption(f"⚠️ Missing from JD: _{', '.join(r['missing_critical'])}_")

                with col_right:
                    st.markdown(
                        f"<div style='background:{tier['color']};color:white;"
                        f"text-align:center;padding:14px;border-radius:10px'>"
                        f"<div style='font-size:30px;font-weight:bold'>{r['cv_match_pct']}%</div>"
                        f"<div style='font-size:11px'>CV MATCH</div>"
                        f"<div style='font-size:10px;margin-top:6px;opacity:0.85'>{tier['label']}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Rubric: {r['rubric_score']}/100")

                # ---------- Smart Apply Kit ----------
                with st.expander("🚀 Smart Apply Kit"):
                    kit = build_apply_kit(
                        job_title=r.get("title", ""),
                        company=r.get("company", "—"),
                        job_url=r.get("url", ""),
                        job_description=r.get("snippet", "") + " " + r.get("title", ""),
                        candidate_name=profile["personal"]["full_name"],
                    )
                    aa, ab = st.columns(2)
                    with aa:
                        st.link_button(
                            "🌐 1. Open Job Posting",
                            kit["apply_url"] or "#",
                            use_container_width=True,
                            disabled=not kit["apply_url"],
                        )
                        if kit["mailto_url"]:
                            st.link_button(
                                f"✉️ 2. Email Application → {kit['primary_email']}",
                                kit["mailto_url"],
                                use_container_width=True,
                            )
                        else:
                            st.caption("ℹ️ No direct application email found in posting. Apply via the portal link above.")

                    with ab:
                        if st.button("📋 Copy pre-filled email body",
                                     key=f"copy_email_{idx}",
                                     use_container_width=True):
                            st.code(kit["email_body"], language="text")
                            st.toast("📋 Select & copy the text above (Ctrl+C)")

                        if st.button("💾 Log to Tracker as 'Applied'",
                                     key=f"log_{idx}",
                                     use_container_width=True,
                                     type="primary"):
                            add_job({
                                "company": r.get("company", "—"),
                                "role_title": r.get("title", "")[:120],
                                "location": r.get("location", ""),
                                "source_platform": r.get("source", "Web"),
                                "job_url": r.get("url", ""),
                                "match_score": str(r["cv_match_pct"]),
                                "status": "Applied",
                                "date_applied": date.today().isoformat(),
                                "notes": f"CV Match: {r['cv_match_pct']}% | Matched: {', '.join(r['matched_terms'][:5])}",
                            })
                            st.success("✅ Logged to Tracker")

                    # Show full kit details
                    if kit["emails_found"]:
                        st.caption(f"📧 Emails found in posting: {', '.join(kit['emails_found'])}")
                    st.text_area("Pre-filled email body (editable):",
                                 value=kit["email_body"],
                                 height=180, key=f"body_{idx}")

# ============================================================
# Help section
# ============================================================
st.divider()
with st.expander("ℹ️ How does Smart Match work?"):
    st.markdown("""
**1. Keyword extraction (CV → keywords)**
- Parses your uploaded PDF/DOCX and/or structured profile
- Recognises **80+ substation-engineering technical phrases** (e.g. "circuit breaker", "IEC 61850", "C&R panel", "KAHRAMAA", "LOA")
- Plus single words excluding stopwords
- Each phrase weighted by frequency in your CV

**2. Multi-board search**
- Uses **Google's `site:` operator** to query LinkedIn, Indeed, Naukri, Bayt, GulfTalent, Glassdoor, Rigzone, Energy Jobline, etc., all in one go
- DuckDuckGo HTML scraping (Google blocks bots; DDG is permissive)
- Plus direct scrape of Bayt, GulfTalent, NaukriGulf for fresher snippets
- Deduplicates by URL

**3. % Match scoring**
- Each found job is compared against YOUR keyword profile
- Technical phrases worth **3x** more than single words
- Score = matched weight / total possible weight × 100

**4. Smart Apply (recruiter-friendly)**
- Detects application emails in the posting
- Opens your email client pre-filled with subject + body
- Provides editable email + copy-to-clipboard
- One-click logs to your tracker

**Why not auto-submit?**
- LinkedIn, Indeed, Naukri **ban accounts that auto-apply**
- Forms have screening questions a bot can't answer well
- Quality > quantity: 5 tailored apps beat 100 spam
- This kit gives you 95% of the speed with 0% of the ban risk
    """)
