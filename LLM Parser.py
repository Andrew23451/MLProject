from dataclasses import dataclass
import json

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
def from_llm(cls, query: str, client) -> "SearchFilters":
    """Send to the LLM and get back a filled object."""

    PROMPT = """
    You are a query parser for a company search system.
    You should extract the filters from the user query.

    You should return a JSON object like this and nothing else:
    {
        country: <string or null>
        min_employees: <int or null>
        max_employees: <int or null>
        min_revenue: <float or null>
        max_revenue: <float or null>
        is_public: <bool or null>
        min_year_founded: <int or null>
        max_year_founded: <int or null>
        semantic_query: str = <rich description of 
        the ideal company that mathces the query>
        complexity: str = "structured | hybrid | semantic"
    }

    You should think it like this, I'll give you some examples:
      - Use null for anything not mentioned in the query
      - "in/from Romania", country: Romania
      - "over $50 million revenue", the min_revenue = 50000000.0, max_revenue = null
      - "with more than 1000 employees", the min_employees = 1000, max_employees = null
      - "public company", the is_public should be set to true
      - "a company founded before 2019", max_year_founded = 2019, min_year_founded = null
      - complexity = structured, only hard filters needed
      - complexity = semantic, needs reasoning(supply chain, ecosystem, roles)
      - complexity = hybrid, both of the above
      - semantic_query should describe what the ideal matching company looks like
      Be careful, if there might appear the keywords "year", "revenue", but no numerical values assigned to them,
      return null for that field. For example, "good revenue". And also pay attention, if there is a country, you will only 
      complete the "country" field if it is in that country ("in Romania"), not "near Romania" or "not in Romania".
    """

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        system=PROMPT,
        messages = [{"role": "user", "content": query}]
    )

    text = response.content[0].text
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        
    text = text.strip()
    data = json.loads(text)

    valid_fields = {}
    # Take each pair (key, value) from the data 
    for k, v in data.items():
        if v is not None:
            if k in cls.__dataclass_fields__:
                valid_fields[k] = v
    return cls(**valid_fields)

def has_hard_filters(self) -> bool:
    return any([
        self.country, self.min_employees, self.max_employees,
        self.min_revenue, self.max_revenue, self.is_public,
        self.min_year_founded, self.max_year_founded
    ])
