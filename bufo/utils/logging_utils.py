import logging


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Creates and returns a logger with standardized formatting
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s [%(levelname)s] %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    return logger
