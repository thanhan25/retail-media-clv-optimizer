
# Retail Media E-Commerce Campaign & CLV Optimizer

An end-to-end cloud data analytics pipeline designed to ingest, segment, and model millions of transactional data rows to optimize retail ad inventory monetization strategies and project long-term customer value.

## 📊 Enterprise Business Intelligence Dashboard

The analytical processing layer is paired with a production-ready **Power BI Semantic Model** utilizing a rigid **Star Schema Design** to ensure optimal DAX performance, strict data protection boundaries, and boardroom-ready operational reporting.

*Note: The fully interactive compilation file can be reviewed or deployed natively via `reports/Retail_Media_Executive_Insights.pbix`.*

## 🛠️ Data Infrastructure Stack

* **Language Runtime:** Python 3.11 (Pandas Data Engineering, Lifetimes Statistical Modeling)
* **Database Infrastructure:** Google Cloud Platform (GCP), BigQuery Sandbox, & Relational SQL
* **Analytics Layer:** Standard ANSI SQL (Window Functions, NTILE distributions, View abstractions)
* **Business Intelligence Engine:** Power BI Desktop & Power BI Service (DAX, Semantic Data Modeling)

## 🏗️ Technical Pipeline Execution Architecture

### 1. Cloud Data Ingestion Pipeline (`scripts/upload_to_bigquery.py`)

Processes raw transactional lines to strip broken structural references, normalize multi-source formats, evaluate absolute line-item revenue matrices, and stream sanitized formats into relational data layers defensively.

### 2. RFM Segmentation Engine (`sql/rfm_segmentation.sql`)

Leverages SQL window functions and database indexing to calculate dynamic customer loyalty cohorts, enabling marketing and sales operations teams to identify and target high-value user clusters.

### 3. Predictive Customer Lifetime Value Pipeline (`scripts/clv_analytics.py`)

Implements a probabilistic **BG/NBD statistical model** to estimate multi-period repeat purchasing frequencies alongside a **Gamma-Gamma submodel** to project future economic value distributions over a rolling 12-month horizon.

### 4. Enterprise BI & Semantic Modeling (`reports/Retail_Media_Executive_Insights.pbix`)

Ingests processed Python statistical outputs into an optimized star schema framework to evaluate marketing campaign performance, calculating real-time Return on Ad Spend (ROAS) and Customer Acquisition Cost (CAC) margins.

## 📐 Relational Data Model (Star Schema)

To guarantee optimal DAX data-refresh speeds and simplify cross-functional query paths, the business intelligence layer completely decouples volatile transactional facts from dimension tables:

| **Table Asset**       | **Type** | **Keys / Relationships**                               | **Core Attributes**                                |
| --------------------------- | -------------- | ------------------------------------------------------------ | -------------------------------------------------------- |
| `Fact_Sales_Transactions` | Fact Table     | `transaction_id`(PK),`customer_key`(FK),`date_key`(FK) | Revenue, Quantity, Margin, Churn Risk Flags              |
| `Dim_Customers`           | Dimension      | `customer_key`(PK), 1:Many to Fact                         | Cohort ID, Acquisition Channel, Predicted Lifetime Value |
| `Dim_Calendar`            | Dimension      | `date_key`(PK), 1:Many to Fact (Time Intelligence)         | Date, Month, Quarter, Fiscal Year, Weekday               |

## 🧮 Advanced DAX Engineering Measures

The following optimized DAX measures are embedded natively within the semantic model to drive automated variance spotting and cohort analysis:

### A. Rolling 30-Day Predictive Customer Lifetime Value Revenue

Evaluates dynamic cash expansions by tracking multi-period transactions relative to statistical projections:

**Code snippet**

```
Rolling_30D_Revenue = 
CALCULATE(
    SUM(fact_sales_transactions[total_revenue]),
    DATESINPERIOD(
        dim_calendar[Date],
        LASTDATE(dim_calendar[Date]),
        -30,
        DAY
    )
)
```

### B. Customer Cohort Retention Variance

Flags customer retention deviations across historical baselines to proactively identify churn risks before they impact supply chain or operations pipelines:

**Code snippet**

```
Cohort_Retention_Variance_Pct = 
VAR ActiveCohortCount = COUNT(dim_customers[customer_id])
VAR TotalInitialSignups = CALCULATE(COUNT(dim_customers[customer_id]), ALLSELECTED(dim_customers))
VAR CurrentCohortRate = DIVIDE(ActiveCohortCount, TotalInitialSignups, 0)
VAR BaselineCohortRate = CALCULATE(DIVIDE(COUNT(dim_customers[customer_id]), TotalInitialSignups, 0), ALL(dim_customers))
RETURN
IF(
    ISBLANK(CurrentCohortRate), 
    0, 
    CurrentCohortRate - BaselineCohortRate
)
```

## 👁️ Executive Boardroom Canvas Features

The reporting environment features three functional reporting layouts tailored directly to cross-functional organizational stakeholders:

* **Sales Operations Canvas:** Real-time variance spotting across product lines, tracking active distribution channels and customer acquisition loops.
* **Logistics & Volume Analytics:** Anticipates downstream warehouse demands by connecting customer purchase velocity metrics to active inventory parameters.
* **Finance Control Dashboard:** Tracks capital efficiency metrics including realized profit margins, CAC boundaries, and net campaign ROAS performance.
