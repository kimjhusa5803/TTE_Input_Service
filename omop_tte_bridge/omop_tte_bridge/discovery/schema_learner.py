import json
import logging
from google.cloud import bigquery

# Configure basic logging for the module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BigQuerySchemaLearner:
    """
    Building block module to discover table and column schemas from standard
    Google BigQuery deployments, targeted for OMOP architectures like NIH All of Us or VUMC SD GCP.
    """
    
    def __init__(self, project_id=None):
        """
        Initializes the BigQuery client. Uses Application Default Credentials natively 
        within the Jupyter/Terra cloud environment if project_id is not specified.
        """
        if project_id:
            self.client = bigquery.Client(project=project_id)
        else:
            # Inherits default environment project and identity
            self.client = bigquery.Client()
            
    def get_dataset_schema(self, dataset_id, target_tables=None):
        """
        Extracts structural table/column information from the dataset's INFORMATION_SCHEMA.
        Crucially, this does NOT touch or extract patient PHI data.
        
        Args:
            dataset_id (str): Formatted as 'dataset' or 'project.dataset'
            target_tables (list): Core OMOP tables to look for mappings of.
            
        Returns:
            dict: The topology layout in a python dictionary.
        """
        if not target_tables:
            target_tables = [
                'person', 'condition_occurrence', 'drug_exposure', 
                'measurement', 'observation', 'procedure_occurrence', 'visit_occurrence', 'concept'
            ]
            
        # Determine the project and dataset correctly for the INFORMATION_SCHEMA path
        if '.' in dataset_id:
            project, dataset = dataset_id.split('.', 1)
            schema_target = f"`{project}.{dataset}.INFORMATION_SCHEMA.COLUMNS`"
        else:
            # If only dataset is provided, rely on default project
            schema_target = f"`{self.client.project}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`"
            
        # We use a LIKE condition for each target_table because some institutions (like AllOfUs)
        # prefix their tables, e.g. 'cb_search_person' instead of just 'person'.
        conditions = " OR ".join([f"table_name LIKE '%{t}%'" for t in target_tables])
        
        query = f"""
        SELECT table_name, column_name, data_type 
        FROM {schema_target}
        WHERE {conditions}
        """
        
        logging.info(f"Executing secure schema extraction against {schema_target}...")
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            schema_dict = {
                "dialect": "BigQuery GCP", 
                "target_dataset": dataset_id,
                "tables": {}
            }
            
            for row in results:
                t_name = row.table_name
                c_name = row.column_name
                d_type = row.data_type
                
                if t_name not in schema_dict["tables"]:
                    schema_dict["tables"][t_name] = []
                
                schema_dict["tables"][t_name].append({"column": c_name, "type": d_type})
                
            logging.info(f"Successfully discovered {len(schema_dict['tables'])} relevant tables.")
            return schema_dict
            
        except Exception as e:
            logging.error(f"Failed to extract schema metadata: {e}")
            raise

    def export_schema_to_json(self, schema_dict):
        """
        Formats the python dictionary schema into a compressed JSON string 
        that can be directly copied into the React UI.
        """
        return json.dumps(schema_dict, indent=2)

    def generate_copy_paste_payload(self, dataset_id):
        """
        Convenience function that wraps extraction and JSON formatting for the Notebook.
        """
        schema = self.get_dataset_schema(dataset_id)
        return self.export_schema_to_json(schema)
