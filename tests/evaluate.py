def evaluate_system(engine, golden_set):
    report = []
    
    for query, expected_companies in golden_set.items():
        results = engine.search(query)
        retrieved_names = [res.name for res in results]
        
        hits = set(expected_companies).intersection(set(retrieved_names))
        hit_rate = len(hits) / len(expected_companies)
        
        report.append({
            "query": query,
            "hit_rate": f"{hit_rate:.2%}",
            "missing": set(expected_companies) - set(retrieved_names)
        })
        
    return report