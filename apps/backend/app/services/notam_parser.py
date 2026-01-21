import re
from typing import Any, Dict


def parse_notam_text(raw_text: str) -> Dict[str, Any]:
    airport_match = re.search(r"A\)\s*([A-Z0-9]{4})", raw_text)
    runway_match = re.search(r"RWY\s*([0-9]{2}[A-Z]?/[0-9]{2}[A-Z]?|[0-9]{2}[A-Z]?)", raw_text)
    status = "unknown"
    if re.search(r"\b(CLOSED|CLSD)\b", raw_text, re.IGNORECASE):
        status = "closed"
    elif re.search(r"\b(OPEN|OPN)\b", raw_text, re.IGNORECASE):
        status = "open"

    return {
        "airport": airport_match.group(1) if airport_match else None,
        "runway": runway_match.group(1) if runway_match else None,
        "status": status,
        "summary": raw_text[:160].strip(),
    }
