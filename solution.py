from utils.data_parsing import df
from hardfiltering.LLM_parser import SearchFilters
from hardfiltering.first_filters import apply_filters
import embedding.transformers as emb

if emb.embeddings_exist():
    all_embeddings = emb.load_all()
else:
    emb.build_and_save(df)
    all_embeddings = emb.load_all()


def search(query: str):
    filters = SearchFilters.from_llm(query)
    print(f"Country: {filters.country}")
    print(f"Complexity: {filters.complexity}")
    print(f"Is public: {filters.is_public}")
    if filters.complexity == "semantic":
        candidates = emb.search(filters.semantic_query, df, all_embeddings, "semantic")

    elif filters.complexity == "structured":
        candidates = apply_filters(df, filters)

    else:
        survivors = apply_filters(df, filters)
        candidates = emb.search(filters.semantic_query, survivors, all_embeddings, "hybrid")

    if "emb_score" in candidates.columns:
        print(candidates[["operational_name", "country", "emb_score"]].head(10))
    else: 
        print(candidates[["operational_name", "country"]].head(10))
    return candidates


if __name__ == "__main__":
    search("A public company that is not from Romania")
    search("Companies that could supply packaging for a cosmetics brand")
    search("Logistic companies that are in Europe")