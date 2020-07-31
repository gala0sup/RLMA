from os import environ
import pathlib
import logging

from kivy.utils import platform
from kivy.config import ConfigParser

from kivymd.toast import toast
from kivymd.uix.snackbar import Snackbar


log = logging.getLogger("RLMA")


class RlmaConfig(object):
    Config = ConfigParser(name="RLMA")

    def __init__(self):
        log.info(f"setting up config for RLMA")
        log.debug(f"Platform is {platform}")
        if platform == "win":
            self.base_path = pathlib.Path(environ["LOCALAPPDATA"]) / "RLMA"
            self.settings = {
                "LocationPaths": {
                    "BasePath": str(self.base_path),
                    "SettingsDir": str(self.base_path / ".settings"),
                    "LibraryPaths": [str(self.base_path / "Library")],
                },
                "Settings": {
                    "File": str(self.base_path / ".settings" / "settings.ini")
                },
            }

    def _setup(self):
        log.info(f"Setting up base dirs and files")
        try:
            for k, v in self.settings["LocationPaths"].items():
                log.debug(f"setting {k}")
                if k == "LibraryPaths":
                    for i in v:
                        pathlib.Path(i).mkdir(exist_ok=True)
                else:
                    pathlib.Path(v).mkdir(exist_ok=True)
            log.debug(f"Making settings file exist_ok=True")
            pathlib.Path(self.settings["Settings"]["File"]).touch(exist_ok=True)

        except Exception as error:
            log.critical(error)
            log.critical("Unable to complete Initial setup exiting....")
            raise

    def set_config(self):
        log.info(f"Settings defaults")
        log.debug(f"Config Parser name {RlmaConfig.Config.name}")
        RlmaConfig.Config.read(self.settings["Settings"]["File"])
        for k, v in self.settings.items():
            log.debug(f"setting {v} in section {k}")
            RlmaConfig.Config.setdefaults(str(k), v)

    def run(self):
        log.info("running RlmaConfig")
        self._setup()
        self.set_config()

    def add_library(self, path):
        try:
            if pathlib.Path(path).is_reserved():
                toast("error :- This is a reserved path")
            else:
                LibraryPathsList = self.settings["LocationPaths"]["LibraryPaths"]
                LibraryPathsList.append(path)
                RlmaConfig.Config.set("LocationPaths", "LibraryPaths", LibraryPathsList)
                RlmaConfig.Config.write()
        except Exception as error:
            Snackbar(
                text="Error in adding Library Path please choose different path",
                padding="20dp",
            )
            log.error(error)
