"""10-point job evaluation matrix.

Scores a job description text against Musthafa's profile.
Returns total score (0-100) and per-criterion breakdown.
"""
from __future__ import annotations
import re
from typing import Tuple, Dict


# ---------- helper text matchers ----------
def _contains_any(text: str, terms) -> bool:
    text_lc = text.lower()
    return any(t.lower() in text_lc for t in terms)


def _extract_years(text: str) -> Tuple[int, int]:
    """Return (min_years, max_years) found in text. (0,0) if none."""
    text_lc = text.lower()
    # patterns: "5-7 years", "5 to 7 years", "minimum 5 years", "at least 7 years"
    range_m = re.search(r"(\d{1,2})\s*[-to]+\s*(\d{1,2})\s*\+?\s*years?", text_lc)
    if range_m:
        return int(range_m.group(1)), int(range_m.group(2))
    min_m = re.search(r"(?:minimum|at\s*least|min\.?)\s*(?:of\s*)?(\d{1,2})\s*\+?\s*years?", text_lc)
    if min_m:
        v = int(min_m.group(1))
        return v, v + 5
    # bare "10+ years"
    plus_m = re.search(r"(\d{1,2})\s*\+\s*years?", text_lc)
    if plus_m:
        v = int(plus_m.group(1))
        return v, v + 5
    any_m = re.search(r"(\d{1,2})\s*years?", text_lc)
    if any_m:
        v = int(any_m.group(1))
        return v, v
    return 0, 0


# ---------- individual scorers (return 0..10) ----------
def score_role_match(text: str) -> Tuple[int, str]:
    exact = ["substation o&m engineer", "substation engineer", "substation technical assistant"]
    related = ["hv engineer", "ehv engineer", "electrical maintenance engineer",
               "protection engineer", "relay engineer", "switchgear engineer",
               "commissioning engineer", "power systems engineer", "field service engineer"]
    partial = ["electrical engineer", "site engineer electrical", "maintenance engineer"]
    if _contains_any(text, exact):
        return 10, "Exact title match"
    if _contains_any(text, related):
        return 7, "Related substation/HV title"
    if _contains_any(text, partial):
        return 4, "Partial: general electrical role"
    return 1, "Unrelated / stretch"


def score_experience_fit(text: str) -> Tuple[int, str]:
    lo, hi = _extract_years(text)
    if lo == 0 and hi == 0:
        return 7, "No years stated \u2014 assume open"
    if 5 <= lo <= 7:
        return 10, f"Asks {lo}-{hi} yrs (perfect for 7 yrs profile)"
    if 5 <= lo <= 8:
        return 8, f"Asks {lo}-{hi} yrs (good fit)"
    if 3 <= lo < 5:
        return 5, f"Asks {lo}-{hi} yrs (slightly junior \u2014 still apply)"
    if 8 <= lo <= 10:
        return 3, f"Asks {lo}+ yrs (stretch, but apply with honest framing)"
    if lo > 10:
        return 0, f"Asks {lo}+ yrs (overreach \u2014 risk skip)"
    return 5, f"Asks ~{lo} yrs"


def score_location(text: str) -> Tuple[int, str]:
    text_lc = text.lower()
    if any(c in text_lc for c in ["qatar", "doha", "al wakrah", "lusail", "dukhan"]):
        return 10, "Qatar (priority 1)"
    if any(c in text_lc for c in ["uae", "dubai", "abu dhabi", "sharjah", "u.a.e", "united arab emirates"]):
        return 9, "UAE (priority 2)"
    if any(c in text_lc for c in ["saudi", "riyadh", "dammam", "neom", "jeddah", "ksa"]):
        return 8, "Saudi Arabia (priority 3)"
    if any(c in text_lc for c in ["oman", "muscat", "kuwait", "bahrain"]):
        return 6, "Oman/Kuwait/Bahrain (priority 4-5)"
    if any(c in text_lc for c in ["india", "kerala", "mumbai", "delhi", "bangalore", "chennai", "gujarat"]):
        return 4, "India (backup)"
    return 2, "Other / unspecified"


def score_employer_type(text: str) -> Tuple[int, str]:
    text_lc = text.lower()
    tier1_utility = ["kahramaa", "dewa", "transco", "addc", "sec", "saudi electricity",
                     "oetc", "qatarenergy", "ashghal"]
    tier1_national = ["qatarenergy", "aramco", "adnoc", "qp", "saudi aramco"]
    tier1_epc_oem = ["siemens", "abb", "hitachi", "ge vernova", "schneider",
                     "larsen", "l&t", "alfanar", "samsung c&t", "hyundai", "alstom"]
    if _contains_any(text, tier1_utility):
        return 10, "Tier-1 utility"
    if _contains_any(text, tier1_national):
        return 9, "National energy company"
    if _contains_any(text, tier1_epc_oem):
        return 8, "Tier-1 EPC / OEM"
    return 6, "Mid-tier / unknown"


def score_technical_alignment(text: str) -> Tuple[int, str]:
    core_skills = ["substation", "transformer", "circuit breaker", "switchgear",
                   "protection", "relay", "scada", "switching", "ptw", "commissioning",
                   "gis", "ais", "ct/vt", "busbar", "c&r"]
    hits = sum(1 for s in core_skills if s in text.lower())
    pct = hits / len(core_skills) * 100
    if pct >= 50:
        return 10, f"{hits}/{len(core_skills)} core skills matched"
    if pct >= 30:
        return 7, f"{hits}/{len(core_skills)} core skills matched"
    if pct >= 15:
        return 4, f"{hits}/{len(core_skills)} core skills matched"
    return 1, f"Only {hits} core skills matched"


def score_voltage(text: str) -> Tuple[int, str]:
    text_lc = text.lower()
    vlist = ["11 kv", "11kv", "33 kv", "33kv", "66 kv", "66kv",
             "110 kv", "110kv", "132 kv", "132kv", "220 kv", "220kv"]
    if any(v in text_lc for v in vlist):
        return 10, "Voltage in 11\u2013220 kV range \u2014 exact match"
    if any(t in text_lc for t in ["hv", "ehv", "high voltage", "extra high voltage", "400 kv", "400kv"]):
        return 7, "HV/EHV mentioned"
    if any(t in text_lc for t in ["lv", "low voltage", "generation"]):
        return 5, "LV/generation focused"
    return 4, "Voltage not specified"


def score_salary(text: str, current_qar: int = 4000) -> Tuple[int, str]:
    # crude: look for any salary mention
    text_lc = text.lower()
    money_m = re.search(r"(\d{1,3}[,\s]?\d{3})\s*(?:qar|aed|sar|usd|qr|dh|riyal)", text_lc)
    if money_m:
        amt = int(money_m.group(1).replace(",", "").replace(" ", ""))
        if amt >= 15000:
            return 10, f"~{amt} \u2014 above market"
        if amt >= 12000:
            return 8, f"~{amt} \u2014 at market"
        if amt >= 8000:
            return 6, f"~{amt} \u2014 slightly below market"
        return 4, f"~{amt} \u2014 low for profile"
    return 7, "Salary not disclosed (assume market)"


def score_growth(text: str) -> Tuple[int, str]:
    text_lc = text.lower()
    if any(t in text_lc for t in ["lead", "senior", "principal", "promotion", "career path", "growth", "development"]):
        return 9, "Growth indicators present"
    if "team leader" in text_lc or "supervise" in text_lc:
        return 7, "Supervisory exposure"
    return 5, "Standard lateral role"


def score_visa(text: str) -> Tuple[int, str]:
    text_lc = text.lower()
    if any(t in text_lc for t in ["qatari national only", "ksa national only", "saudi national",
                                   "emirati only", "uae national", "local only", "citizenship required"]):
        return 2, "Nationality-restricted"
    if any(t in text_lc for t in ["transferable visa", "qid", "qatar residents", "locally available", "noc"]):
        return 10, "Local/transferable visa friendly"
    return 7, "Open to all (sponsor likely)"


def score_application_ease(text: str) -> Tuple[int, str]:
    text_lc = text.lower()
    if "easy apply" in text_lc:
        return 10, "Easy Apply"
    if any(t in text_lc for t in ["email cv", "send your cv", "@"]):
        return 9, "Direct email application"
    if any(t in text_lc for t in ["assessment", "test", "online exam"]):
        return 4, "Multi-step / test required"
    return 7, "Standard portal application"


# ---------- main entry ----------
CRITERIA = [
    ("Role Match", score_role_match),
    ("Experience Fit", score_experience_fit),
    ("Location Priority", score_location),
    ("Employer Type", score_employer_type),
    ("Technical Alignment", score_technical_alignment),
    ("Voltage Level Match", score_voltage),
    ("Salary Attractiveness", score_salary),
    ("Growth Potential", score_growth),
    ("Visa/Legal Compatibility", score_visa),
    ("Application Ease", score_application_ease),
]


def score_job(jd_text: str) -> Dict:
    """Return full evaluation: total score, tier, breakdown."""
    breakdown = []
    total = 0
    for name, fn in CRITERIA:
        s, reason = fn(jd_text)
        breakdown.append({"criterion": name, "score": s, "reason": reason})
        total += s

    if total >= 85:
        tier = "\U0001F7E2 APPLY IMMEDIATELY"
        tier_class = "excellent"
    elif total >= 70:
        tier = "\U0001F7E1 APPLY \u2014 customize CV"
        tier_class = "good"
    elif total >= 55:
        tier = "\U0001F7E0 OPTIONAL \u2014 if time permits"
        tier_class = "optional"
    else:
        tier = "\U0001F534 SKIP \u2014 not worth time"
        tier_class = "skip"

    return {
        "total": total,
        "tier": tier,
        "tier_class": tier_class,
        "breakdown": breakdown,
    }
