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

---

## Phase 1: Current Operating Model (The "Air-Gapped Handshake")

Because secure Terra environments often completely restrict external internet access and live Vertex integrations are still under review for Phase 2, the **current operating standard** utilizes a manual, secure air-gap mechanism:

1. The provided Python Discovery Notebook executes securely inside the cloud, reading the internal `INFORMATION_SCHEMA`.
2. The notebook dumps the schema summary as a compressed JSON text block directly into the Jupyter Notebook output cell.
3. Because patient PHI is **not** included in this structural text, the researcher can securely highlight, copy, and paste this JSON block into the local `TTE_Input_Service` dashboard on their personal machine.
4. The local web dashboard (which has safe external internet/AI access via API proxies) receives the JSON structure alongside the user's natural language prompts and generates the dialect-specific experimental BigQuery SQL.

## Phase 2: Future Automation Roadmap (V1.5+ Vertex API)

The long-term goal is to phase out the manual "Air-Gapped Handshake" copy/paste steps in favor of a fully autonomous integration natively inside the cloud:

### The Native Cloud API Call
Because NIH Terra natively runs on Google Cloud Platform (GCP), it has an incredible security advantage: **Vertex AI**.
Instead of bouncing data outward to the local dashboard, the Python package will eventually talk directly to Google's internal Vertex AI models.

**Authentication:** 
The script will use the native Jupyter Notebook Service Account credentials. The package will use GCP `Application Default Credentials` to summon a Gemini model entirely securely within the VPC boundary to automatically generate complex SQL extractions without ever leaving the cloud environment.
