import pandas as pd
df = pd.read_json("data/companies.jsonl", lines=True)

print(df.head())