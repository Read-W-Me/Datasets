# Datasets Archive

An archive repository holding dataset fetch scripts and documentation for the "Study With Me" (BASHAR) project. 

## ⚠️ Core Rule: No Raw Data Uploads
**Do NOT upload raw dataset files (CSVs, ZIPs, images) directly to this repository.**

Uploading gigabytes of raw data violates GitHub's file size limits (100MB max) and permanently bloats the Git history, slowing down operations for the entire team. Instead, this repository uses a script-based approach to pull data directly from original academic sources on demand.

## How to Add a New Dataset
When integrating a new dataset into the project, provide a download script rather than the data itself:

1. Create a new directory for the dataset (e.g., `mkdir ETDD70`).
2. Write a Python script (e.g., `fetch_and_analyze.py`) that:
   - Downloads the dataset from its source (Zenodo, PhysioNet, Kaggle, etc.).
   - Extracts the files into a local `/raw_data` folder.
   - Generates a quick Exploratory Data Analysis (EDA) plot to verify the data structure.
3. **Data Protection:** Always extract your files into a folder named `raw_data/` or `data/`. The global `.gitignore` at the root of this repository is configured to automatically block those directories (along with all `.csv` and `.zip` files) to ensure they never accidentally get staged.
4. Update the **Dataset Metadata Registry** below.
5. Commit and push the script.

## How to Use a Dataset
To use a dataset locally:
1. Clone this repository.
2. Navigate to the desired dataset's folder (e.g., `cd ETDD70`).
3. Run the fetch script (e.g., `python3 fetch_and_analyze.py`). The script will pull the heavy files directly to your local machine.

---

## Dataset Metadata Registry

*Contributors: Add a new row to this table immediately upon uploading a new dataset fetch script.*

| Dataset Name | Directory | Content Description | Source / Fetch Method |
| :--- | :--- | :--- | :--- |
| **ETDD70** | `/ETDD70` | Raw reading recordings from 70 Czech children (35 dyslexic, 35 typical). Includes continuous spatial gaze streams and metadata. | Fetched via Zenodo URL (`fetch_and_analyze.py`) |
| *[Template]* | `/directory` | *Brief description of the raw data, subjects, or environment.* | *Origin URL or API method* |