# TTE_Input_Service: Development Strategy & Architecture

## Core Philosophy: Exploratory & Interactive Design

The overarching strategy for the next milestone of the TTE_Input_Service is to prioritize an **interactive and exploratory workflow**. Rather than building a rigid, one-shot automation script, the service functions as an interactive "sandbox" where researchers can interact with the AI to refine their inputs. 

This interactive approach ensures accuracy when dealing with complex, institution-specific OMOP schemas and subtle phenotype definitions, paving the way for reliable, fully automated Target Trial Emulation (TTE) in the final phase.

## The Three-Step Operating Architecture

The current dashboard UI and underlying Python backend architecture are purposefully structured to support the following three-step procedure, designed around strict "air-gapped" security protocols:

### Step 1: Secure Discovery (Cloud Phase via Notebooks)
**Objective:** Standardize the local database structure and identify dialect quirks (e.g., table prefixes like `cb_search_person` used by "NIH All of Us" or standard schemas used by "VUMC SD").

*   **Mechanism:** Instead of extracting raw patient data (PHI), the researcher physically logs into their secured cloud enclave (like Terra workspaces). They execute the provided Python Jupyter Notebook (`OMOP_AllOfUs_Discovery.ipynb`), which safely discovers the `INFORMATION_SCHEMA` and bundles the blueprint.
*   **Action:** The researcher copies the resulting JSON string from their cloud notebook.

### Step 2: Interactive Query Translation (Local Dashboard Phase)
**Objective:** Translate natural language medical phenotypes into exact BigQuery SQL queries utilizing the architectural blueprint extracted in Step 1.

*   **Mechanism:** The researcher switches over to the local `TTE_Input_Service` web dashboard. 
*   **Interaction:** They paste the OMOP schema JSON into the UI and provide a natural language prompt (e.g., *"Find patients exposed to Metformin with a prior diagnosis of Type 2 Diabetes"*). 
*   **Iteration:** The local UI routes this prompt through a generation layer to output experimental AI-assisted BigQuery SQL. The user reviews the snippet, tweaks the prompt, and iterates until the translated SQL perfectly maps their required variables.

### Step 3: Future Automation (V1.5+ API Integration)
**Objective:** Eradicate the manual "copy/paste" air-gapped translation layer in favor of seamless automation.

*   **Roadmap Strategy:** Once the SQL mapping mechanics are proven robust via the dashboard UI, the next major version will revise the Python microservice to bypass the local web app entirely. The Python notebooks natively residing in the cloud will securely query Google Vertex AI directly, parsing complex extraction prompts internally and automatically generating the `.rda` files required by the overall TTE engine.
