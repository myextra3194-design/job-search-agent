"""CSV-backed application tracker."""
import csv
from datetime import date
from pathlib import Path
from typing import List, Dict

import pandas as pd

JOBS_CSV = Path(__file__).parent.parent / "data" / "jobs.csv"

COLUMNS = [
    "app_id", "date_added", "date_applied", "company", "role_title",
    "location", "source_platform", "job_url", "match_score",
    "cv_version_used", "status", "recruiter_contacted",
    "follow_up_1_date", "follow_up_2_date", "response_date",
    "response_type", "interview_date", "outcome",
    "salary_quoted_qar", "notes",
]

STATUS_OPTIONS = [
    "Saved", "Applied", "Followed Up", "Phone Screen",
    "Interview", "Offer", "Rejected", "Withdrawn",
]


def load_jobs() -> pd.DataFrame:
    if not JOBS_CSV.exists() or JOBS_CSV.stat().st_size == 0:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(JOBS_CSV, dtype=str).fillna("")
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = ""
    return df[COLUMNS]


def save_jobs(df: pd.DataFrame) -> None:
    df = df.reindex(columns=COLUMNS)
    df.to_csv(JOBS_CSV, index=False)


def add_job(row: Dict) -> None:
    df = load_jobs()
    next_id = (df["app_id"].astype(str)
                 .replace("", "0").astype(int).max() + 1) if len(df) else 1
    row["app_id"] = str(next_id)
    row.setdefault("date_added", date.today().isoformat())
    row.setdefault("status", "Saved")
    full = {c: row.get(c, "") for c in COLUMNS}
    df = pd.concat([df, pd.DataFrame([full])], ignore_index=True)
    save_jobs(df)


def update_status(app_id: str, new_status: str, extra: Dict | None = None) -> None:
    df = load_jobs()
    mask = df["app_id"].astype(str) == str(app_id)
    if mask.any():
        df.loc[mask, "status"] = new_status
        if extra:
            for k, v in extra.items():
                if k in df.columns:
                    df.loc[mask, k] = v
        save_jobs(df)


def delete_job(app_id: str) -> None:
    df = load_jobs()
    df = df[df["app_id"].astype(str) != str(app_id)]
    save_jobs(df)


def stats() -> Dict:
    df = load_jobs()
    total = len(df)
    by_status = df["status"].value_counts().to_dict() if total else {}
    applied = sum(1 for s in df["status"] if s and s != "Saved")
    interviews = by_status.get("Interview", 0) + by_status.get("Phone Screen", 0)
    offers = by_status.get("Offer", 0)
    response_rate = (applied and round(
        (interviews + offers) / applied * 100, 1)) or 0
    return {
        "total_tracked": total,
        "applied": applied,
        "by_status": by_status,
        "interviews": interviews,
        "offers": offers,
        "response_rate_pct": response_rate,
    }
