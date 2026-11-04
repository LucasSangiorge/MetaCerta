import logging
import sys
import time

from data.pipelines import extract, load, transform
from data.pipelines.config import setup_logging


logger = logging.getLogger(__name__)

STEPS = [
    ("extract", extract.run),
    ("transform", transform.run),
    ("load", load.run),
]


def run_pipeline() -> None:
    for name, step in STEPS:
        logger.info("Etapa %s: iniciada", name)
        start = time.perf_counter()
        try:
            step()
        except Exception:
            logger.exception("Etapa %s falhou. Etapas seguintes canceladas.", name)
            raise
        logger.info("Etapa %s: concluída em %.1fs", name, time.perf_counter() - start)

    logger.info("Pipeline concluído: Bronze, Silver e Gold atualizadas")


if __name__ == "__main__":
    setup_logging()
    try:
        run_pipeline()
    except Exception:
        sys.exit(1)
