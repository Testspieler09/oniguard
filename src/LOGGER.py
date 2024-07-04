import logging

class Logger:
    def __init__(self, log_file) -> None:
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename=log_file,
                            filemode="w",
                            format="[ %(asctime)s | %(levelname)s ] %(message)s",
                            datefmt="%H:%M:%S",
                            level=logging.DEBUG)
        logging.info("Started Logger")

    @staticmethod
    def debug(message: str) -> None:
        logging.debug(message)

    @staticmethod
    def info(message: str) -> None:
        logging.info(message)

    @staticmethod
    def warning(message: str) -> None:
        logging.warning(message)

    @staticmethod
    def error(message: str) -> None:
        logging.error(message)

    @staticmethod
    def critical(message: str) -> None:
        logging.critical(message)

if __name__ == "__main__":
    logger = Logger("logfile.log")
    logger.debug("hello")
    logger.info("hello")
    logger.warning("hello")
    logger.error("hello")
    logger.critical("hello")
