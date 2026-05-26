"""Score a job posting against the candidate's CV keywords.

Returns a % match (0-100) with breakdown of which keywords matched.
"""
from __future__ import annotations
import re
from typing import Dict, List


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def score_job_vs_keywords(
    job_text: str,
    cv_keywords: Dict,
    technical_weight: float = 3.0,
    single_weight: float = 1.0,
) -> Dict:
    """
    Compare job posting text against the candidate's extracted CV keywords.

    Args:
        job_text: full text of job (title + company + location + description)
        cv_keywords: output of extract_keywords_from_text/profile
        technical_weight: how much more a technical phrase match counts
        single_weight: weight per single-word match

    Returns:
        {
          'match_pct': 0-100,
          'matched_technical': [phrases],
          'matched_singles': [words],
          'missing_critical': [top phrases NOT found in job],
          'score_raw': float,
          'score_max': float,
        }
    """
    job_lc = _clean(job_text)
    if not job_lc or not cv_keywords:
        return {
            "match_pct": 0, "matched_technical": [], "matched_singles": [],
            "missing_critical": [], "score_raw": 0, "score_max": 0,
        }

    tech_phrases = cv_keywords.get("technical_phrases", [])
    single_words = cv_keywords.get("single_words", [])

    matched_tech: List[str] = []
    matched_singles: List[str] = []
    score_raw = 0.0
    score_max = 0.0

    # Technical phrases (capped count = 1 per phrase to avoid over-rewarding repeats)
    for phrase, count_in_cv in tech_phrases:
        weight = technical_weight * min(count_in_cv, 3)
        score_max += weight
        if phrase in job_lc:
            matched_tech.append(phrase)
            score_raw += weight

    # Single words (cap top-30 to keep matching focused)
    for word, count_in_cv in single_words[:30]:
        weight = single_weight * min(count_in_cv, 3)
        score_max += weight
        # Use word-boundary regex for cleaner single-word matching
        if re.search(rf"\b{re.escape(word)}\b", job_lc):
            matched_singles.append(word)
            score_raw += weight

    pct = round((score_raw / score_max * 100), 1) if score_max > 0 else 0

    # Identify critical missing phrases (top 5 technical phrases not in job)
    missing = [ph for ph, _ in tech_phrases[:10] if ph not in job_lc][:5]

    return {
        "match_pct": pct,
        "matched_technical": matched_tech,
        "matched_singles": matched_singles,
        "missing_critical": missing,
        "score_raw": round(score_raw, 1),
        "score_max": round(score_max, 1),
    }


def tier_from_pct(pct: float) -> Dict:
    """Map % to tier badge."""
    if pct >= 70:
        return {"label": "🟢 EXCELLENT MATCH", "color": "#2ea043", "class": "excellent"}
    if pct >= 50:
        return {"label": "🟡 GOOD MATCH", "color": "#d29922", "class": "good"}
    if pct >= 30:
        return {"label": "🟠 PARTIAL MATCH", "color": "#db6d28", "class": "partial"}
    return {"label": "🔴 LOW MATCH", "color": "#f85149", "class": "low"}
