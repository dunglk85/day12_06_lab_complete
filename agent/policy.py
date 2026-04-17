from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TripIntent:
    origin: str
    destination: str



def should_force_parallel_search(last_human_message: Optional[str]) -> bool:
    if not last_human_message:
        return False
    return "budget" in last_human_message.lower()



def extract_trip_intent(last_human_message: str) -> TripIntent:
    """Extract origin/destination from user text with safe defaults."""
    origin_match = re.search(r"(?:ở|từ)\s+([^,]+)", last_human_message, re.IGNORECASE)
    dest_match = re.search(r"(?:đi|đến)\s+([^,\d]+)", last_human_message, re.IGNORECASE)

    origin = origin_match.group(1).strip() if origin_match else "Hà Nội"
    destination = dest_match.group(1).strip() if dest_match else "Phú Quốc"

    return TripIntent(origin=origin, destination=destination)