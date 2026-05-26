"""Extract keywords from candidate's CV (PDF / DOCX / structured profile JSON).

Strategy:
- Domain-specific stopwords removed
- Multi-word substation engineering phrases preserved (e.g. "circuit breaker")
- Weighted: technical terms > generic words
"""
from __future__ import annotations
import re
from collections import Counter
from typing import Dict, List, Set
from pathlib import Path
from io import BytesIO

# ---------- Stopwords (generic + CV-specific noise) ----------
STOPWORDS: Set[str] = set("""
a an the and or but if then else of in on at to for with by from as is are was were
be been being have has had do does did will would could should may might must can
this that these those i you he she it we they me him her us them my your his their our
not no nor so very just also too only own same each every all any some such
about into through during before after above below between within without
will would should could may might can must one two three first second next last
year years month months day days time times
work works working worked job jobs role roles position positions experience experiences
responsibility responsibilities skill skills duty duties task tasks
team teams company companies organisation organization business
please kindly thank thanks regards sincerely yours faithfully
include included including required require requires requirement requirements
preferred desirable mandatory necessary
""".split())

# ---------- Domain dictionary: known multi-word substation terms ----------
TECHNICAL_PHRASES = [
    # voltage levels
    "11 kv", "33 kv", "66 kv", "110 kv", "132 kv", "220 kv", "400 kv",
    "11kv", "33kv", "66kv", "110kv", "132kv", "220kv", "400kv",
    # substation types
    "gis substation", "ais substation", "air insulated", "gas insulated",
    "indoor substation", "outdoor substation",
    # equipment
    "power transformer", "distribution transformer", "auxiliary transformer",
    "circuit breaker", "sf6 breaker", "vacuum breaker", "oil breaker",
    "disconnect switch", "isolator", "earth switch",
    "current transformer", "voltage transformer", "potential transformer",
    "lightning arrester", "surge arrester", "capacitor bank",
    "busbar", "cable termination", "control cable",
    # protection
    "protection relay", "numerical relay", "differential relay",
    "distance relay", "overcurrent relay", "earth fault relay",
    "transformer protection", "feeder protection", "busbar protection",
    "line protection", "generator protection", "motor protection",
    "trip circuit supervision", "auto reclose",
    "c&r panel", "control and relay panel", "control relay panel",
    "relay coordination", "relay settings", "secondary injection",
    "primary injection",
    # operations
    "preventive maintenance", "corrective maintenance", "breakdown maintenance",
    "predictive maintenance", "condition monitoring",
    "hv switching", "ehv switching", "switching operation",
    "permit to work", "ptw", "loa", "limit of authority",
    "fault isolation", "fault analysis", "root cause analysis",
    "load shedding", "load management",
    # systems
    "scada", "ems", "dms", "sas", "substation automation",
    "iec 61850", "iec 60255", "modbus", "dnp3", "iec 60870",
    # commissioning / testing
    "site acceptance test", "factory acceptance test", "sat", "fat",
    "insulation resistance", "contact resistance", "tan delta",
    "ratio test", "polarity test", "end to end test", "stability test",
    "testing and commissioning", "t&c", "energization", "energisation",
    # utilities
    "kahramaa", "kseb", "dewa", "transco", "addc", "sec", "oetc",
    "qatarenergy", "saudi aramco", "adnoc", "pgcil", "ntpc",
    # software
    "autocad", "revit mep", "etap", "dialux", "primavera", "ms project",
    "ms office", "excel", "powerpoint",
    # general
    "operations and maintenance", "o&m", "o & m",
    "high voltage", "extra high voltage", "medium voltage", "low voltage",
    "hv", "ehv", "mv", "lv",
    "transmission line", "distribution line", "overhead line",
    "underground cable", "xlpe cable",
    "transmission and distribution", "t&d",
    "preventive and corrective", "commissioning support",
    "qa qc", "quality assurance", "hse", "health safety environment",
    "nebosh", "iosh",
]

# ---------- File parsers ----------
def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber."""
    try:
        import pdfplumber
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            return "\n".join((page.extract_text() or "") for page in pdf.pages)
    except Exception as e:
        return f""

def parse_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    try:
        from docx import Document
        doc = Document(BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""

def parse_uploaded_file(uploaded) -> str:
    """Streamlit UploadedFile -> raw text."""
    if not uploaded:
        return ""
    name = uploaded.name.lower()
    data = uploaded.read()
    if name.endswith(".pdf"):
        return parse_pdf(data)
    if name.endswith(".docx"):
        return parse_docx(data)
    if name.endswith((".txt", ".md")):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    return ""

# ---------- Keyword extraction ----------
def _clean(text: str) -> str:
    """Lowercase, normalise whitespace."""
    return re.sub(r"\s+", " ", text.lower()).strip()

def _extract_phrases(text: str) -> List[str]:
    """Find known technical phrases in text."""
    text_lc = _clean(text)
    found = []
    for phrase in TECHNICAL_PHRASES:
        if phrase in text_lc:
            found.append(phrase)
    return found

def _extract_single_words(text: str, min_len: int = 3) -> List[str]:
    """Extract single-word tokens, excluding stopwords."""
    tokens = re.findall(r"[a-zA-Z][a-zA-Z&\-/]+", text.lower())
    return [t for t in tokens
            if len(t) >= min_len and t not in STOPWORDS]

def extract_keywords_from_text(text: str, top_n: int = 50) -> Dict:
    """
    Return weighted keyword dict:
      {
        'technical_phrases': [(phrase, count), ...],   # high weight
        'single_words': [(word, count), ...],           # low weight
        'all_keywords': set of strings,
        'raw_text_length': int
      }
    """
    if not text or len(text.strip()) < 20:
        return {
            "technical_phrases": [], "single_words": [],
            "all_keywords": set(), "raw_text_length": 0,
        }
    phrases = _extract_phrases(text)
    phrase_counts = Counter(phrases)

    # Remove phrase-words from single-word extraction
    text_for_singles = text.lower()
    for ph in set(phrases):
        text_for_singles = text_for_singles.replace(ph, " ")

    singles = _extract_single_words(text_for_singles)
    single_counts = Counter(singles).most_common(top_n)

    all_kw = set(phrase_counts.keys()) | set(w for w, _ in single_counts)

    return {
        "technical_phrases": phrase_counts.most_common(),
        "single_words": single_counts,
        "all_keywords": all_kw,
        "raw_text_length": len(text),
    }


def extract_keywords_from_profile(profile: dict) -> Dict:
    """Build a 'pseudo-CV' from the profile.json and extract."""
    parts = []
    p = profile.get("personal", {})
    parts.append(p.get("education", ""))
    parts.extend(p.get("languages", []))

    for exp in profile.get("experience", []):
        parts.append(exp.get("role", ""))
        parts.append(exp.get("company", ""))
        parts.append(exp.get("voltage", ""))
        parts.extend(exp.get("highlights", []))

    s = profile.get("skills", {})
    for key in ["voltage_levels", "substation_types", "equipment",
                "operations", "software", "certifications"]:
        parts.extend(s.get(key, []))

    text = " ".join(str(x) for x in parts)
    return extract_keywords_from_text(text)


def merge_keywords(*keyword_dicts) -> Dict:
    """Combine multiple keyword dicts (e.g. profile + uploaded CV)."""
    all_phrases = Counter()
    all_singles = Counter()
    all_kw: Set[str] = set()
    total_len = 0
    for kd in keyword_dicts:
        if not kd:
            continue
        for w, c in kd.get("technical_phrases", []):
            all_phrases[w] += c
        for w, c in kd.get("single_words", []):
            all_singles[w] += c
        all_kw |= kd.get("all_keywords", set())
        total_len += kd.get("raw_text_length", 0)
    return {
        "technical_phrases": all_phrases.most_common(),
        "single_words": all_singles.most_common(50),
        "all_keywords": all_kw,
        "raw_text_length": total_len,
    }
