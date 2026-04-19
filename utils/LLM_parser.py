from dataclasses import dataclass
import json
import os
import time
from dotenv import load_dotenv
from google import genai
from utils.prompt import PROMPT

load_dotenv()

# First stage
# The user input will be given to a LLM and it should return 
# an object of type SearchFilters where the fields that appear in the input are not None

@dataclass
class SearchFilters:
    country: str | None = None
    continent: str | None = None
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
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        last_error = None
        for attempt in range(1, 4):
            try:
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=PROMPT + f"\n\nUser query: {query}"
                )

                text = response.text
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
                last_error = e
                if attempt < 3:
                    time.sleep(2 * attempt)

        return cls() # all fields are None, but I hope the embeddings will still work         
    

# TODO: If the LLM is full of requests/is not working, I should handle the situation