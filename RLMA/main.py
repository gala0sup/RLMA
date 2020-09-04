from kivy.config import Config

from core.logger import Logger
from gui.gui import RLMA

logger = Logger().getLogger()

if __name__ == "__main__":
    a = RLMA()
    a.run()
