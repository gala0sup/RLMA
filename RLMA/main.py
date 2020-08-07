from kivy.config import Config
from core import logger
from gui.gui import RLMA

Config.set("kivy", "log_level", "debug")

if __name__ == "__main__":
    a = RLMA()
    a.run()
