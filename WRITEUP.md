# Company Search System

## Overview

This system is a multi-layer company retrieval engine that accepts a natural language query, where there might be misspelling and returns a ranked list of companies from a structured database. The challenge it addresses is that company search queries are not uniforme, some are almost entirely structured filters (`Public software companies with more than 1000 employees`), while others require semantic reasoning about roles and business relationships (`Companies that could supply packaging materials for a cosmetics brand`).

## System Architecture

The system is engineered as a **Modular Pipeline**, where the input query is filtered three times in order to achieve high efficiency.

### Preprocessing the database

#### Raw data challenges

The raw database is a JSONL file where many fields are stored as stringified dictionaries or lists rather than parsed JSON. To make searching work, the organization is:

* Fixing "broken" data

The lists and the dictionaries were being read as plain text. The `safe_parse` function automatically detects this and converts them into a format that Python can actually use. 

* Derived columns

Two columns were derived and added to the DataFrame during preprocessing: country - full lowercase country name resolved from the ISO code using `COUNTRY_CODES` and continent: continent name resolved using `CONTINENT_MAP`.


### Layer 1 - Query Parser

#### Structured Query Parsing & Deterministic Filtering

The query parser transforms a free-form natural language query into a typed, structured object named **Search Filters** that helps a lot for the future layers. A single call to a LLM with a carefully engineered prompt returns a JSON object that is parsed into a Python dataclass that has these fields: `country`, `continent`, `region`, `min_employees`, `max_employess`, `min_revenue`, `max_revenue`, `is_public`, `min_year_founded`, `max_year_founded`, `semantic_query`, `complexity`. Default, all fields are None. A query such as `Logistic companies in Romania` will populate `country` and leave all numeric fields as `None`. A different approach like `Public companies with more than 1000 employees from Europe`, will populate `is_public`, `min_employees` and `continent`. The `region` field is populated manually by trying to extract it, using some of the most popular regions in the world. After some tests, the LLM gave some inconsistencies, so the decision was to build a **REGION_MAP** dictionary and to match the name from the query.  

#### Importance of semantic_query field

The `semantic_query` field is the most important output of the parser and the one most frequently underestimated. Rather than passing the raw user query to the embedding model, the parser generates a rich, expanded description of the ideal matching company. For example, the query `Logistic companies from Romania` will be transformed to `Companies operating in logistics, freight forwarding, supply chain management and warehousing, based in Romania, serving B2B clients`. For the query `Packaging for cosmetic brands`, the parser will return something like `Manufacturers and suppliers of packaging materials including bottles, jars, tubes and containers. These companies produce and sell packaging to cosmetics and beauty brands`. The second example demonstrates the critical function of the semantic query for ecosystem queries - it explicitly describes the supplier role rather than the end brand, which prevents the embedding model from matching cosmetics companies instead of packaging suppliers.

### Importance of the complexity field 

The `complexity` field is critical, because it dictates the operational mode of the system, directly influencing how every following component process the data. It can have three value:

* **structured** - used when the input consists exclusively of explicit constraints
* **semantic** - applied when the query requires reasoning and context
* **hybrid** - both of the above are involved

This first filter really depends on the AI model that is used, because a newer one will make much more accurate extractions, significantly reducing the "false negative" rate where valid companies are accidentally filtered out. So, in order to maximize the efficiency, please create an account at [OpenRouter](https://openrouter.ai/models) and choose the best model that can be afforded. Modify the file "LLM_parser.py" and put that model in the function "from_llm". Also create a `.env` file and put your API Key named `OPENROUTER_API_KEY`. You will find an example in the final project. 


### Layer 2 - Hard Filtering

Hard filtering eliminates companies from the full database that definitively cannot satisfy the query. Companies that fail any single filter are permanently removed and do not appear in the other layers. This is a strict exclusion mechanism, not a ranking mechanism.

Filtering is applied as a pandas boolean mask over the full DataFrame. Each filter condition is composed with logical AND.

#### NaN Handling

Numeric columns (`employee_count`, `revenue`, `year_founded`) contain a significant proportion of **null** values. The design decision here is to exclude companies with null values when a numeric filter is explicitly requested. The rationale is that if a user requests companies with revenue over $50 million, a company with unknown revenue is not a useful result even if it might teoretically qualify. Returning unknown-revenue companies alongside known-qualifying ones will reduce the precision.

### Layer 3 - Embedding

Embedding search retrieves semantically relevant companies from the pool produced by Layer 2 (or the full database for semantic queries).It converts both the semantic query and the company text into dense vector representations and ranks by cosine similarity. 

#### Multi-field Embedding

Rather than embedding all company information into a single text string, the system maintains four separate embedding arrays - one per field:

* **description** (free text company description) - semantic understanding of what the company does
* **offerings** (**core_offerings** + **target markets**) - specific products, services and customer segments
* **industry** (**primary_naics** label) - broad industry category confirmation 
* **business** (**business model** + **target_markets**) - business model and operational context

Each field is embedded independently and saved to disk as a `.npy` array. At search time, the system slices the relevant rows from each array and computes a weighted sum of per-field cosine similarity scores.

#### Weighted scores by complexity

The relative weights assigned to each field vary based on the query complexity:

* **semantic** - **description** (0.35)
               - **offerings** (0.30)
               - **industry** (0.10)
               - **business** (0.25)

* **hybrid**   - **description** (0.20)
               - **offerings** (0.25)
               - **industry** (0.30)
               - **business** (0.25)

* For **semantic** queries, the `description` and `offerings` fields carry the most, because the query requires understanding the role and function of the company. The `industry` field receives a low weight, because NAICS codes are too rough to distinguish between, for example, a `electricity company` and a `supplier for an electricity company`

* For **hybrid** queries, hard filters have already narrowed the pool by location and size. The embedding layer now needs to confirm industry category, so `industry` receives more weight.

#### Dynamic Threshold

After ranking, a cliff detection algorithm removes candidates whose scores fall sharply below the leading results. This is applied only when there is a significant discontinuity in the score distribution. For example, when the top three results score `0.52`, `0.51`, `0.49` and the fourth scores `0.27`. The gap of `0.22` far exceeds the average gap and this signals that is not that relevant. A minimum of three results is always return regardless.


## Known Limitations and Tradeoffs 

### Optimization

In building this engine, I prioritized **Robustness**, **Accuracy** and also **Simplicity**, as it doesn't use some complex databases for calculations. 

* **Robustness** - The `safe_parse` and `list_to_text` functions ensure that even if the raw data is malformed or has missing fields, the pipeline continues without errors. Also, by moving the region logic out of the LLM and into a Python `REGION_MAP`, I eliminated a risk. The system doesn't "guess" where Scandinavia is, but makes sure that it knows exactly which countries to look for every single time. 

* **Accuracy** - a search engine is useless if it misses the right company or shows a wrong one. I separated the **intent extraction** from the **data retrieval**. The LLM doesn't search the database; It just takes a user query and converts it to a JSON object. This ensures that the downstream logic receives structured instructions. The embedding model also uses the `build_text` function to create a better "profile" for each company (merging location, industry and description).

### Limitations

### Negation is not supported

The hard filter cannot express negative conditions. A query such as `companies not in Romania` or `companies outside Europe` will not exclude the specific region. The LLM parser is instructed to ignore negative conditions and the `semantic_query` may describe the exclusion, but the embedding model has limited ability to penalize based on the condition. 

### Missing data hard filtering

The database has significant null rates in numeric columns. Queries that specify employee count or revenue thresholds will only return companies that have those fields populated, regardless of whether the non-populated companies would otherwise qualify.

### LLM parser consistency

The AI model that is used cannot always return identical outputs for the same query. The complexity label in particular can vary between `hybrid` and `semantic` across runs. This introduces non-determinism into the routing logic, which in turn affects which layers run and therefore which companies are returned. Prompt tells explicitly to be really careful, but this doesn't eliminate the probability. For example, if the user query is `Innovative logistics startups in Central Europe`, the parser might categorize this differently across two separate runs: `semantic` when the focus is on `innovative logistics` and `hybrid` when the focus is on both the region and the category of business. 

### Database size

The database contains 477 companies. This is a small dataset and the embedding doesn't benefit from approximate nearest-neighbor indexing that would be required at scale. The current numpy dot-product approach is appropriate for this size but would not scale to tens of thousands of records without architectural changes.


### Scaling

The current system uses a **Linear Search** (brute-force) approach. While perfect fpor 477 companies, it would bcome too slow
as the dataset grows. To handle 10.000 companies per query, the system should be more focused on finding the best candidates quickly. First step, I would move from storing the embeddings in a simple numpy array to a dedicated `vector database` like **Pinecone** to use the ANN (Approximate Nearest Neighbour). The second step, I will use **FAISS** to speed up the math and efficiently search in dense vectors. 

## How to run the project

In order to run the project, in the `solution.py` file, you can add different types of queries. 
This project uses Docker and docker-compose files to simplify the setup and ensure consistency between different users. To further simplify the installation process, use the provided Makefile as follow:

* **make build** - install all the dependencies for the project
* **make up** - run the implementation
* **make down** - stop the running and clean the RAM

**Disclaimer**: In the Makefile, everything is runned with root privilleges. If the user is part of the Docker group, the `sudo` can be removed. 

## Testing and validation

I included a set of initial tests to verify the core logic of the system. While these are not exhaustive, they were essential during the development for validation (ensuring that the functions `safe_parse` and `build_text` handle different data types correctly), accuracy (the embedding scores were made dinamically afterwards, not simple, hardcoded ones and i also modified the threshold for the embedding score so that the output is as near as possible to be considered a good result). 





