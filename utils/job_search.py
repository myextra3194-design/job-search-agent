"""Live job board search.

Strategy: build search-URLs to popular job boards. Some boards
allow lightweight scraping of their public listing pages; others
require JS rendering. To be robust *and* legal:

1. We construct ready-to-click search URLs for each platform
   (so the user can open one-click search in browser).
2. For boards that expose simple HTML, we attempt a polite scrape
   with proper User-Agent + 5s timeout. If a board changes layout
   or blocks us, we gracefully fall back to "click-through" only.

Boards covered:
- Bayt        (public HTML, scrapable)
- GulfTalent  (public HTML, scrapable)
- NaukriGulf  (public HTML, scrapable)
- LinkedIn    (URL only \u2014 needs login to scrape)
- Indeed Qatar (URL only \u2014 anti-bot)
- Glassdoor   (URL only \u2014 anti-bot)

Each scraped result returns:
{title, company, location, url, snippet, source}
"""
from __future__ import annotations
import time
from typing import List, Dict
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

UA = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}
TIMEOUT = 8


# ---------------- URL builders (always work) ----------------
def build_search_urls(keyword: str, location: str) -> Dict[str, str]:
    k = quote_plus(keyword)
    l = quote_plus(location)
    return {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={k}&location={l}",
        "Bayt": f"https://www.bayt.com/en/{l.lower()}/jobs/{k.lower().replace('+','-')}-jobs/",
        "GulfTalent": f"https://www.gulftalent.com/jobs/search?keywords={k}&location={l}",
        "NaukriGulf": f"https://www.naukrigulf.com/{k.lower().replace('+','-')}-jobs-in-{l.lower()}",
        "Indeed Qatar": f"https://qa.indeed.com/jobs?q={k}&l={l}",
        "Glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={k}&locT=N&locKeyword={l}",
        "Monster Gulf": f"https://www.monstergulf.com/srp/results?query={k}&searchId=&where={l}",
        "Rigzone": f"https://www.rigzone.com/oil/jobs/search/?sk={k}&loc={l}",
    }


# ---------------- Scrapers ----------------
def _safe_get(url: str) -> str | None:
    try:
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        if r.status_code == 200 and r.text:
            return r.text
    except Exception:
        return None
    return None


def scrape_bayt(keyword: str, location: str = "qatar", max_results: int = 10) -> List[Dict]:
    """Bayt has fairly clean HTML for public listing pages."""
    url = f"https://www.bayt.com/en/{location.lower()}/jobs/{keyword.lower().replace(' ', '-')}-jobs/"
    html = _safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    results = []
    for card in soup.select("li[data-job-id], li.has-pointer-d")[:max_results]:
        a = card.find("a", href=True)
        if not a:
            continue
        title = (a.get_text(strip=True) or "")[:140]
        link = a["href"]
        if link.startswith("/"):
            link = "https://www.bayt.com" + link
        comp = card.select_one("div.t-default, .t-nowrap, b")
        loc = card.select_one(".t-mute, span.t-mute")
        snippet_el = card.select_one("div.jb-descr, p.m0")
        results.append({
            "title": title or "Listing",
            "company": comp.get_text(strip=True) if comp else "—",
            "location": loc.get_text(strip=True) if loc else location.title(),
            "url": link,
            "snippet": (snippet_el.get_text(" ", strip=True)[:300] if snippet_el else "")[:300],
            "source": "Bayt",
        })
    return results


def scrape_gulftalent(keyword: str, location: str = "qatar", max_results: int = 10) -> List[Dict]:
    url = f"https://www.gulftalent.com/{location.lower()}/jobs/title/{keyword.lower().replace(' ', '-')}"
    html = _safe_get(url)
    if not html:
        # fall back to generic search
        url = f"https://www.gulftalent.com/jobs/search?keywords={quote_plus(keyword)}&location={quote_plus(location)}"
        html = _safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    results = []
    # GulfTalent uses div.job-listing or li.listing
    for card in soup.select("div.job, div.listing, li.job-result")[:max_results]:
        a = card.find("a", href=True)
        if not a:
            continue
        title = a.get_text(strip=True)[:140]
        link = a["href"]
        if link.startswith("/"):
            link = "https://www.gulftalent.com" + link
        comp = card.select_one(".company, .employer")
        loc = card.select_one(".location, .loc")
        results.append({
            "title": title or "Listing",
            "company": comp.get_text(strip=True) if comp else "—",
            "location": loc.get_text(strip=True) if loc else location.title(),
            "url": link,
            "snippet": card.get_text(" ", strip=True)[:300],
            "source": "GulfTalent",
        })
    return results


def scrape_naukrigulf(keyword: str, location: str = "qatar", max_results: int = 10) -> List[Dict]:
    url = f"https://www.naukrigulf.com/{keyword.lower().replace(' ', '-')}-jobs-in-{location.lower()}"
    html = _safe_get(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "lxml")
    results = []
    for card in soup.select("div.ng-box.srp-tuple, article.job-tuple")[:max_results]:
        a = card.find("a", href=True)
        if not a:
            continue
        title = a.get_text(strip=True)[:140]
        link = a["href"]
        if link.startswith("/"):
            link = "https://www.naukrigulf.com" + link
        comp = card.select_one(".info-org, .comp-name, .company")
        loc = card.select_one(".loc, .location")
        results.append({
            "title": title or "Listing",
            "company": comp.get_text(strip=True) if comp else "—",
            "location": loc.get_text(strip=True) if loc else location.title(),
            "url": link,
            "snippet": card.get_text(" ", strip=True)[:300],
            "source": "NaukriGulf",
        })
    return results


# ---------------- Orchestrator ----------------
def search_all(keyword: str, location: str = "Qatar",
               sources: List[str] | None = None,
               per_source_max: int = 8) -> Dict:
    """Run all enabled scrapers + return click-through URLs for the rest."""
    sources = sources or ["Bayt", "GulfTalent", "NaukriGulf"]
    scraped: List[Dict] = []
    errors: Dict[str, str] = {}

    if "Bayt" in sources:
        try:
            scraped.extend(scrape_bayt(keyword, location.lower(), per_source_max))
        except Exception as e:
            errors["Bayt"] = str(e)
        time.sleep(0.3)
    if "GulfTalent" in sources:
        try:
            scraped.extend(scrape_gulftalent(keyword, location.lower(), per_source_max))
        except Exception as e:
            errors["GulfTalent"] = str(e)
        time.sleep(0.3)
    if "NaukriGulf" in sources:
        try:
            scraped.extend(scrape_naukrigulf(keyword, location.lower(), per_source_max))
        except Exception as e:
            errors["NaukriGulf"] = str(e)

    return {
        "results": scraped,
        "search_urls": build_search_urls(keyword, location),
        "errors": errors,
    }
