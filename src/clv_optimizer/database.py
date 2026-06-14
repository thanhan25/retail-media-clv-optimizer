import logging
import sqlite3
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
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
            conn.commit()
        except sqlite3.Error as sql_err:
            if conn:
                conn.rollback()
            raise DataLakeExtractionError(f"Data storage ingestion failure: {sql_err}")
        finally:
            if conn:
                conn.close()


db_manager = DatabaseConnectionManager(db_path=str(settings.DB_PATH))
