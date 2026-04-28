import numpy as np
import pandas as pd

def dynamic_threshold(candidates: pd.DataFrame, min_results: int = 3) -> pd.DataFrame:
    if "emb_score" not in candidates or len(candidates) < 2:
        return candidates

    scores = candidates["emb_score"].values
    diffs = np.diff(scores)

    avg_drop = np.abs(diffs).mean()
    cliff_threshold = 2.0 * avg_drop

    cliff_index = None
    for i, diff in enumerate(diffs):
        if abs(diff) > cliff_threshold and i >= min_results - 1:
            cliff_index = i + 1
            break
    
    if cliff_index is not None:
        return candidates.iloc[:cliff_index]
    
    return candidates
    

