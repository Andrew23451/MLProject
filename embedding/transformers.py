from sentence_transformers import SentenceTransformer
from utils.data_parsing import safe_parse
from utils.weights import WEIGHTS
from utils.paths import PATHS
from utils.weights import adjust_weights_dinamically
import numpy as np
import torch
import os
import pandas as pd
from dotenv import load_dotenv

torch.manual_seed(42)
np.random.seed(42)
torch.use_deterministic_algorithms(False)
os.environ['TRANSFORMERS_OFFLINE'] = '1'

load_dotenv()


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def extract_description(row) -> str:
    return (row.get("description") or "").strip()

def extract_offerings(row) -> str:
    offerings = row.get("core_offerings") or []
    if isinstance(offerings, str):
        offerings = safe_parse(offerings) or []
    
    targets = row.get("target_markets") or []
    if isinstance(targets, str):
        targets = safe_parse(targets) or []

    parts = []
    for v in offerings + targets:
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, dict):
            for key in ["label", "name", "value"]:
                if key in v and v[key]:
                    parts.append(str(v[key]))
                    break
    return " ".join(parts).strip()

def extract_industry(row) -> str:
    naics = safe_parse(row.get("primary_naics"))
    if naics and isinstance(naics, dict):
        return naics.get("label", "")
    return ""

def extract_business(row) -> str:
    business = row.get("business_model") or []
    if isinstance(business, str):
        business = safe_parse(business) or []

    targets = row.get("target_markets") or []
    if isinstance(targets, str):
        targets = safe_parse(targets) or []

    parts = []
    for v in business + targets:
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, dict):
            for key in ["label", "name", "value"]:
                if key in v and v[key]:
                    parts.append(str(v[key]))
                    break
    return " ".join(parts).strip()
    

def build_and_save(df: pd.DataFrame):
    os.makedirs("data", exist_ok=True)
    fields = {
        "description": df.apply(extract_description, axis=1).tolist(),
        "offerings": df.apply(extract_offerings, axis=1).tolist(),
        "industry": df.apply(extract_industry, axis=1).tolist(),
        "business": df.apply(extract_business, axis=1).tolist()
    }

    for field_name, texts in fields.items():
        embeddings = model.encode(
            texts, 
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=64
        ).astype(np.float32)
        np.save(PATHS[field_name], embeddings)


def load_all() -> dict[str, np.ndarray]:
    embeddings = {}
    for field_name, path in PATHS.items():
        embeddings[field_name] = np.load(path)
        
    return embeddings

def embeddings_exist() -> bool:
    return all(os.path.exists(p) for p in PATHS.values())

def search(
    semantic_query: str,
    db: pd.DataFrame,
    all_embeddings: dict[str, np.ndarray],
    complexity: str = "hybrid",
    top_k: int = 40,
) -> pd.DataFrame:
    if db.empty:
        return db

    top_k = min(top_k, len(db))
    query_emb = model.encode([semantic_query], normalize_embeddings=True)
    base_weights = WEIGHTS.get(complexity, WEIGHTS["hybrid"])
    idx = db.index
    individual_scores = {}
    for field_name in base_weights.keys():
        field_embeddings = all_embeddings[field_name][idx]
        individual_scores[field_name] = (field_embeddings @ query_emb.T).flatten()
    
    final_scores = []
    for i in range(len(db)):
        row = db.iloc[i]
        row_field_scores = {field: individual_scores[field][i] for field in base_weights.keys()}
        dynamic_w = adjust_weights_dinamically(row, semantic_query, base_weights)
        score = sum(row_field_scores[f] * dynamic_w.get(f, 0) for f in base_weights.keys())
        final_scores.append(score)

    final_scores = np.array(final_scores)
    
    top_indices = np.argsort(final_scores)[::-1][:top_k]
    result = db.iloc[top_indices].copy()
    result["emb_score"] = final_scores[top_indices]
    return result
