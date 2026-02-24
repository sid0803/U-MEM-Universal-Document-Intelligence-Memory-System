from pathlib import Path
from typing import List, Callable, Optional
import logging


logger = logging.getLogger(__name__)


def safe_cleanup(
    files: Optional[List[Path]] = None,
    callbacks: Optional[List[Callable]] = None,
) -> None:
    """
    Cleanup helper for rollback on failure.

    - Deletes provided files if they exist.
    - Executes optional rollback callbacks.
    - Never raises errors (safe rollback).
    """

    # -------------------------------
    # Delete files
    # -------------------------------
    if files:
        for f in files:
            try:
                if f and f.exists():
                    f.unlink()
            except Exception:
                logger.warning(
                    "Failed to delete file during cleanup: %s",
                    f,
                )

    # -------------------------------
    # Run callbacks
    # -------------------------------
    if callbacks:
        for cb in callbacks:
            try:
                if cb:
                    cb()
            except Exception:
                logger.warning(
                    "Cleanup callback failed: %s",
                    cb,
                )