import logging

from rich.logging import RichHandler

FORMAT = logging.Formatter("%(funcName)s : %(message)s")
Logger = logging.getLogger("RLMA")
Logger.setLevel(logging.INFO)
Logger.addHandler(RichHandler())
Logger.handlers[0].setFormatter(FORMAT)
