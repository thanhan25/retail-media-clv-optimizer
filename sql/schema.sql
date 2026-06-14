-- Enforce database structural validation constraints
PRAGMA foreign_keys = ON;

-- Create transactional ledger with defensive safety guards
CREATE TABLE IF NOT EXISTS transactions (
    customer_id TEXT NOT NULL,
    frequency INTEGER NOT NULL CHECK(frequency >= 0),
    recency REAL NOT NULL CHECK(recency >= 0.0),
    T INTEGER NOT NULL CHECK(T > 0),
    cohort TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id, cohort)
);

-- Optimize analytics query lookup arrays for performance
CREATE INDEX IF NOT EXISTS idx_transactions_cohort 
ON transactions(cohort);