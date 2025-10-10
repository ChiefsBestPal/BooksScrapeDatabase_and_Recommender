"""
Simple utility to transfer analytics raw semi-structured data into Cloud
BigQuery CSV Bulk Uploader
Automatically uploads all CSVs from Neo4j Desktop import folder to BigQuery

Might need rework and vary based on cases... but should be something simple like this
Mostly need this to avoid doing this manually with BQ CLI or on Google Cloud interface starting jobs one by one
"""

import os
import glob
from google.cloud import bigquery

from dotenv import load_dotenv

load_dotenv() # .env file... call with os.getenv see below CONFIGURATION

# =============================
# CONFIGURATION ###############
# =============================
CSV_FOLDER = rf"{os.getenv('neo4j_desktop_root_path')}\.Neo4jDesktop\relate-data\dbmss\dbms-1c9e4905-ed10-48d8-b3fb-0acbf104f39b\import"
PROJECT_ID = os.getenv('gcp_project')#"booksscrapedatabase-warehouse"  # REPLACE WITH YOUR GCP PROJECT ID
DATASET_ID = os.getenv('gcp_main_warehouse_dataset') #"BookScrapeDB"  # BigQuery dataset name

# ===============
# SETUP ########
# ===============

def create_dataset_if_not_exists(client, dataset_id):
    """Create BigQuery dataset if it doesn't exist"""
    dataset_ref = f"{PROJECT_ID}.{dataset_id}"
    
    try:
        client.get_dataset(dataset_ref)
        print(f"✓ Dataset {dataset_id} already exists")
    except:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # Free tier region
        client.create_dataset(dataset)
        print(f"✓ Created dataset {dataset_id}")


def upload_csv_to_bigquery(client, csv_path, dataset_id):
    """Upload a single CSV file to BigQuery"""
    
    # Get table name from filename
    filename = os.path.basename(csv_path)
    table_name = filename.replace('.csv', '')
    table_id = f"{PROJECT_ID}.{dataset_id}.{table_name}"
    
    # Configure load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip header row
        autodetect=True,  # Auto-detect schema from CSV
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite if exists
        allow_quoted_newlines=True,  # Handle multi-line fields
        allow_jagged_rows=True,  # Handle inconsistent column counts
    )
    
    print(f"⏳ Uploading {filename}...", end=" ")
    
    try:
        # Load CSV into BigQuery
        with open(csv_path, "rb") as csv_file:
            job = client.load_table_from_file(
                csv_file, 
                table_id, 
                job_config=job_config
            )
        
        # Wait for job to complete
        job.result()
        
        # Get table info
        table = client.get_table(table_id)
        print(f"✓ Loaded {table.num_rows} rows into {table_name}")
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False


def main():
    """Main function to upload all CSVs"""
    
    print("=" * 60)
    print("BigQuery CSV Bulk Uploader")
    print("=" * 60)
    
    # Initialize BigQuery client
    try:
        client = bigquery.Client(project=PROJECT_ID)
        print(f"✓ Connected to GCP project: {PROJECT_ID}")
    except Exception as e:
        print(f"✗ ERROR connecting to BigQuery: {str(e)}")
        print("\nMake sure you have:")
        print("1. Set up authentication (see instructions below)")
        print("2. Replaced PROJECT_ID with your actual GCP project ID")
        return
    
    # Create dataset if needed
    create_dataset_if_not_exists(client, DATASET_ID)
    
    # Find all CSV files
    csv_pattern = os.path.join(CSV_FOLDER, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"\n✗ No CSV files found in: {CSV_FOLDER}")
        return
    
    print(f"\n📁 Found {len(csv_files)} CSV files")
    print("-" * 60)
    
    # Upload each CSV
    successful = 0
    failed = 0
    
    for csv_path in csv_files:
        if upload_csv_to_bigquery(client, csv_path, DATASET_ID):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("-" * 60)
    print(f"\n✓ Successfully uploaded: {successful} tables")
    if failed > 0:
        print(f"✗ Failed: {failed} tables")
    
    print(f"\n🎉 Done! View your data at:")
    print(f"https://console.cloud.google.com/bigquery?project={PROJECT_ID}&d={DATASET_ID}")


if __name__ == "__main__":
    main()


# ================================================================
# SETUP INSTRUCTIONS
# ================================================================
"""
STEP 1: Install required package
--------------------------------
pip install google-cloud-bigquery


STEP 2: Set up GCP Authentication
----------------------------------
Option A - Service Account (Recommended):
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Create service account with "BigQuery Admin" role
3. Create and download JSON key
4. Set environment variable:
   
   Windows (PowerShell):
   $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\key.json"
   
   Windows (CMD):
   set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\key.json
   
   Linux/Mac:
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

Option B - User Authentication (Quick test):
1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
2. Run: gcloud auth application-default login
3. Follow browser prompts


STEP 3: Update Configuration
-----------------------------
1. Replace PROJECT_ID with your GCP project ID
2. Update CSV_FOLDER path if different
3. Run the script: python upload_to_bigquery.py


TROUBLESHOOTING
---------------
- "DefaultCredentialsError": Authentication not set up
- "Permission denied": Service account needs BigQuery permissions
- "Dataset not found": Script will auto-create it
- "Table already exists": Script will overwrite (WRITE_TRUNCATE mode)
"""