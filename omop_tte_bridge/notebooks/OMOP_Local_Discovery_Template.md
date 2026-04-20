# OMOP TTE Bridge: Local Discovery Template

This notebook demonstrates how to deploy the `omop_tte_bridge` building blocks locally in your secured GCP/Terra environment to support the TTE_Input_Service.

## 1. Setup and Deployment
First, you need to deploy the python package. Ensure the `omop_tte_bridge` directory is uploaded to your environment.
Run the following pip command to install it. Replace `/path/to/...` with your actual setup directory.

```python
!pip install -e /home/jupyter/packages/omop_tte_bridge
```

## 2. Step 1: Discover Local Architecture
The core building block `BigQuerySchemaLearner` securely queries your `INFORMATION_SCHEMA` to build the required JSON payload for the main TTE web app.

```python
from omop_tte_bridge.discovery.schema_learner import BigQuerySchemaLearner

# Initialize learner (Inherits credentials if running in Terra/GCP automatically)
learner = BigQuerySchemaLearner()

# Enter your project.dataset or dataset name here:
DATASET_ID = "your_project.your_dataset"

# Pull and format the topology payload
topology_json = learner.generate_copy_paste_payload(DATASET_ID)

print("===========================================================")
print("COPY THE TEXT BELOW AND PASTE INTO THE TTE DB DISCOVERY UI:")
print("===========================================================")
print(topology_json)
```

## 3. Step 2+ Follow Up: Executing Generated BigQuery SQL
Once you have iteratively generated the experimental BigQuery target trial extraction SQL using the main web-app UI, you can test it directly here.

```python
from google.cloud import bigquery

client = bigquery.Client()

# Paste your specific experimental SQL string from the TTE Prep Service app here
experimental_sql = """
SELECT * 
FROM `your_project.your_dataset.cb_search_person`
LIMIT 10;
"""

print("Executing follow-up query...")
df = client.query(experimental_sql).to_dataframe()
display(df)
```
