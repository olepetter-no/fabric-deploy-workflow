import logging
import sys

def setup_logging(verbose: bool = False) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO
    print("setup logging called")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True
    )

    for ns in ("azure", "urllib3"):
        logging.getLogger(ns).setLevel(logging.WARNING)