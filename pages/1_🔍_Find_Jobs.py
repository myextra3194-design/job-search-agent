"""Page 1 \u2014 Live Job Search"""
import streamlit as st
from utils.job_search import search_all, build_search_urls
from utils.scorer import score_job
from utils.tracker import add_job

st.set_page_config(page_title="Find Jobs", page_icon="\U0001F50D", layout="wide")
st.title("\U0001F50D Find Jobs \u2014 Live Search")
st.caption("Scrapes Bayt, GulfTalent, NaukriGulf + provides one-click search URLs for LinkedIn, Indeed, Glassdoor, Monster, Rigzone.")

# ---------- Search form ----------
with st.form("search_form"):
    c1, c2, c3 = st.columns([2, 1, 1])
    keyword = c1.text_input("Job title / keywords",
                            value="Substation Engineer",
                            help="e.g. 'Substation Engineer', 'Protection Relay', 'HV Engineer'")
    location = c2.selectbox("Location",
                            ["Qatar", "UAE", "Saudi Arabia", "Oman",
                             "Kuwait", "Bahrain", "India"],
                            index=0)
    sources = c3.multiselect(
        "Scrape sources",
        ["Bayt", "GulfTalent", "NaukriGulf"],
        default=["Bayt", "GulfTalent", "NaukriGulf"],
    )
    submitted = st.form_submit_button("\U0001F680 Search Now", use_container_width=True, type="primary")

# ---------- One-click search URLs (always shown) ----------
st.subheader("\U0001F310 One-click search across all major platforms")
urls = build_search_urls(keyword, location)
url_cols = st.columns(4)
for i, (platform, link) in enumerate(urls.items()):
    with url_cols[i % 4]:
        st.link_button(platform, link, use_container_width=True)

st.divider()

# ---------- Live scrape results ----------
if submitted:
    with st.spinner(f"Searching {len(sources)} job boards for '{keyword}' in {location}\u2026"):
        data = search_all(keyword, location, sources)

    results = data["results"]
    errors = data["errors"]

    if errors:
        for src, err in errors.items():
            st.warning(f"\u26A0\ufe0f {src} returned no results ({err[:60]}). Use one-click button above instead.")

    if not results:
        st.info("No live results scraped \u2014 use the **one-click search buttons above** to view listings directly.")
    else:
        st.success(f"\u2705 Found **{len(results)}** live results. Click any to score & save.")

        for idx, r in enumerate(results):
            score = score_job(f"{r['title']} {r['snippet']} {r['location']}")
            tier_color = {"excellent": "#2ea043", "good": "#d29922",
                          "optional": "#db6d28", "skip": "#f85149"}[score["tier_class"]]
            with st.container(border=True):
                cc1, cc2 = st.columns([4, 1])
                with cc1:
                    st.markdown(f"### {r['title']}")
                    st.markdown(
                        f"**{r['company']}** &middot; {r['location']} &middot; "
                        f"<span style='color:#8b949e'>[{r['source']}]</span>",
                        unsafe_allow_html=True)
                    if r.get("snippet"):
                        st.caption(r["snippet"][:280] + ("\u2026" if len(r["snippet"]) > 280 else ""))
                    st.link_button("\U0001F517 View on " + r["source"], r["url"])
                with cc2:
                    st.markdown(
                        f"<div style='text-align:center;background:{tier_color};"
                        f"color:white;padding:14px;border-radius:10px'>"
                        f"<div style='font-size:28px;font-weight:bold'>{score['total']}/100</div>"
                        f"<div style='font-size:11px;margin-top:4px'>{score['tier']}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button("\U0001F4CC Save to Tracker", key=f"save_{idx}", use_container_width=True):
                        add_job({
                            "company": r["company"],
                            "role_title": r["title"],
                            "location": r["location"],
                            "source_platform": r["source"],
                            "job_url": r["url"],
                            "match_score": str(score["total"]),
                            "status": "Saved",
                            "notes": r.get("snippet", "")[:200],
                        })
                        st.success("Saved to tracker \u2705")
                with st.expander("\U0001F50E See 10-criterion score breakdown"):
                    for b in score["breakdown"]:
                        st.write(f"- **{b['criterion']}** \u2014 {b['score']}/10 \u2014 _{b['reason']}_")
else:
    st.info("\U0001F4A1 Enter a keyword and click **Search Now** to scrape live job boards. "
            "Or use the **one-click buttons above** to open searches in your browser directly.")
