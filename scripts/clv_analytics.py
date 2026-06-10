import os
import pandas as pd
from google.cloud import bigquery
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

# Connect Client
client = bigquery.Client(project="sharp-avatar-297916")

def calculate_predictive_clv():
    print("📥 Pulling real-time records from BigQuery for statistical modeling...")
    query = "SELECT customer_id, transaction_timestamp, total_revenue FROM `sharp-avatar-297916.retail_media_analytics.transaction_records`"
    df = client.query(query).to_dataframe()
    
    # Ensure correct data primitives
    df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])
    df['total_revenue'] = df['total_revenue'].astype(float)
    
    print("⚙️ Engineering Recency, Frequency, Monetary (RFM-T) matrices...")
    # Summary function evaluates Recency, Frequency, and Monetary parameters using historical timestamps
    rfm_t = summary_data_from_transaction_data(
        df, 
        customer_id_col='customer_id', 
        datetime_col='transaction_timestamp', 
        monetary_value_col='total_revenue',
        observation_period_end=df['transaction_timestamp'].max()
    )
    
    # Filter out users with zero repeat purchases to stabilize Gamma-Gamma estimation logic
    modeling_df = rfm_t[rfm_t['frequency'] > 0]
    
    print("📈 Fitting Beta-Geometric (BG/NBD) Purchase Frequency Model...")
    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(modeling_df['frequency'], modeling_df['recency'], modeling_df['T'])
    
    # Predict expected transactions across a future quarterly horizon (90 days)
    modeling_df['predicted_purchases_90d'] = bgf.conditional_expected_number_of_purchases_up_to_time(
        90, modeling_df['frequency'], modeling_df['recency'], modeling_df['T']
    )
    
    print("💰 Fitting Gamma-Gamma Monetary Submodel...")
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(modeling_df['frequency'], modeling_df['monetary_value'])
    
    # Compute 12-Month Predictive Customer Lifetime Value
    modeling_df['predicted_12m_clv'] = ggf.customer_lifetime_value(
        bgf,
        modeling_df['frequency'],
        modeling_df['recency'],
        modeling_df['T'],
        modeling_df['monetary_value'],
        time=12, # 12 Months projections
        discount_rate=0.01 # Monthly discount factor adjustment
    )
    
    # Reset indices cleanly for deployment
    output_df = modeling_df.reset_index()[['customer_id', 'predicted_purchases_90d', 'predicted_12m_clv']]
    print(f"Processed CLV indices for {len(output_df)} recurring customers.")
    
    # Push back into BigQuery as an advanced analytics target
    table_ref = client.dataset("retail_media_analytics").table("customer_predictive_clv")
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE", autodetect=True)
    
    print("📤 Streaming predictive model computations to BigQuery storage layer...")
    client.load_table_from_dataframe(output_df, table_ref, job_config=job_config).result()
    print("🎉 Predictive CLV table successfully written to Cloud BigQuery warehouse!")

if __name__ == "__main__":
    calculate_predictive_clv()