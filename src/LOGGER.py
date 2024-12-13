from logging import DEBUG, Logger, basicConfig, getLogger


def setup_logger(log_file: str) -> Logger:
    logger = getLogger(__name__)
    basicConfig(
        filename=log_file,
        filemode="w",
        format="[ %(asctime)s | %(levelname)s ] - %(module)s.py - line %(lineno)d - %(message)s",
        datefmt="%H:%M:%S",
        level=DEBUG,
    )
    logger.info("Started Logger")
    return logger
