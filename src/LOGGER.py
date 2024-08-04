from logging import getLogger, basicConfig, DEBUG


def setup_logger(log_file: str) -> None:
    logger = getLogger(__name__)
    basicConfig(
        filename=log_file,
        filemode="w",
        format="[ %(asctime)s | %(levelname)s ] - %(module)s.py - %(message)s",
        datefmt="%H:%M:%S",
        level=DEBUG,
    )
    logger.info("Started Logger")
    return logger
