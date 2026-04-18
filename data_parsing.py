import json
import ast
import pandas as pd
import uuid

df = pd.read_json("data/companies.jsonl", lines=True)


# The database contains a lot of dictionaries and lists
# To avoid working on these types of data structures, 
# I transformed everything into a string

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


def build_text(row):
    parts = []

    if row.get("operational_name"):
        parts.append(str(row["operational_name"]))

    addr = safe_parse(row.get("address"))
    if addr:
        parts.append(addr.get("country_code", ""))
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
    return df


df = df.drop(columns=["secondary_naics"], errors="ignore")
df = apply_text_normalization(df)

df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]