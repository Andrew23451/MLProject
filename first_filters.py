from LLM_parser import SearchFilters
import pandas as pd

def apply_filters(df: pd.DataFrame, f: SearchFilters) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)

    if f.country:
        mask &= df["text"].str.contains(f.country.lower(), na=False)

    if f.continent:
        mask &= df["text"].str.contains(f.continent.lower(), na=False)

    if f.min_employees is not None:
        mask &= (df["employee_count"] >= f.min_employees) | df["employee_count"].isna()

    if f.max_employees is not None:
        mask &= (df["employee_count"] <= f.max_employees) | df["employee_count"].isna()

    if f.min_revenue is not None:
        mask &= (df["revenue"] >= f.min_revenue) | df["revenue"].isna()

    if f.max_revenue is not None:
        mask &= (df["revenue"] <= f.max_revenue) | df["revenue"].isna()

    if f.is_public is not None:
        mask &= df["is_public"] == f.is_public

    if f.min_year_founded is not None:
        mask &= (df["year_founded"] >= f.min_year_founded) | df["year_founded"].isna()

    if f.max_year_founded is not None:
        mask &= (df["year_founded"] <= f.max_year_founded) | df["year_founded"].isna()

    survivors = df[mask]
    return survivors