-- RFM Analysis for Inventory Monetization Strategy
CREATE OR REPLACE TABLE `sharp-avatar-297916.retail_media_analytics.customer_rfm_segments` AS 
WITH base_metrics AS (
  SELECT
    customer_id,
    -- Recency: Days elapsed from maximum transaction date to the final date in dataset
    DATE_DIFF(
      (SELECT MAX(EXTRACT(DATE FROM TIMESTAMP(transaction_timestamp))) FROM `sharp-avatar-297916.retail_media_analytics.transaction_records`), 
      MAX(EXTRACT(DATE FROM TIMESTAMP(transaction_timestamp))), 
      DAY
    ) AS recency,
    -- Frequency: Number of unique purchase invoices
    COUNT(DISTINCT invoice_id) AS frequency,
    -- Monetary: Combined gross dollar allocation volume
    SUM(total_revenue) AS monetary
  FROM `sharp-avatar-297916.retail_media_analytics.transaction_records`
  GROUP BY customer_id
),

rfm_scores AS (
  SELECT 
    *,
    -- Dynamic NTILE distribution tiers (1-5 point scales)
    NTILE(5) OVER (ORDER BY recency DESC) AS r_score, -- Lower recency days = higher score
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
  FROM base_metrics
)

SELECT
  customer_id,
  recency,
  frequency,
  monetary,
  r_score,
  f_score,
  m_score,
  (r_score + f_score + m_score) AS combined_score,
  CASE
    WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Core Champions (High Ad Value)'
    WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customer Ingestions'
    WHEN r_score >= 4 AND f_score = 1 THEN 'New Target Captures'
    WHEN r_score <= 2 AND f_score >= 3 THEN 'At-Risk Volume (Offer Ad Incentives)'
    ELSE 'Hibernating / Dormant Profile'
  END AS customer_segment
FROM rfm_scores;