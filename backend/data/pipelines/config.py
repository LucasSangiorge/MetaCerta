import logging
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1]

BRONZE_DIR = DATA_DIR / "bronze" / "currency"
SILVER_FILE = DATA_DIR / "silver" / "currency" / "rates.parquet"
GOLD_DIR = DATA_DIR / "gold" / "currency"

PAIRS = [("USD", "BRL"), ("EUR", "BRL")]


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
