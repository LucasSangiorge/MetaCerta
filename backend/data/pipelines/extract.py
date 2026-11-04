import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx

from app.core.config import settings
from data.pipelines.config import BRONZE_DIR, PAIRS, setup_logging


logger = logging.getLogger(__name__)


def extract_rates(base: str, quote: str, start: date, end: date) -> Path:
    response = httpx.get(
        f"{settings.EXCHANGE_API_URL}/rates",
        params={
            "base": base,
            "quotes": quote,
            "from": start.isoformat(),
            "to": end.isoformat(),
        },
        timeout=settings.EXCHANGE_API_TIMEOUT,
    )
    response.raise_for_status()

    extracted_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    file_name = f"{base}_{quote}_{start}_{end}_{extracted_at}.json"
    path = BRONZE_DIR / file_name

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)

    logger.info("Bronze: %s (%d bytes)", path.name, len(response.content))

    return path


def run(days: int = 365) -> list[Path]:
    end = date.today()
    start = end - timedelta(days=days)
    return [extract_rates(base, quote, start, end) for base, quote in PAIRS]


if __name__ == "__main__":
    setup_logging()
    run()
