from utils.data_parsing import df
from types import SimpleNamespace
from hardfiltering.LLM_parser import SearchFilters
from hardfiltering.first_filters import apply_filters
from utils.region_countries import resolve_region
from utils.dynamic_threshold import dynamic_threshold
from tests.evaluate import evaluate_system
from tests.set import SET
import embedding.transformers as emb

if emb.embeddings_exist():
    all_embeddings = emb.load_all()
else:
    emb.build_and_save(df)
    all_embeddings = emb.load_all()


def search(query: str):
    filters = SearchFilters.from_llm(query)
    region_name, countries = resolve_region(query)
    if countries:
        filters.country = countries

    if filters.complexity == "semantic":
        survivors = apply_filters(df, filters, countries) # Putting it here just if the LLM doesn't respond correctly
        candidates = emb.search(filters.semantic_query, survivors, all_embeddings, "semantic")

    elif filters.complexity == "structured":
        candidates = apply_filters(df, filters, countries)

    else: # hybrid
        survivors = apply_filters(df, filters, countries)
        candidates = emb.search(filters.semantic_query, survivors, all_embeddings, "hybrid")

    if "emb_score" in candidates.columns:
        candidates = candidates[candidates["emb_score"] >= 0.30] # This is a pretty good target
        candidates = dynamic_threshold(candidates, min_results=3)
        print(candidates[["operational_name", "country", "description", "target_markets"]].to_string())
    else:
        print(candidates[["operational_name", "country", "description", "target_markets"]].to_string())

    return candidates.head(10) # Top 10 results


if __name__ == "__main__":
    queries = [
        "A public company from Germany"
    ]
    for q in queries:
        search(q)
    
