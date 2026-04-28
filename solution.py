from utils.data_parsing import df
from hardfiltering.LLM_parser import SearchFilters
from hardfiltering.first_filters import apply_filters
from utils.region_countries import resolve_region
import embedding.transformers as emb
import time

if emb.embeddings_exist():
    all_embeddings = emb.load_all()
else:
    emb.build_and_save(df)
    all_embeddings = emb.load_all()


def search(query: str):
    filters = SearchFilters.from_llm(query)
    region_name, _ = resolve_region(query)
    if region_name:
        filters.region = region_name
    
    print(f"Complexity: {filters.complexity}")
    print(f"Country: {filters.country}")
    print(f"Continent: {filters.continent}")

    if filters.complexity == "semantic":
        survivors = apply_filters(df, filters) # Putting it here just if the LLM doesn't respond correctly
        candidates = emb.search(filters.semantic_query, survivors, all_embeddings, "semantic")

    elif filters.complexity == "structured":
        candidates = apply_filters(df, filters)

    else:  # hybrid
        survivors = apply_filters(df, filters)
        candidates = emb.search(filters.semantic_query, survivors, all_embeddings, "hybrid")

    if "emb_score" in candidates.columns:
        print(candidates[["operational_name", "country", "emb_score"]].head(10))
    else:
        print(candidates[["operational_name", "country"]].head(10))

    return candidates


if __name__ == "__main__":
    queries = [
        "A public company from Scandinavia"
    ]

    for q in queries:
        print(f"Query: {q}")
        search(q)
        time.sleep(4)
