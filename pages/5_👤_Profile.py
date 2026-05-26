"""Page 5 \u2014 Edit Master Profile (honesty-locked fields)"""
import streamlit as st
from utils.profile_loader import load_profile, save_profile

st.set_page_config(page_title="Profile", page_icon="\U0001F464", layout="wide")
st.title("\U0001F464 Master Profile")
st.caption("Editable contact info & non-locked sections. Honesty rules cannot be overridden.")

profile = load_profile()
p = profile["personal"]
r = profile["honesty_rules"]

# ---------- Honesty rules (read-only display) ----------
st.warning(
    f"\U0001F512 **Honesty lock active** \u2014 these fields cannot be edited from the UI:\n"
    f"- Max experience claim: **{r['max_years_claim']} years**\n"
    f"- Current title: **{r['current_title_locked']}**\n"
    f"- Never claim: {' \u2022 '.join(r['never_claim'])}"
)

st.divider()

# ---------- Editable contact info ----------
st.subheader("\U0001F4DE Contact Info (edit to populate CVs)")
with st.form("contact_form"):
    c1, c2 = st.columns(2)
    email = c1.text_input("Email", value=p.get("email", ""))
    phone = c2.text_input("Phone (e.g. +974 ...)", value=p.get("phone", ""))
    linkedin = st.text_input("LinkedIn URL", value=p.get("linkedin", ""))
    location = st.text_input("Current location", value=p.get("location", ""))
    if st.form_submit_button("\U0001F4BE Save contact info", type="primary"):
        profile["personal"]["email"] = email
        profile["personal"]["phone"] = phone
        profile["personal"]["linkedin"] = linkedin
        profile["personal"]["location"] = location
        save_profile(profile)
        st.success("Saved \u2705 \u2014 your CVs will now include these details automatically.")

st.divider()

# ---------- Read-only profile snapshot ----------
st.subheader("\U0001F4CB Profile Snapshot (locked)")

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**Full name:** {p['full_name']}")
    st.markdown(f"**Nationality:** {p['nationality']}")
    st.markdown(f"**Education:** {p['education']}")
    st.markdown(f"**Qatar Driving License:** {'\u2705 Yes' if p['qatar_driving_license'] else '\u274C No'}")
    st.markdown(f"**Languages:** {', '.join(p['languages'])}")
with c2:
    st.markdown(f"**Total experience:** {profile['total_experience_years']} years")
    st.markdown(f"**Current salary:** {p['current_salary_qar']:,} QAR/month")

st.subheader("\U0001F454 Experience Timeline")
type_label = {"current": "\U0001F7E2 Current", "primary": "\U0001F535 Primary", "trainee": "\U0001F7E1 Trainee"}
for e in profile["experience"]:
    with st.container(border=True):
        cc1, cc2 = st.columns([3, 1])
        with cc1:
            st.markdown(f"**{e['role']}** \u2014 *{e['company']}*")
            st.caption(f"{e['location']} | {e['from']} \u2192 {e['to']} | Voltage: {e['voltage']}")
            for h in e["highlights"]:
                st.markdown(f"- {h}")
        with cc2:
            st.markdown(f"### {type_label.get(e['type'],'')}")
            st.metric("Years", e["years"])

st.subheader("\U0001F6E0\ufe0f Skills Inventory")
s = profile["skills"]
sc1, sc2 = st.columns(2)
with sc1:
    st.markdown("**Voltage levels:** " + ", ".join(s["voltage_levels"]))
    st.markdown("**Substation types:** " + ", ".join(s["substation_types"]))
    st.markdown("**Software:** " + ", ".join(s["software"]))
with sc2:
    st.markdown("**Certifications:**")
    for c in s["certifications"]:
        st.markdown(f"- {c}")

with st.expander("Full equipment & operations list"):
    st.markdown("**Equipment:**")
    for x in s["equipment"]:
        st.markdown(f"- {x}")
    st.markdown("**Operations:**")
    for x in s["operations"]:
        st.markdown(f"- {x}")
