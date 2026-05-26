"""Generate tailored CV markdown + plain text for each focus area."""
from typing import Dict


def _header(profile: dict, subtitle: str) -> str:
    p = profile["personal"]
    contacts = []
    if p.get("email"):
        contacts.append(f"\u2709\ufe0f {p['email']}")
    if p.get("phone"):
        contacts.append(f"\U0001F4DE {p['phone']}")
    if p.get("linkedin"):
        contacts.append(f"\U0001F517 {p['linkedin']}")
    contacts.append(f"\U0001F4CD {p['location']}")
    if p.get("qatar_driving_license"):
        contacts.append("Qatar Driving License")
    return f"""# {p['full_name']}
**{subtitle}**

{" | ".join(contacts)}

---
"""


def _experience_block(profile: dict) -> str:
    lines = ["## PROFESSIONAL EXPERIENCE\n"]
    type_order = {"current": 0, "primary": 1, "trainee": 2}
    exps = sorted(profile["experience"], key=lambda e: type_order.get(e["type"], 9))
    for e in exps:
        label = " *(Trainee \u2014 concurrent)*" if e["type"] == "trainee" else ""
        lines.append(f"### {e['role']}{label}")
        lines.append(f"**{e['company']}** \u2014 {e['location']} | *{e['from']} \u2013 {e['to']}*")
        lines.append(f"Voltage: **{e['voltage']}**\n")
        for h in e["highlights"]:
            lines.append(f"- {h}")
        lines.append("")
    return "\n".join(lines)


def _footer(profile: dict) -> str:
    s = profile["skills"]
    return f"""

## EDUCATION
{profile['personal']['education']}

## CERTIFICATIONS
- {chr(10).join("- " + c for c in s['certifications']).lstrip("- ")}

## SOFTWARE
{" \u2022 ".join(s['software'])}

## LANGUAGES
{" \u2022 ".join(profile['personal']['languages'])}
"""


# -------- 5 CV templates --------
def cv_substation_oam(profile: dict) -> str:
    s = profile["skills"]
    out = _header(profile, "Substation O&M Engineer | HV/EHV | 11 kV \u2013 220 kV | GIS & AIS")
    out += f"""## PROFESSIONAL SUMMARY
Electrical Engineer with **{profile['total_experience_years']} years of hands-on substation Operations & Maintenance** experience across {", ".join(s['voltage_levels'])} GIS and AIS substations. Currently supporting KAHRAMAA transmission network in Qatar under KEIC contract \u2014 performing HV switching, preventive & corrective maintenance, SCADA monitoring, and fault isolation under Permit-to-Work discipline. Authorized LOA holder. Seeking a substation O&M / HV engineering role with a leading GCC utility, OEM, or EPC contractor.

## CORE COMPETENCIES
- **Voltage Levels:** {", ".join(s['voltage_levels'])}
- **Substation Types:** {", ".join(s['substation_types'])}
- **Equipment:** {"; ".join(s['equipment'][:5])}
- **Operations:** {"; ".join(s['operations'])}

"""
    out += _experience_block(profile)
    out += _footer(profile)
    return out


def cv_protection_relay(profile: dict) -> str:
    out = _header(profile, "Protection & Relay Engineer | HV Substations | Numerical Relays")
    out += f"""## PROFESSIONAL SUMMARY
Electrical Engineer with **{profile['total_experience_years']} years of substation experience** including focused training in protection & relay engineering at KSEB Relay Subdivision and live exposure to numerical protection systems on 11 kV\u2013220 kV networks in Qatar. Hands-on with overcurrent, differential, and distance protection schemes; experienced in relay flag analysis, fault investigation, and protection system testing. Seeking a Protection & Relay Engineer role with a utility, EPC contractor, or OEM.

## CORE COMPETENCIES
- Numerical Protection Relays \u2014 Overcurrent (50/51), Differential (87), Distance (21)
- Protection schemes: Transformer, Busbar, Feeder, Line
- Relay testing & coordination, secondary injection
- Fault analysis & root-cause investigation
- C&R Panel operation, IEC 60255 / IEC 61850 awareness
- SCADA monitoring, HV switching (LOA \u2014 KAHRAMAA)

"""
    out += _experience_block(profile)
    out += _footer(profile)
    return out


def cv_qatar_utility(profile: dict) -> str:
    out = _header(profile, "Substation Engineer \u2014 Qatar Utility Experience | KAHRAMAA Network | LOA Authorized")
    out += f"""## PROFESSIONAL SUMMARY
Electrical Engineer with **{profile['total_experience_years']} years of substation experience and 2+ years live operational service on the KAHRAMAA transmission network** in Qatar (under KEIC contract). Deep familiarity with KAHRAMAA standards, switching protocols, PTW discipline, and Qatar HSE requirements. **Authorized LOA holder** for HV switching across 11 kV\u2013220 kV GIS and AIS substations. Qatar driving license holder, locally available.

## QATAR-SPECIFIC HIGHLIGHTS
- \u2705 2+ years live KAHRAMAA network experience (via KEIC)
- \u2705 LOA holder \u2014 authorized for HV switching under KAHRAMAA system
- \u2705 Familiar with KAHRAMAA substation standards & PTW protocols
- \u2705 Qatar Driving License \u2014 full mobility across sites
- \u2705 Basic Arabic \u2014 effective coordination with bilingual teams

"""
    out += _experience_block(profile)
    out += _footer(profile)
    return out


def cv_commissioning(profile: dict) -> str:
    out = _header(profile, "Commissioning Support Engineer \u2014 HV/EHV Substations | 11 kV \u2013 220 kV")
    out += f"""## PROFESSIONAL SUMMARY
Electrical Engineer with **{profile['total_experience_years']} years of substation experience**, including hands-on commissioning support of new bays, equipment extensions, and protection systems on the KAHRAMAA 11 kV\u2013220 kV network. Combines operations discipline (LOA-authorized switching) with practical testing & commissioning exposure \u2014 uniquely positioned to bridge installation, energization, and handover-to-operations phases. Seeking a Commissioning Engineer role with an EPC contractor, OEM, or utility expansion program.

## COMMISSIONING-RELEVANT EXPERIENCE
- Pre-energization checks: CT/VT ratio & polarity, insulation, contact resistance
- Secondary injection testing of protection relays
- Functional testing of trip circuits, interlocks, control schemes
- SCADA point verification
- Energization & load testing, documentation, snag-lists, handover protocols

"""
    out += _experience_block(profile)
    out += _footer(profile)
    return out


def cv_gcc_general(profile: dict) -> str:
    s = profile["skills"]
    out = _header(profile, "Electrical Engineer | Substation O&M | HV/EHV | GCC Experience")
    out += f"""## PROFESSIONAL SUMMARY
Results-driven Electrical Engineer with **{profile['total_experience_years']} years of substation Operations & Maintenance experience** across two national utilities \u2014 KAHRAMAA (Qatar, via KEIC) and KSEB (India). Skilled across {", ".join(s['voltage_levels'])} GIS and AIS substations. Authorized LOA holder. Open to opportunities across Qatar, UAE, KSA, and Oman.

## KEY STRENGTHS
- {profile['total_experience_years']} years substation O&M (110 kV India + 11\u2013220 kV Qatar)
- KAHRAMAA LOA Switching Authorization
- GIS and AIS substation experience
- Power transformer, switchgear, protection relay maintenance
- SCADA monitoring, PTW practitioner
- Multilingual: English, Hindi, Malayalam, basic Arabic
- Qatar Driving License \u2014 immediate GCC mobility

"""
    out += _experience_block(profile)
    out += _footer(profile)
    return out


CV_TEMPLATES = {
    "CV_SUBSTATION_OAM": cv_substation_oam,
    "CV_PROTECTION_RELAY": cv_protection_relay,
    "CV_QATAR_UTILITY": cv_qatar_utility,
    "CV_COMMISSIONING": cv_commissioning,
    "CV_GCC_GENERAL": cv_gcc_general,
}


def generate_cv(template_key: str, profile: dict) -> str:
    fn = CV_TEMPLATES.get(template_key)
    if not fn:
        raise ValueError(f"Unknown CV template: {template_key}")
    return fn(profile)


# ---------- Cover letter ----------
def generate_cover_letter(profile: dict, company: str, role: str,
                          company_hook: str = "") -> str:
    p = profile["personal"]
    hook = company_hook or f"I am drawn to {company}'s reputation in the HV/EHV substation space and your active projects in the region."
    return f"""**{p['full_name']}**
{p['location']} | {p.get('email','[email]')} | {p.get('phone','[phone]')}

**Hiring Manager**
**{company}**

**Re: Application for {role}**

Dear Hiring Manager,

I am writing to express my interest in the **{role}** position at **{company}**. With **{profile['total_experience_years']} years of dedicated substation Operations & Maintenance experience** across the KAHRAMAA transmission network in Qatar (via KEIC) and Kerala State Electricity Board (KSEB) in India, I am confident I can contribute immediately to your team.

In my current role with KEIC supporting KAHRAMAA, I operate and maintain **11 kV to 220 kV GIS and AIS substations**, performing HV switching under PTW as an **authorized LOA holder**, monitoring via SCADA, and supporting commissioning of new bays. Previously at KSEB, I independently managed a 110 kV substation \u2014 overseeing transformer health, protection relay performance, and breakdown response.

{hook}

What I bring to your team:
- **LOA-authorized** HV switching experience on a Tier-1 GCC utility
- Hands-on with power transformers, SF6 circuit breakers, protection relays, CTs/VTs
- 2+ years of live KAHRAMAA standards experience \u2014 quick ramp-up in any GCC utility environment
- Qatar Driving License + locally available
- Multilingual (English, Hindi, Arabic basic) for effective regional collaboration

I would welcome the opportunity to discuss how my hands-on substation O&M background can contribute to {company}'s objectives. My CV is attached for your review, and I am available for interview at your convenience.

Thank you for your consideration.

Sincerely,
**{p['full_name']}**
"""
