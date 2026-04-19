import os
from utils.data_parsing import df
from utils.LLM_parser import SearchFilters
from first_filters import apply_filters

def search(query: str):
    filters = SearchFilters.from_llm(query)
    survivors = apply_filters(df, filters)
    print(f"Complexity:  {filters.complexity}")
    print(f"Country:     {filters.country}")
    print(f"Continent:   {filters.continent}")
    print(f"Min emp:     {filters.min_employees}")
    print(f"Max emp:     {filters.max_employees}")
    print(f"Min revenue: {filters.min_revenue}")
    print(f"Max revenue: {filters.max_revenue}")
    print(f"Is public:   {filters.is_public}")
    print(f"Semantic Q:  {filters.semantic_query}")

    print(f"Survivors: {len(survivors)}/{len(df)}")
    print(survivors[["operational_name", "country", "employee_count", "revenue"]].head(5))
    return survivors


if __name__ == "__main__":
    search("Public companies that are in Romania")
    search("A company with more than 1000 employees that is in Europe")
    search("A company that has less than $1000 revenue that is in Asia")

# TODO: Start the second layer of filtering