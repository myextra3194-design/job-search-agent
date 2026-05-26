"""Smart Apply Assistant — pre-fill application materials, open posting in new tab.

This is the RECRUITER-FRIENDLY approach. We do NOT auto-submit forms
(which would violate ToS and get accounts banned). Instead we:

1. Detect application email if present in the JD
2. Pre-fill mailto: link with subject + body + CV reference
3. Provide copy-to-clipboard buttons for CV / cover letter
4. Auto-log the application to tracker on click
"""
from __future__ import annotations
import re
from typing import Dict, Optional
from urllib.parse import quote


EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)


def extract_emails(text: str) -> list[str]:
    """Find all email addresses in a job posting."""
    if not text:
        return []
    found = EMAIL_RE.findall(text)
    # filter common false-positives (placeholders, footer noise)
    blacklist = ("example.com", "domain.com", "yourcompany.com",
                 "noreply", "no-reply", "donotreply")
    return [e for e in set(found) if not any(b in e.lower() for b in blacklist)]


def build_mailto_link(
    to_email: str,
    company: str,
    role: str,
    candidate_name: str = "Muhammed Musthafa K",
    summary_line: str = "7 years substation O&M experience, LOA-authorized KAHRAMAA",
) -> str:
    """Build a mailto: link that opens user's email client pre-filled."""
    subject = f"Application — {role} — {candidate_name} ({summary_line.split(',')[0]})"
    body = f"""Dear Hiring Manager,

Please find attached my CV in response to your posting for the {role} position at {company}.

Quick fit summary:
- {summary_line}
- 11 kV to 220 kV GIS & AIS substations
- Currently based in Al Wakrah, Qatar — Qatar Driving License — locally available

I would welcome the opportunity to discuss how my background aligns with your requirements.

Best regards,
{candidate_name}
"""
    return f"mailto:{to_email}?subject={quote(subject)}&body={quote(body)}"


def build_apply_kit(
    job_title: str,
    company: str,
    job_url: str,
    job_description: str,
    candidate_name: str = "Muhammed Musthafa K",
) -> Dict:
    """
    Build everything needed to apply to a job in one click:
      - apply_url: the job posting itself (always)
      - mailto_url: if direct email found in JD
      - emails_found: list of contact emails
      - email_subject: pre-filled subject
      - email_body: pre-filled body
      - application_log: dict to save to tracker
    """
    emails = extract_emails(job_description)
    primary_email = emails[0] if emails else None

    summary_line = "7 yrs Substation O&M — KAHRAMAA LOA-authorized — Qatar-based"

    mailto = None
    email_subject = f"Application — {job_title} — {candidate_name}"
    email_body = f"""Dear Hiring Manager,

Please find attached my CV in response to your posting for the {job_title} position at {company}.

Quick fit summary:
- {summary_line}
- 11 kV to 220 kV GIS & AIS substations
- Currently based in Al Wakrah, Qatar — Qatar Driving License — locally available

I would welcome the opportunity to discuss how my background aligns with your requirements.

Best regards,
{candidate_name}
+974 [phone] | [email]
"""

    if primary_email:
        mailto = build_mailto_link(primary_email, company, job_title,
                                    candidate_name, summary_line)

    return {
        "apply_url": job_url,
        "emails_found": emails,
        "primary_email": primary_email,
        "mailto_url": mailto,
        "email_subject": email_subject,
        "email_body": email_body,
    }
