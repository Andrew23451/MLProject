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

# Use this function to see the percentage of the common companies between a set of tests and the actual output
# The tests consist of some companies that corresponds to the user query, that were selected manually,
# but there are not all of them, so the hit rate will not be 100% (the average will be between 30% and 70%). I used this to see
# where I am situated and the percentages allowed me to make the scores dynamically in order to match he query to the company as
# much as possible. 
