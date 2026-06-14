import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator
from clv_optimizer.config import settings
from clv_optimizer.exceptions import DataLakeExtractionError

logger = logging.getLogger("clv_optimizer.database")

class DatabaseConnectionManager:
    """Enforces reliable connection states using strict isolation context loops."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def execution_session(self) -> Generator[sqlite3.Connection, None, None]:
        """Provides a safe database connection environment with automated transaction rollback blocks."""
        settings.validate_environment()
        conn = None
        try:
            logger.debug(f"Opening transactional storage session at: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            # Enforce foreign key constraints inside SQLite sessions
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except sqlite3.Error as sql_err:
            if conn:
                logger.warning("Active execution exception encountered. Rolling back storage modifications.")
                conn.rollback()
            raise DataLakeExtractionError(
                f"Data storage ingestion failure: Underneath driver raised an error. Details: {sql_err}"
            )
        finally:
            if conn:
                conn.close()
                logger.debug("Transactional storage session successfully terminated.")

# Create the primary package database client instance
db_manager = DatabaseConnectionManager(db_path=str(settings.DB_PATH))