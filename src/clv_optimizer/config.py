import os
from pathlib import Path

from dotenv import load_dotenv

from clv_optimizer.exceptions import DataLakeExtractionError

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


class PipelineSettings:
    """Central configuration vault parsing and validating critical runtime parameters."""

    def __init__(self):
        self.ENVIRONMENT: str = os.getenv("PIPELINE_ENV", "development").lower()
        self.DB_PATH: Path = BASE_DIR / os.getenv("DATABASE_PATH", "data/retail_transactions.db")

        try:
            self.MIN_RECENCY_DAYS: float = float(os.getenv("MIN_RECENCY_DAYS", "0.0"))
        except ValueError as err:
            raise DataLakeExtractionError(f"Configuration parsing failed: {err}")

    def validate_environment(self) -> None:
        """Verifies operational directories are ready before calculations fire."""
        if not self.DB_PATH.parent.exists():
            raise DataLakeExtractionError(f"Operational directory missing: '{self.DB_PATH.parent}'")


settings = PipelineSettings()
