import logging
from pathlib import Path

import pandas as pd

from data.pipelines.config import GOLD_DIR, SILVER_FILE, setup_logging


logger = logging.getLogger(__name__)

DAILY_FILE = GOLD_DIR / "daily.parquet"
MONTHLY_FILE = GOLD_DIR / "monthly.parquet"

PAIR = ["base", "quote"]


def read_silver() -> pd.DataFrame:
    df = pd.read_parquet(SILVER_FILE, dtype_backend="pyarrow")
    logger.info("Silver: %d linhas lidas", len(df))
    return df


def build_daily(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values([*PAIR, "rate_date"]).reset_index(drop=True)
    rate = df["rate"].astype("float64")
    by_pair = rate.groupby([df["base"], df["quote"]])

    df["change_pct"] = (by_pair.pct_change() * 100).round(4)
    df["moving_avg_30d"] = by_pair.transform(
        lambda serie: serie.rolling(30, min_periods=1).mean()
    ).round(6)

    return df[[*PAIR, "rate_date", "rate", "change_pct", "moving_avg_30d"]]


def build_monthly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(
        month=df["rate_date"].map(lambda day: day.replace(day=1)),
        rate_float=df["rate"].astype("float64"),
    )
    monthly = (
        df.sort_values("rate_date")
        .groupby([*PAIR, "month"], as_index=False)
        .agg(
            avg_rate=("rate_float", "mean"),
            min_rate=("rate", "min"),
            max_rate=("rate", "max"),
            close_rate=("rate", "last"),
            days=("rate", "size"),
        )
    )
    monthly["avg_rate"] = monthly["avg_rate"].round(6)

    close = monthly["close_rate"].astype("float64")
    by_pair = close.groupby([monthly["base"], monthly["quote"]])
    monthly["change_pct"] = (by_pair.pct_change() * 100).round(4)

    return monthly


def save_gold(daily: pd.DataFrame, monthly: pd.DataFrame) -> list[Path]:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    daily.to_parquet(DAILY_FILE, index=False)
    monthly.to_parquet(MONTHLY_FILE, index=False)
    logger.info(
        "Gold: %s (%d linhas), %s (%d linhas)",
        DAILY_FILE.name,
        len(daily),
        MONTHLY_FILE.name,
        len(monthly),
    )
    return [DAILY_FILE, MONTHLY_FILE]


def run() -> list[Path]:
    silver = read_silver()
    return save_gold(build_daily(silver), build_monthly(silver))


if __name__ == "__main__":
    setup_logging()
    run()
