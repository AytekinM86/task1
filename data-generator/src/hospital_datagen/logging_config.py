"""Logging configuration.

Only the application entrypoint (the CLI) calls :func:`configure_logging`.
Library modules never touch handlers or call ``basicConfig`` — they simply do
``logger = logging.getLogger(__name__)`` and emit records, keeping the package
import-safe and testable.
"""

from __future__ import annotations

import logging
import sys

_LOG_FORMAT = "%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging(level: str = "INFO") -> None:
    """Configure a single stdout handler on the root logger (idempotent)."""
    numeric_level = logging.getLevelName(level.upper())
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    # Replace any previously installed handlers so repeated calls stay clean.
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(numeric_level)
