from setuptools import setup, find_packages

setup(
    name="omop_tte_bridge",
    version="1.5.0",
    description="OMOP Data Extraction Code Generator for TTE Pipelines",
    author="TTE_AI Core",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "google-cloud-bigquery",
        "google-cloud-aiplatform",
        "jinja2"
    ],
    python_requires=">=3.8",
)
