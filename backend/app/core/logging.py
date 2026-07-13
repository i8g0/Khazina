import logging
import sys

from app.core.config import settings
from app.core.logging_filters import SensitiveDataFilter

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_root_logger(level: int) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(SensitiveDataFilter())
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[handler],
        force=True,
    )


def setup_logging() -> None:
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    configure_root_logger(log_level)
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("uvicorn.error").addFilter(SensitiveDataFilter())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
