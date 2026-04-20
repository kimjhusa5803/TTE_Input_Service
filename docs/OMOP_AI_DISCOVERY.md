# V1.5 Future Roadmap: AI-Assisted OMOP Schema Discovery

## The Problem
While OMOP is the "Common Data Model," in practice, structural anomalies exist between institutions. For example, some biobanks might prefix their tables with custom strings, or use a slightly different custom string formatting for their patient columns. 
If our Python query-builder uses strictly hardcoded OMOP v5.4 SQL, the queries will instantly fail in these environments. 

We need the Python package to securely "read" the database topology and adapt.

---

## How Step 2 Works: The Mechanics of AI Topology Discovery

This explains the exact flow of how a Jupyter notebook inside a highly restricted environment safely leverages AI to learn the database structure *without* violating security protocols or moving clinical data.

### Step 2.1: Extracting Non-PHI Metadata (Local Execution)
Before generating any clinical SQL, our Python package executes a highly restricted BigQuery metadata query.
Instead of querying patient tables, it targets the backend `INFORMATION_SCHEMA`:

```sql
SELECT table_name, column_name, data_type 
FROM `project.dataset.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN ('person', 'condition_occurrence', 'drug_exposure');
```
**Security Implication:** This returns only structural blueprint data (e.g., "The 'person' table has a column named 'birth_datetime' of type TIMESTAMP"). **Zero patient data (PHI) is ever touched or extracted.**

### Step 2.2: The Native Cloud API Call
Because NIH Terra natively runs on Google Cloud Platform (GCP), it has an incredible security advantage: **Vertex AI**.
Instead of sending data out to the public internet (like `chatgpt.com`), the Python package talks directly to Google's internal Vertex AI models.

**Authentication:** 
The script does not use a raw "API Key" that could be stolen. Because the Jupyter Notebook is running inside a Terra Workspace, it automatically inherits the Google Service Account credentials of that secure boundary. The package uses GCP `Application Default Credentials` to summon a Gemini model entirely securely.

### Step 2.3: Synthesizing the AI Translation Prompt
The Python package bundles the `INFORMATION_SCHEMA` text output into a strict system prompt and sends it to the AI.

**Example Prompt Payload sent to Gemini/Vertex AI:**
> *"You are an expert OHDSI/OMOP Database Architect. I have attached the INFORMATION_SCHEMA of a target biobank's database. Identify if this matches standard OMOP v5.4, or if it utilizes a known custom dialect (like NIH All of Us). Parse the schema and return a strict JSON mapping object aligning the standard OMOP concepts to their custom table/column names found in the biobank."*

### Step 2.4: Receiving the JSON Blueprint
The AI model returns a structured JSON mapping block. 

*Example AI Response:*
```json
{
  "dialect_detected": "NIH All of Us (v7)",
  "mappings": {
    "person_table": "cb_search_person",
    "drug_exposure_table": "cb_search_all_events",
    "custom_date_cast": "CAST(drug_exposure_start_datetime as DATE)"
  }
}
```

### Step 2.5: Feeding the Query Engine
The Python package receives this JSON mapping file and feeds it directly into our underlying Jinja BigQuery templating engine. The user is now granted a perfectly optimized BigQuery SQL string ready for execution in the exact dialect the local environment expects!

---

## Contingency Plans (If Vertex AI is Blocked)

Even if a specific NIH Terra workspace is locked down so tightly that it forcefully blocks the internal Vertex API, we can still achieve auto-mapping through fallback mechanisms:

### Hand-off to the Local React Dashboard (`.rda` conversion)
Once the Python package successfully extracts the final cohort matrix from the BigQuery servers, it generates a standard `.csv` file. 
Because the main local TTE application precisely requires `.rda` formatting to run target trial analysis robustly, a bridge utility script (`packages/omop_tte_bridge/utils/csv_to_rda.R`) has been provided. 

**Workflow:**
1. Download `trial_cohort.csv` from your Cloud workspace.
2. Run locally: `Rscript packages/omop_tte_bridge/utils/csv_to_rda.R trial_cohort.csv TrialEmulation/data/trial_cohort.rda`
3. The local dashboard pipeline will instantly detect this new RDA file in the Dropdown for execution!

### Alternative 1: The Local Offline Dictionary
Because many major biobanks are highly popular, their exact topological quirks are known. The `omop_tte_bridge` Python package can ship with a pre-compiled, offline JSON catalogue of known mappings. When `schema_learner` runs, it simply compares the local `INFORMATION_SCHEMA` against its internal dictionary. If it matches a known profile, it automatically routes the templates without needing to talk to a live AI.

### Alternative 2: Bring-Your-Own-Key (Whitelisted Egress)
If Vertex is blocked but general HTTP outbound traffic to external providers is allowed (e.g., standard OpenAI/Gemini REST endpoints), the package can accept a user's personal API Key to process the metadata mapping.

### Alternative 3: The "Air-Gapped Handshake"
If Terra enforces a complete, literal air-gap:
1. The Python package dumps the `INFORMATION_SCHEMA` summary as a compressed JSON block directly into the Jupyter Notebook output cell.
2. The researcher highlights, copies, and pastes this block into the local `TTE_AI` dashboard outside of Terra.
3. The local dashboard (which has full internet access) connects to the AI to synthesize the mapping logic.
4. The researcher uploads the resulting tiny `mapping.json` rules-file back into Terra, and the Python package uses it to build the final queries!
