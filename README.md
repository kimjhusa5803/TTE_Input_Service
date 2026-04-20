# TTE Input Preparation Service (Microservice)

This repository contains the standalone Python core for the **Target Trial Emulation (TTE) Input Preparation Service**.

It is designed to be fully decoupled from the primary web application dashboard, allowing for lightweight and secure local installation directly into protected cloud workflows (like GCP/Terra) without carrying unnecessary frontend dashboard bloat.

## Quickstart (Jupyter/Terra)
You can directly load this module as an editable package within your workspace:
```bash
!pip install git+https://github.com/Kim_Lab/TTE_Input_Service.git
```
**(Replace the git URL with your final remote repository link).*

## Repository Structure
- **`omop_tte_bridge/`**: The core python library logic (building blocks).
- **`notebooks/`**: The Jupyter templates used to initialize the interactive OMOP extraction tools.
- **`docs/`**: Extracted architectural and strategic documentation for the service.
