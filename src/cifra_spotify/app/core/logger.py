import os
import sys

from loguru import logger

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs")

# Normaliza o caminho
LOG_DIR = os.path.abspath(LOG_DIR)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Remove handlers anteriores para evitar duplicação
logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
)

logger.add(
    LOG_FILE,
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    level="INFO",
)

__all__ = ["logger"]
