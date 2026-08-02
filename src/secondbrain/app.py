import os
import sys
from pathlib import Path

from loguru import logger

from secondbrain.notes import notes_dir

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level.icon}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

LEVEL_ICONS = {
    "TRACE": "T",
    "DEBUG": "D",
    "INFO": "I",
    "SUCCESS": "S",
    "WARNING": "W",
    "ERROR": "E",
    "CRITICAL": "C",
}


def configure_logging():
    """Configure loguru for console and file logging.

    Removes the default handler and sets up:
    - stderr handler at LOG_LEVEL (default: INFO, configurable via env var)
    - File handler at DEBUG level writing to LOG_FILE (default:
      `app.log` inside the notes directory, *not* the current directory --
      the CLI can be run from anywhere, including read-only locations)

    If the log file cannot be opened, console logging still works and the
    command continues; logging must never be the reason a command fails.

    Both handlers share `LOG_FORMAT`, a compact pipe-delimited line with
    second-precision timestamps and a single-letter level code drawn from
    `LEVEL_ICONS` (T, D, I, S, W, E, C):

    ```
    2026-08-01 20:56:47 | I | secondbrain.app:main:29 | Hello from secondbrain!
    ```
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    log_file = Path(os.environ.get("LOG_FILE") or notes_dir() / "app.log").expanduser()
    for name, icon in LEVEL_ICONS.items():
        logger.level(name, icon=icon)
    logger.remove()
    logger.add(sys.stderr, level=log_level, format=LOG_FORMAT)
    try:
        logger.add(
            log_file, level="DEBUG", rotation="50 KB", retention=1, format=LOG_FORMAT
        )
    except OSError as exc:
        logger.warning("File logging disabled ({}): {}", log_file, exc)


@logger.catch
def main():
    """Run the application.

    Configures logging and prints a greeting to verify the setup works.
    """
    configure_logging()
    logger.info("Hello from secondbrain!")
