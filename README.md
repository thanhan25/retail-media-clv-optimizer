# Retail Media E-Commerce Campaign & CLV Optimizer

An end-to-end cloud data analytics pipeline designed to ingest, segment, and model millions of transactional data rows to optimize retail ad inventory monetization strategies.

## 📊 Executive Analytics Dashboard

Click the dashboard image below to interact with the live, fully functional report in Looker Studio!

[![https://datastudio.google.com/reporting/65582cb0-b14a-49f3-ba38-d774935feb10](dashboard-preview.png)](PASTE_YOUR_PUBLIC_LOOKER_STUDIO_SHARE_LINK_HERE)

> 📊 **[Access the Live Interactive Looker Studio Campaign Dashboard](https://datastudio.google.com/reporting/65582cb0-b14a-49f3-ba38-d774935feb10)**

## 🛠️ Data Infrastructure Stack

* **Language Runtime:** Python 3.11 (Pandas Data Engineering, Lifetimes Statistical Modeling Package)
* **Cloud Infrastructure Warehouse:** Google Cloud Platform (GCP) & BigQuery Sandbox environments
* **Analytics Layer:** Standard ANSI SQL (Window Functions, NTILE distributions, View abstractions)
* **Business Intelligence Engine:** Looker Studio enterprise performance reporting tools

## 🏗️ Technical Pipeline Execution Architecture

1. **Cloud Data Ingestion Pipeline (`scripts/upload_to_bigquery.py`)**

   * Processes transactional lines to strip broken structural references, normalize data structures, evaluate absolute line-item revenue matrices, and stream sanitized formats into remote GCP environments.
2. **RFM Segmentation Engine (`sql/rfm_segmentation.sql`)**

   * Uses SQL window functions to calculate dynamic customer loyalty tiers, allowing the Ad Operations and Sales teams to identify high-value audiences.
3. **Predictive Customer Lifetime Value Pipeline (`scripts/clv_analytics.py`)**

   * Implements a **BG/NBD statistical model** to estimate multi-period repeat purchasing patterns alongside a **Gamma-Gamma submodel** to project future economic value over a rolling 12-month horizon.
4. **Marketing Campaign Attribution Optimization (`Looker Studio Visualization`)**

   * Integrates customer segments with campaign spend to calculate **Return on Ad Spend (ROAS)** and **Customer Acquisition Cost (CAC)**, driving better monetization choices for retail networks.
