import numpy as np
import pandas as pd


GENERIC_TERMS = {"services", "solutions", "products", 
                 "manufacturing", "company", "expertise", 
                 "international", "group"}


def adjust_weights_dinamically(row, query, base_weights):
    query_words = set(query.lower().split())
    adjusted = base_weights.copy()

    for field, weight in base_weights.items():
        content = str(row.get(field, "")).lower()
        content_words = set(content.split())
        if field in ["industry", "offerings"] and (query_words & content_words):
            adjusted[field] *= 2.5
        elif len(content) < 15:
            if any(term in content for term in GENERIC_TERMS) or len(content_words) < 2:
                adjusted[field] *= 0.2

        if not content or content == "nan" or content == "none":
            adjusted[field] = 0
        
        total = sum(adjusted.values())
        if total == 0: return base_weights

    return {f: w / total for f, w in adjusted.items()}

# TODO: Adjust this function

WEIGHTS = {
    "semantic": {
        "description": 0.35,
        "offerings": 0.30,
        "industry": 0.10,
        "business": 0.25
    },

    "hybrid": {
        "description": 0.20,
        "offerings": 0.25,
        "industry": 0.30,
        "business": 0.25
    }
}

# The weights should sum up to 1
