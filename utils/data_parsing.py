import json
import ast
import pandas as pd
import uuid
from .country_codes import COUNTRY_CODES, EUROPE, ASIA, AFRICA, NORTH_AMERICA, SOUTH_AMERICA, OCEANIA

CONTINENT_MAP = {}
for code in EUROPE: CONTINENT_MAP[code] = "Europe"
for code in ASIA: CONTINENT_MAP[code] = "Asia"
for code in AFRICA: CONTINENT_MAP[code] = "Africa"
for code in SOUTH_AMERICA: CONTINENT_MAP[code] = "South America"
for code in NORTH_AMERICA: CONTINENT_MAP[code] = "North America"
for code in OCEANIA: CONTINENT_MAP[code] = "Oceania"

def safe_parse(x):
    if x is None:
        return None

    if isinstance(x, (dict, list)):
        return x

    if isinstance(x, str):
        try:
            return json.loads(x)
        except:
            try:
                return ast.literal_eval(x)
            except:
                return None

    return None


def list_to_text(value):
    if not isinstance(value, list):
        return ""

    out = []
    for v in value:
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            for key in ["label", "name", "value"]:
                if key in v and v[key]:
                    out.append(str(v[key]))
                    break

    return " ".join(out)


def get_location_info(address_raw):
    addr = safe_parse(address_raw)
    if not addr:
        return pd.Series(["", "Unknown"])
    
    code = addr.get("country_code", "").lower().strip()
    country_name = COUNTRY_CODES.get(code, code)
    continent_name = CONTINENT_MAP.get(code, "Unknown")
    return pd.Series([country_name, continent_name])



def build_text(row):
    parts = []

    if row.get("operational_name"):
        parts.append(str(row["operational_name"]))

    addr = safe_parse(row.get("address"))
    if addr:
        code = addr.get("country_code", "").lower().strip()
        parts.append(COUNTRY_CODES.get(code, code))
        parts.append(CONTINENT_MAP.get(code, ""))
        parts.append(addr.get("region_name", ""))
        parts.append(addr.get("town", ""))

    naics = safe_parse(row.get("primary_naics"))
    if naics:
        parts.append(naics.get("label", ""))

    if row.get("description"):
        parts.append(row["description"])

    for field in ["core_offerings", "target_markets", "business_model"]:
        parts.append(list_to_text(row.get(field)))

    return " ".join([p for p in parts if p]).lower().strip()



def apply_text_normalization(df):
    df = df.copy()
    df["text"] = df.apply(build_text, axis=1)
    df[["country", "continent"]] = df["address"].apply(get_location_info)

    return df


df = pd.read_json("data/companies.jsonl", lines=True)

df = df.drop(columns=["secondary_naics"], errors="ignore")
df = apply_text_normalization(df)
