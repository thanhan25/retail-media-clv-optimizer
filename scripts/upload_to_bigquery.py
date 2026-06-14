import os

import pandas as pd
from google.cloud import bigquery

# Initialize BigQuery Client
# Note: Ensure your GOOGLE_APPLICATION_CREDENTIALS environment variable is set or you are authenticated via gcloud CLI
client = bigquery.Client(project="sharp-avatar-297916")

DATASET_ID = "retail_media_analytics"
TABLE_ID = "transaction_records"


def clean_and_upload():
    csv_path = os.path.join("data", "online_retail.csv")
    print(f"🔄 Reading data from {csv_path}...")

    # Read dataset with fallback encoding
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="ISO-8859-1")

    print(f"📋 Initial records: {len(df)}")

    # Clean Data matching Retail Media standards
    df = df.dropna(subset=["CustomerID"])  # Remove rows without identifier
    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)
    df = df[df["Quantity"] > 0]  # Filter out cancellations/returns
    df = df[df["UnitPrice"] > 0]  # Filter out system errors/freebies

    # Calculate revenue total per line
    df["TotalRevenue"] = df["Quantity"] * df["UnitPrice"]

    # Format dates correctly for BigQuery
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["InvoiceDate"] = df["InvoiceDate"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Select and rename columns cleanly
    df = df[
        [
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "Country",
            "TotalRevenue",
        ]
    ].rename(
        columns={
            "InvoiceNo": "invoice_id",
            "StockCode": "product_id",
            "Description": "product_name",
            "Quantity": "quantity",
            "InvoiceDate": "transaction_timestamp",
            "UnitPrice": "unit_price",
            "CustomerID": "customer_id",
            "Country": "country",
            "TotalRevenue": "total_revenue",
        }
    )

    print(f"✨ Cleaned records for ingestion: {len(df)}")

    # Create BigQuery Dataset if it doesn't exist
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"✅ Dataset '{DATASET_ID}' already exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "EU"
        client.create_dataset(dataset)
        print(f"🚀 Created new BigQuery Dataset: '{DATASET_ID}'")

    # Configure Ingestion Parameters
    table_ref = dataset_ref.table(TABLE_ID)
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE", source_format=bigquery.SourceFormat.CSV, autodetect=True
    )

    print("📤 Uploading rows to Google BigQuery cloud platform...")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for completion

    print(f"🎉 Success! Data fully loaded into {DATASET_ID}.{TABLE_ID}")


if __name__ == "__main__":
    clean_and_upload()
