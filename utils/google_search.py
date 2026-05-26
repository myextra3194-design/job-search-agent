"""Use Google as a meta-aggregator for jobs across ALL boards.

Strategy: build Google search queries like:
   site:linkedin.com/jobs "substation engineer" qatar
   site:bayt.com "substation engineer" qatar
   site:gulftalent.com ...

This effectively searches every job board through Google's index,
bypassing individual site blocks.

Two modes:
1. PUBLIC URL MODE (always works): generate ready-to-click Google URLs
2. SCRAPE MODE (best effort): pull top results via DuckDuckGo HTML
   (Google blocks scraping; DuckDuckGo is more permissive)
"""
from __future__ import annotations
from typing import List, Dict
from urllib.parse import quote_plus
import time
import re

import requests
from bs4 import BeautifulSoup

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Boards to target via Google site: queries
JOB_SITES = {
    "LinkedIn":      "linkedin.com/jobs",
    "Bayt":          "bayt.com",
    "GulfTalent":    "gulftalent.com",
    "NaukriGulf":    "naukrigulf.com",
    "Naukri":        "naukri.com",
    "Indeed":        "indeed.com",
    "Glassdoor":     "glassdoor.com",
    "Rigzone":       "rigzone.com",
    "Energy Jobline":"energyjobline.com",
    "Monster":       "monstergulf.com",
    "QatarLiving":   "qatarliving.com/jobs",
}


# ---------- URL builders (always work) ----------
def build_google_queries(keywords: List[str], location: str = "Qatar",
                         sites: List[str] | None = None) -> Dict[str, str]:
    """Build one Google search URL per target site."""
    sites = sites or list(JOB_SITES.keys())
    quoted_kw = " ".join(f'"{k}"' if " " in k else k for k in keywords[:3])
    out = {}
    for site_label in sites:
        domain = JOB_SITES.get(site_label)
        if not domain:
            continue
        q = f"site:{domain} {quoted_kw} {location}"
        out[site_label] = f"https://www.google.com/search?q={quote_plus(q)}"
    # Also add a meta "all-boards" query
    sites_or = " OR ".join(f"site:{JOB_SITES[s]}" for s in sites if s in JOB_SITES)
    out["🌐 ALL boards (Google)"] = f"https://www.google.com/search?q={quote_plus(f'({sites_or}) {quoted_kw} {location}')}"
    return out


def build_duckduckgo_query(keywords: List[str], location: str,
                           sites: List[str] | None = None) -> str:
    sites = sites or list(JOB_SITES.keys())
    sites_or = " OR ".join(f"site:{JOB_SITES[s]}" for s in sites if s in JOB_SITES)
    kw = " ".join(f'"{k}"' if " " in k else k for k in keywords[:3])
    return f"https://duckduckgo.com/html/?q={quote_plus(f'({sites_or}) {kw} {location}')}"


# ---------- Scraper (DuckDuckGo HTML — more permissive than Google) ----------
def search_via_duckduckgo(keywords: List[str], location: str = "Qatar",
                          max_results: int = 25,
                          sites: List[str] | None = None) -> List[Dict]:
    """Scrape DuckDuckGo HTML search results."""
    url = build_duckduckgo_query(keywords, location, sites)
    try:
        r = requests.post("https://duckduckgo.com/html/",
                          data={"q": _q_from_url(url)},
                          headers=UA, timeout=10)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception:
        return []

    results = []
    for res in soup.select("div.result, div.web-result")[:max_results]:
        title_el = res.select_one("a.result__a, a.result__url, h2 a")
        snippet_el = res.select_one(".result__snippet, .result__body")
        if not title_el:
            continue
        link = title_el.get("href", "")
        # DuckDuckGo wraps in redirector — extract real URL
        m = re.search(r"uddg=([^&]+)", link)
        if m:
            from urllib.parse import unquote
            link = unquote(m.group(1))
        title = title_el.get_text(" ", strip=True)
        snippet = snippet_el.get_text(" ", strip=True) if snippet_el else ""

        # Identify which board it's from
        source = "Web"
        for label, domain in JOB_SITES.items():
            if domain in link:
                source = label
                break

        results.append({
            "title": title[:160],
            "url": link,
            "snippet": snippet[:400],
            "source": source,
        })
    return results


def _q_from_url(url: str) -> str:
    """Extract q= parameter from search URL."""
    from urllib.parse import urlparse, parse_qs, unquote
    qs = parse_qs(urlparse(url).query)
    if "q" in qs:
        return unquote(qs["q"][0])
    return ""


# ---------- Main entry ----------
def google_meta_search(keywords: List[str], location: str = "Qatar",
                       sites: List[str] | None = None,
                       try_scrape: bool = True) -> Dict:
    """
    Returns:
       {
         'results': [...],         # scraped if possible
         'google_urls': {site: url, ...},   # always clickable
         'duckduckgo_url': str,
       }
    """
    results = []
    if try_scrape:
        try:
            results = search_via_duckduckgo(keywords, location, 30, sites)
        except Exception:
            results = []

    return {
        "results": results,
        "google_urls": build_google_queries(keywords, location, sites),
        "duckduckgo_url": build_duckduckgo_query(keywords, location, sites),
    }
