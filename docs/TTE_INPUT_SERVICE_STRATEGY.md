# TTE_Input_Service: Development Strategy & Architecture

## Core Philosophy: Exploratory & Interactive Design

The overarching strategy for the next milestone of the TTE_Input_Service is to prioritize an **interactive and exploratory workflow**. Rather than building a rigid, one-shot automation script, the service functions as an interactive "sandbox" where researchers can interact with the AI to refine their inputs. 

This interactive approach ensures accuracy when dealing with complex, institution-specific OMOP schemas and subtle phenotype definitions, paving the way for reliable, fully automated Target Trial Emulation (TTE) in the final phase.

## The Two-Step Architectural Procedure

The current UI design and underlying backend architecture are structured to support the following two-step procedure:

### Step 1: Discover the Local Architecture (Schema Mapping)
**Objective:** Standardize the local database structure and identify dialect quirks (e.g., specific table prefixes, custom datetime formats used by "NIH All of Us" or "VUMC SD").

*   **Mechanism:** Instead of passing raw patient data (PHI), the system relies purely on database structural blueprints. The researcher executes a secure query against their `INFORMATION_SCHEMA` in their local, restricted environment (like a Terra Jupyter Notebook).
*   **Interaction:** In the UI (Panel 1: "Paste OMOP Topology JSON"), the user pastes this schema blueprint. The AI backend consumes this JSON to map the local architecture to the standard OMOP v5.4 topology.

### Step 2: Interactively Generate Experimental SQL (Phenotype & Variable Mapping)
**Objective:** Translate natural language medical phenotypes into exact SQL queries that map seamlessly into the required TTE matrix variables.

*   **Mechanism:** The researcher utilizes the UI's **"Generation Mode"** set to **"Exploratory (Investigation)"**. 
*   **Interaction:** The user inputs multiple natural language phenotype descriptions in the "NL Prompt / Rules" text area (e.g., *"Find patients exposed to Metformin with a prior diagnosis of Type 2 Diabetes"*). 
*   **Iteration:** Upon clicking "Generate SQL", the AI engine returns an experimental BigQuery SQL script. The user can review it, tweak their natural language prompt, and regenerate the SQL iteratively. This iterative loop continues until the logic perfectly matches their intended clinical variables.

## Path to Automation
Once the user validates that the interactive, experimental queries successfully generate the required medical cohorts, they can toggle the system to **"Final TTE Matrix (Production)"** mode. This transitions the interactive query logic into the final, automated data extraction pipeline required by the Target Trial Emulation engine.
