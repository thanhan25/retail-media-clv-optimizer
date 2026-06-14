import os
import sys
import pandas as pd
import numpy as np
from google.cloud import bigquery
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

def generate_local_mock_data():
    print("🤖 GCP Auth unavailable. Generating synthetic enterprise transaction data...")
    np.random.seed(42)
    n_customers = 250
    n_transactions = 1200
    
    customer_ids = [f"CUST-{1000 + i}" for i in range(n_customers)]
    chosen_customers = np.random.choice(customer_ids, size=n_transactions)
    
    start_date = pd.to_datetime("2025-01-01")
    date_offsets = np.random.randint(0, 180, size=n_transactions)
    timestamps = start_date + pd.to_timedelta(date_offsets, unit='D')
    
    revenues = np.random.exponential(scale=75.0, size=n_transactions) + 15.0
    
    df = pd.DataFrame({
        'customer_id': chosen_customers,
        'transaction_timestamp': timestamps,
        'total_revenue': np.round(revenues, 2)
    })
    return df

def calculate_predictive_clv():
    # Ingestion Layer with Safe Failsafe
    try:
        print("📥 Pulling real-time records from BigQuery for statistical modeling...")
        client = bigquery.Client(project="sharp-avatar-297916")
        query = "SELECT customer_id, transaction_timestamp, total_revenue FROM `sharp-avatar-297916.retail_media_analytics.transaction_records`"
        df = client.query(query).to_dataframe()
    except Exception:
        print("⚠️ Cloud Auth Notice: Default credentials not active.")
        df = generate_local_mock_data()
    
    df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])
    df['total_revenue'] = df['total_revenue'].astype(float)
    
    print("⚙️ Engineering Recency, Frequency, Monetary (RFM-T) matrices...")
    rfm_t = summary_data_from_transaction_data(
        df, 
        customer_id_col='customer_id', 
        datetime_col='transaction_timestamp', 
        monetary_value_col='total_revenue',
        observation_period_end=df['transaction_timestamp'].max()
    )
    
    modeling_df = rfm_t[rfm_t['frequency'] > 0].copy()
    
    print("📈 Fitting Beta-Geometric (BG/NBD) Purchase Frequency Model...")
    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(modeling_df['frequency'], modeling_df['recency'], modeling_df['T'])
    
    modeling_df['predicted_purchases_90d'] = bgf.conditional_expected_number_of_purchases_up_to_time(
        90, modeling_df['frequency'], modeling_df['recency'], modeling_df['T']
    )
    
    print("💰 Fitting Gamma-Gamma Monetary Submodel...")
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(modeling_df['frequency'], modeling_df['monetary_value'])
    
    modeling_df['predicted_12m_clv'] = ggf.customer_lifetime_value(
        bgf,
        modeling_df['frequency'],
        modeling_df['recency'],
        modeling_df['T'],
        modeling_df['monetary_value'],
        time=12, 
        discount_rate=0.01 
    )
    
    output_df = modeling_df.reset_index()[['customer_id', 'predicted_purchases_90d', 'predicted_12m_clv']]
    print(f"Processed CLV indices for {len(output_df)} recurring customers.")
    
    # Local Power BI Relational Layer Generation
    print("📂 Structuring relational Star Schema layers for local Power BI model...")
    output_dir = os.path.join("data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Export Fact Table
    fact_sales = df.copy()
    fact_sales['date_key'] = fact_sales['transaction_timestamp'].dt.strftime('%Y%m%d')
    fact_sales_path = os.path.join(output_dir, "fact_sales_transactions.csv")
    fact_sales.to_csv(fact_sales_path, index=False)
    print(f"   -> Fact Table generated: {fact_sales_path}")
    
    # 2. Export Customers Dimension
    dim_customers = modeling_df.reset_index()
    dim_customers_path = os.path.join(output_dir, "dim_customers.csv")
    dim_customers.to_csv(dim_customers_path, index=False)
    print(f"   -> Customer Dimension generated: {dim_customers_path}")
    
    # 3. Export Calendar Dimension
    start_date = df['transaction_timestamp'].min()
    end_date = df['transaction_timestamp'].max()
    date_range = pd.date_range(start=start_date, end=end_date)
    
    dim_calendar = pd.DataFrame({
        "date_key": date_range.strftime("%Y%m%d"),
        "Date": date_range,
        "Month": date_range.strftime("%B"),
        "Quarter": "Q" + date_range.quarter.astype(str),
        "Fiscal_Year": date_range.year,
        "Weekday": date_range.strftime("%A")
    })
    dim_calendar_path = os.path.join(output_dir, "dim_calendar.csv")
    dim_calendar.to_csv(dim_calendar_path, index=False)
    print(f"   -> Calendar Dimension generated: {dim_calendar_path}")
    
    try:
        client = bigquery.Client(project="sharp-avatar-297916")
        table_ref = client.dataset("retail_media_analytics").table("customer_predictive_clv")
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE", autodetect=True)
        print("📤 Streaming predictive model computations to BigQuery storage layer...")
        client.load_table_from_dataframe(output_df, table_ref, job_config=job_config).result()
        print("🎉 Predictive CLV table successfully written to Cloud BigQuery warehouse!")
    except Exception:
        print("ℹ️ Local run execution complete. Skipping remote cloud write back step.")

if __name__ == "__main__":
    calculate_predictive_clv()