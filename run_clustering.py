"""
CLI utility for manual/offline clustering.

This file is NOT used by FastAPI.
It runs clustering for a specific user.

Usage:
    python run_clustering.py <user_id>
"""

import sys
import logging
import argparse

from app.core.logging_config import setup_logging
from app.services.topic_clustering import run_topic_clustering
from app.services.cluster_labeler import label_clusters


# --------------------------------------------------
# Setup Logging (use centralized config)
# --------------------------------------------------
setup_logging()
logger = logging.getLogger(__name__)


def run_clustering_pipeline(user_id: str) -> int:
    """
    Runs full clustering pipeline for a user.
    Returns exit code.
    """
    user_id = (user_id or "").strip()

    if not user_id:
        logger.error("Invalid user_id provided")
        return 1

    try:
        logger.info("Starting clustering pipeline | user_id=%s", user_id)

        clusters = run_topic_clustering(user_id=user_id)

        if clusters is None:
            logger.error("Clustering returned None | user_id=%s", user_id)
            return 1

        if not clusters:
            logger.warning("No clusters created | user_id=%s", user_id)

        logger.info("Labeling clusters | user_id=%s", user_id)
        label_clusters(user_id=user_id)

        logger.info("Clustering completed successfully | user_id=%s", user_id)
        return 0

    except Exception:
        logger.exception("Clustering pipeline failed | user_id=%s", user_id)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Run clustering for a specific user"
    )

    parser.add_argument(
        "user_id",
        type=str,
        help="User ID for which clustering should be executed",
    )

    args = parser.parse_args()

    exit_code = run_clustering_pipeline(args.user_id)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
