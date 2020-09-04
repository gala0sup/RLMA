import logging


class Logger:
    def __init__(self):
        self.format = logging.Formatter(
            f"%(levelname)s :   %(funcName)s   : %(message)s"
        )
        self.level = logging.DEBUG

        self.logger = logging.getLogger("RLMA")
        self.logger.setLevel(self.level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel = self.logger.level
        console_handler.setFormatter(self.format)

        self.logger.addHandler(console_handler)
        self.info("logger setup done")

    def getLogger(self):
        """returns logger instance"""
        return self.logger

    def info(self, message) -> None:
        self.logger.info(message)

    def debug(self, message) -> None:
        self.logger.debug(message)

    def warning(self, message) -> None:
        self.logger.warning(message)

    def critical(self, message) -> None:
        self.logger.critical(message)

    def setLevel(self, level: int):
        self.logger.setLevel(level)

