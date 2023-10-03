import logging


def init() -> None:
    """Initialize application logging."""
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.getLogger("app")
