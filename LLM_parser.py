from dataclasses import dataclass
import json
import os
import re
from dotenv import load_dotenv
from google import genai
from Prompt import PROMPT

load_dotenv()

# First stage
# The user input will be given to a LLM and it should return 
# an object of type SearchFilters where the fields that appear in the input are not None

@dataclass
class SearchFilters:
    country: str | None = None
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

    def has_hard_filters(self) -> bool:
        return any([
            self.country,
            self.min_employees,
            self.max_employees,
            self.min_revenue,
            self.max_revenue,
            self.is_public is not None,
            self.min_year_founded,
            self.max_year_founded,
        ])