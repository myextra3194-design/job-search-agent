"""Page 3 \u2014 CV & Cover Letter Generator"""
import streamlit as st
from utils.profile_loader import load_profile
from utils.cv_generator import CV_TEMPLATES, generate_cv, generate_cover_letter

st.set_page_config(page_title="Generate CV", page_icon="\U0001F4DD", layout="wide")
st.title("\U0001F4DD CV & Cover Letter Generator")
st.caption("All content uses your locked profile only. No inflation. No hallucination.")

profile = load_profile()

tab1, tab2 = st.tabs(["\U0001F4C4 Generate CV", "\u2709\ufe0f Generate Cover Letter"])

# ----------- CV Tab -----------
with tab1:
    st.subheader("Choose a tailored CV version")
    descriptions = {
        "CV_SUBSTATION_OAM": "\U0001F50C **Substation O&M Engineer** \u2014 default. Operations & maintenance focus.",
        "CV_PROTECTION_RELAY": "\u26A1 **Protection & Relay Engineer** \u2014 numerical relay, fault analysis, IEC 61850.",
        "CV_QATAR_UTILITY": "\U0001F1F6\U0001F1E6 **Qatar Utility Specialist** \u2014 plays up KAHRAMAA LOA + 2+ yrs local network.",
        "CV_COMMISSIONING": "\U0001F527 **Commissioning Engineer** \u2014 T&C, FAT/SAT, energization support.",
        "CV_GCC_GENERAL": "\U0001F30D **GCC General Electrical Engineer** \u2014 broad pitch across GCC opportunities.",
    }
    cv_key = st.radio(
        "Pick a focus:",
        list(CV_TEMPLATES.keys()),
        format_func=lambda k: descriptions[k],
    )
    if st.button("\U0001F680 Generate CV", type="primary", use_container_width=True):
        cv_md = generate_cv(cv_key, profile)
        st.session_state["last_cv"] = cv_md
        st.session_state["last_cv_key"] = cv_key

    if "last_cv" in st.session_state:
        st.divider()
        st.subheader(f"Preview \u2014 {st.session_state['last_cv_key']}")
        col_p, col_d = st.columns([3, 1])
        with col_p:
            st.markdown(st.session_state["last_cv"])
        with col_d:
            st.download_button(
                "\u2b07\ufe0f Download as .md",
                st.session_state["last_cv"],
                file_name=f"{st.session_state['last_cv_key']}_Musthafa.md",
                mime="text/markdown",
                use_container_width=True,
            )
            # also offer plain text
            st.download_button(
                "\u2b07\ufe0f Download as .txt",
                st.session_state["last_cv"],
                file_name=f"{st.session_state['last_cv_key']}_Musthafa.txt",
                mime="text/plain",
                use_container_width=True,
            )
            st.info("To convert to PDF/Word: open the .md in Notion, Typora, or paste into Google Docs \u2192 Download as PDF.")

# ----------- Cover Letter Tab -----------
with tab2:
    st.subheader("Tailored Cover Letter")
    cc1, cc2 = st.columns(2)
    company = cc1.text_input("Company name", placeholder="e.g. KAHRAMAA, TAQA, Siemens Energy")
    role = cc2.text_input("Role title", placeholder="e.g. Substation Engineer")
    hook = st.text_area(
        "Optional company hook (1-2 sentences \u2014 why THIS company)",
        placeholder="e.g. Your ongoing 400 kV grid expansion in Lusail directly aligns with my hands-on EHV experience\u2026",
        height=80,
    )
    if st.button("\u270D\ufe0f Generate Cover Letter", type="primary", use_container_width=True):
        if not company or not role:
            st.error("Please enter both company and role.")
        else:
            letter = generate_cover_letter(profile, company, role, hook)
            st.session_state["last_letter"] = letter
            st.session_state["last_letter_meta"] = f"{company}_{role}"

    if "last_letter" in st.session_state:
        st.divider()
        st.subheader("Preview")
        col_p, col_d = st.columns([3, 1])
        with col_p:
            st.markdown(st.session_state["last_letter"])
        with col_d:
            safe_name = st.session_state["last_letter_meta"].replace(" ", "_")
            st.download_button(
                "\u2b07\ufe0f Download .md",
                st.session_state["last_letter"],
                file_name=f"CoverLetter_{safe_name}.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.download_button(
                "\u2b07\ufe0f Download .txt",
                st.session_state["last_letter"],
                file_name=f"CoverLetter_{safe_name}.txt",
                mime="text/plain",
                use_container_width=True,
            )
