import csv
import logging
import sys
from pathlib import Path

from clv_optimizer.database import db_manager
from clv_optimizer.exceptions import DataLakeExtractionError

# Configure structured runtime telemetry logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("clv_optimizer.ingestion")


def initialize_database_schema(schema_path: Path) -> None:
    """Reads and executes the relational migration blueprint defensively."""
    logger.info(f"Loading database layout migrations from: {schema_path}")
    try:
        with open(schema_path, "r") as f:
            schema_script = f.read()

        with db_manager.execution_session() as conn:
            conn.executescript(schema_script)
        logger.info("Database schema migration successfully synchronized.")
    except Exception as err:
        raise DataLakeExtractionError(f"Database layout setup aborted: {err}")


def ingest_transactional_csv(csv_path: Path) -> None:
    """Parses raw source csv records and writes them to the data lake context."""
    logger.info(f"Parsing transactional data records from: {csv_path}")
    if not csv_path.exists():
        raise DataLakeExtractionError(f"Ingestion source target missing: '{csv_path}'")

    insert_query = """
        INSERT OR REPLACE INTO transactions (customer_id, frequency, recency, T, cohort)
        VALUES (?, ?, ?, ?, ?);
    """

    try:
        records = []
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(
                    (row["customer_id"], int(row["frequency"]), float(row["recency"]), int(row["T"]), row["cohort"])
                )

        with db_manager.execution_session() as conn:
            conn.executemany(insert_query, records)
        logger.info(f"Successfully processed and stored {len(records)} transaction vectors.")

    except Exception as err:
        raise DataLakeExtractionError(f"Data ingestion pipeline execution failed: {err}")


if __name__ == "__main__":
    WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

    # 1. Run database structure initializations
    schema_file = WORKSPACE_ROOT / "sql" / "schema.sql"
    initialize_database_schema(schema_file)

    # 2. Check if mock data is available for test hydration
    mock_data = WORKSPACE_ROOT / "data" / "mock_transactions.csv"
    if mock_data.exists():
        ingest_transactional_csv(mock_data)
    else:
        logger.warning(f"Skipping CSV load step: '{mock_data}' file not found.")
