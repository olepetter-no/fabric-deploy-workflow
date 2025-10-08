"""
Simple logging configuration
"""

import logging
import sys


def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    """
    Set up basic logging configuration

    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Optional log file path (unused - keeping for CLI compatibility)
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # Reduce noise from Azure libraries
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
