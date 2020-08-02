from core import logger
from core.config import RlmaConfig

Config = RlmaConfig()
Config.run()

from gui.gui import RLMA

if __name__ == "__main__":
    a = RLMA()
    a.run()
