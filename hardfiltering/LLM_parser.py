from dataclasses import dataclass
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from utils.prompt import PROMPT

load_dotenv()

# First stage
# The user input will be given to a LLM and it should return 
# an object of type SearchFilters where the fields that appear in the input are not None

@dataclass
class SearchFilters:
    country: str | None = None
    continent: str | None = None
    region: str | None = None
    min_employees: int | None = None
    max_employees: int | None = None
    min_revenue: float | None = None
    max_revenue: float | None = None
    is_public: bool | None = None
    min_year_founded: int | None = None
    max_year_founded: int | None = None
    semantic_query: str = ""
    complexity: str = "hybrid"

    @classmethod
    def from_llm(cls, query: str) -> "SearchFilters":
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        
        
        for attempt in range(1, 4):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-4o-mini", # Put your best model here
                    messages=[
                        {"role": "system", "content": PROMPT},
                        {"role": "user", "content": f"User query: {query}"}
                    ],
                    temperature=0 # This can be modified, depending on the AI Model used (between 0 and 2)
                )
                text = response.choices[0].message.content
                if "```" in text:
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
        
                text = text.strip()
                data = json.loads(text)

                valid_fields = {
                    k: v for k, v in data.items()
                    if v is not None and k in cls.__dataclass_fields__
                }
                return cls(**valid_fields)
            except Exception as e:
                print(e)
                if attempt < 3:
                    time.sleep(2 * attempt)

        return cls() # all fields are None, but I hope the embeddings will still work
