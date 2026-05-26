"""Load and persist candidate profile."""
import json
from pathlib import Path

PROFILE_PATH = Path(__file__).parent.parent / "data" / "profile.json"
KEYWORDS_PATH = Path(__file__).parent.parent / "data" / "keywords.json"


def load_profile() -> dict:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile: dict) -> None:
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def load_keywords() -> dict:
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
