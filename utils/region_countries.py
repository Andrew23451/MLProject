from typing import Tuple
from utils.country_codes import REGION_MAP

def resolve_region(query: str) -> Tuple[str, list]:
    q = query.lower()
    for region, countries in REGION_MAP.items():
        if region.lower() in q:
            return region, [c.lower() for c in countries]
    return "", []