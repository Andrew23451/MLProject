from typing import Tuple
from utils.country_codes import REGION_MAP

def resolve_region(query: str) -> Tuple[str, list]:
    q = query.lower()
    for region, countries in REGION_MAP.items():
        if any(word.startswith(region[:5]) for word in q.split()):
            return region, countries
    return "", []