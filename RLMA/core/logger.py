import logging
from rich.logging import RichHandler


class Logger:
    def __init__(self):
        self.format = logging.Formatter("%(funcName)s : %(message)s")
        self.level = logging.DEBUG

        self.logger = logging.getLogger("RLMA")
        self.logger.setLevel(self.level)
        self.logger.addHandler(RichHandler())
        self.logger.handlers[0].setFormatter(self.format)

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

