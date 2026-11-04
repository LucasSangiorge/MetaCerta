import json
import logging
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pyarrow as pa

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1]
BRONZE_DIR = DATA_DIR / "bronze" / "currency"
SILVER_DIR = DATA_DIR / "silver" / "currency"
SILVER_FILE = SILVER_DIR / "rates.parquet"

RATE_TYPE = pd.ArrowDtype(pa.decimal128(18, 6))


def read_bronze() -> pd.DataFrame:
    frames = []
    for path in sorted(BRONZE_DIR.glob("*.json")):
        records = json.loads(path.read_bytes(), parse_float=Decimal)
        frame = pd.DataFrame(records)
        frame["extracted_at"] = path.stem.split("_")[-1]
        frames.append(frame)

    if not frames:
        raise FileNotFoundError(f"Nenhum arquivo no Bronze: {BRONZE_DIR}")

    df = pd.concat(frames, ignore_index=True)
    logger.info("Bronze %d arquivos, %d linhas", len(frames), len(df))
    return df


def to_silver(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"date": "rate_date"})

    df["base"] = df["base"].str.strip().str.upper()
    df["quote"] = df["quote"].str.strip().str.upper()
    df["rate_date"] = pd.to_datetime(df["rate_date"], errors="coerce").dt.date
    df["extracted_at"] = pd.to_datetime(df["extracted_at"], format="%Y%m%dT%H%M%SZ", utc=True)

    total = len(df)
    df = df.dropna(subset=["base", "quote", "rate_date", "rate"])
    df = df[df["rate"] > 0]
    logger.info("Silver: %d linhas inválidas removidas", total - len(df))

    df["rate"] = df["rate"].astype(RATE_TYPE)

    before = len(df)
    df = (
        df.sort_values("extracted_at")
        .drop_duplicates(subset=["base", "quote", "rate_date"], keep="last")
        .sort_values(["base", "quote", "rate_date"])
        .reset_index(drop=True)
    )
    logger.info("Silver: %d duplicatas removidas", before - len(df))

    return df[["base", "quote", "rate_date", "rate", "extracted_at"]]


def save_silver(df: pd.DataFrame) -> Path:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SILVER_FILE, index=False)
    logger.info("Silver: %s (%d linhas)", SILVER_FILE.name, len(df))
    return SILVER_FILE


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    save_silver(to_silver(read_bronze()))
