from hardfiltering.LLM_parser import SearchFilters
from utils.country_codes import REGION_MAP
import pandas as pd

def apply_filters(df: pd.DataFrame, f: SearchFilters, region_countries: list = None) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)

    if region_countries:
        mask &= df["country"].str.lower().isin(c.lower() for c in region_countries)
    elif f.country:
        mask &= df["country"].str.lower() == f.country.lower()

    if f.continent:
        mask &= df["continent"].str.lower() == f.continent.lower()

    if f.region:
        region_countries = REGION_MAP.get(f.region, [])
        if region_countries:
            mask &= df["country"].str.lower().isin(region_countries)

    if f.min_employees is not None:
        mask &= (df["employee_count"] >= f.min_employees)

    if f.max_employees is not None:
        mask &= (df["employee_count"] <= f.max_employees)

    if f.min_revenue is not None:
        mask &= (df["revenue"] >= f.min_revenue)

    if f.max_revenue is not None:
        mask &= (df["revenue"] <= f.max_revenue)

    if f.is_public is not None:
        mask &= df["is_public"] == f.is_public

    if f.min_year_founded is not None:
        mask &= (df["year_founded"] >= f.min_year_founded)

    if f.max_year_founded is not None:
        mask &= (df["year_founded"] <= f.max_year_founded)

    survivors = df[mask]
    return survivors
