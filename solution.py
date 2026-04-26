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
    print(f"Complexity: {filters.complexity}")
    print(f"Country: {filters.country}")
    print(f"Continent: {filters.continent}")
    print(f"Is public: {filters.is_public}")

    if filters.complexity == "semantic":
        candidates = emb.search(filters.semantic_query, df, all_embeddings, "semantic")

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
        "Logistic companies in Romania",
        "Public software companies with more than 1,000 employees",
        "Food and beverage manufacturers in France",
        "Companies that could supply packaging for a cosmetics brand",
        "Construction companies in the United States with revenue over $50 million",
        "Pharmaceutical companies in Switzerland",
        "B2B SaaS companies providing HR solutions in Europe",
        "Clean energy startups founded after 2018 with fewer than 200 employees",
        "Fast-growing fintech companies competing with traditional banks in Europe",
        "E-commerce companies using Shopify or similar platforms",
        "Renewable energy equipment manufacturers in Scandinavia",
        "Companies that manufacture or supply critical components for electric vehicle battery production",
    ]

    for q in queries:
        print(f"\n{'='*60}")
        print(f"Query: {q}")
        search(q)
