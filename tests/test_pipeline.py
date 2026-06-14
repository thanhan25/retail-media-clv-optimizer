import os
import sqlite3

import pytest

from clv_optimizer.config import BASE_DIR, PipelineSettings
from clv_optimizer.database import DatabaseConnectionManager
from clv_optimizer.exceptions import DataLakeExtractionError, ModelFittingInversionError
from clv_optimizer.pipeline import RetailMediaCLVEngine


# ==============================================================================
# 🎯 SECTION 1: CORE CALCULATION ASSERTERS
# ==============================================================================
def test_successful_transaction_projection():
    engine = RetailMediaCLVEngine(target_cohort="q1_retail_media")
    projections = engine.compute_expected_transactions(frequency=4, recency=12.5, t=30)
    assert projections == 8.8889


def test_invalid_cohort_initialization():
    with pytest.raises(DataLakeExtractionError, match="Target cohort indicator cannot be null"):
        RetailMediaCLVEngine(target_cohort="   ")


def test_negative_variance_divergence():
    engine = RetailMediaCLVEngine(target_cohort="valid_test_frame")
    with pytest.raises(ModelFittingInversionError, match="Mathematical optimization failed"):
        engine.compute_expected_transactions(frequency=-2, recency=10.0, t=30)


# ==============================================================================
# 🎯 SECTION 2: CONFIGURATION ENVIRONMENT VALIDATION TESTS
# ==============================================================================
def test_configuration_value_error(monkeypatch):
    """Triggers and validates numerical setting parser handling anomalies."""
    monkeypatch.setenv("MIN_RECENCY_DAYS", "corrupted_string_value")
    with pytest.raises(DataLakeExtractionError, match="Configuration parsing failed"):
        PipelineSettings()


def test_configuration_invalid_directory():
    """Forces path tracking checks to flag missing operational environments."""
    test_settings = PipelineSettings()
    test_settings.DB_PATH = BASE_DIR / "non_existent_directory_mock_path/records.db"
    with pytest.raises(DataLakeExtractionError, match="Operational directory missing"):
        test_settings.validate_environment()


# ==============================================================================
# 🎯 SECTION 3: DATABASE CONTEXT & DATA LAKE INTEGRATION TESTS
# ==============================================================================
@pytest.fixture
def setup_mock_db(tmp_path):
    """Builds a temporary sandboxed file database to preserve rows across sessions."""
    db_file = tmp_path / "test_retail_transactions.db"
    test_mgr = DatabaseConnectionManager(db_path=str(db_file))
    with test_mgr.execution_session() as conn:
        conn.execute(
            """
            CREATE TABLE transactions (
                customer_id TEXT,
                frequency INTEGER,
                recency REAL,
                T INTEGER,
                cohort TEXT
            );
        """
        )
        conn.execute("INSERT INTO transactions VALUES ('C101', 5, 14.2, 365, 'retail_2026');")
    return test_mgr


def test_load_historical_metrics_success(setup_mock_db, monkeypatch):
    """Verifies data ingestion records can be securely queried and loaded."""
    monkeypatch.setattr("clv_optimizer.pipeline.db_manager", setup_mock_db)

    engine = RetailMediaCLVEngine(target_cohort="retail_2026")
    records = engine.load_historical_metrics()

    assert len(records) == 1
    assert records[0] == ("C101", 5, 14.2, 365)


def test_database_execution_failure_handling(setup_mock_db, monkeypatch):
    """Validates that internal driver query issues throw managed pipeline errors."""
    monkeypatch.setattr("clv_optimizer.pipeline.db_manager", setup_mock_db)
    engine = RetailMediaCLVEngine(target_cohort="retail_2026")

    # Securely drop the table now that it persistently exists in our sandbox file
    with setup_mock_db.execution_session() as conn:
        conn.execute("DROP TABLE transactions;")

    with pytest.raises(DataLakeExtractionError, match="Failed to extract customer tracking rows"):
        engine.load_historical_metrics()


def test_database_driver_exception_rollback():
    """Enforces transaction rollbacks when lower driver connections fail boundaries."""
    bad_mgr = DatabaseConnectionManager(db_path="/invalid_system_path_xyz/unwriteable.db")
    with pytest.raises(DataLakeExtractionError, match="Data storage ingestion failure"):
        with bad_mgr.execution_session():
            pass
