import logging
import sys


def setup_logging(verbose: bool = False) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,  # Required since fabric-cicd library modifies global logging config
    )

    for ns in ("azure", "urllib3"):
        logging.getLogger(ns).setLevel(logging.WARNING)
