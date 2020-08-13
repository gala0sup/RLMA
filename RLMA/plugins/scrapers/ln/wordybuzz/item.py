import logging
from math import ceil
from pathlib import Path
import json
import traceback

from kivymd.uix.snackbar import Snackbar

from plugins.scrapers.base.item import Base

logger = logging.getLogger("RLMA")


class Scraper(Base):
    def __init__(self, link=None, wait=False, _log_level=1, LibraryItemInstance=None):
        super().__init__(
            link=link,
            wait=wait,
            _log_level=_log_level,
            LibraryItemInstance=LibraryItemInstance,
        )
        self.type_ = Path(__file__).parent.parts[-2]
        self.websitename = Path(__file__).parent.parts[-1]

    def _set_info(self):
        try:
            dicts = self.prased_webpage.find_all("script", type="application/ld+json")

            JSON = None
            for dict_ in dicts:
                try:
                    try:
                        JSON = json.loads(dict_.string)
                    except:
                        pass
                    # logger.debug(JSON["@type"] == "WebPage")
                    if JSON["@type"] == "WebPage":
                        for k, v in JSON.items():
                            if k == "mainEntity":
                                for key, value in v.items():
                                    if key == "author":
                                        if len(value):
                                            self.about["Author"] = value[0]["name"]
                                    elif key == "image":
                                        self.about["CoverImage"] = value
                                    elif key == "name":
                                        self.about["Name"] = value
                                    elif key == "numberOfPages":
                                        self.about["Chapters"] = int(value)
                                    elif key == "description":
                                        self.about["extra"] = value
                        break
                    else:
                        pass
                except:
                    raise
            div = self.prased_webpage.find("div", class_="summary text-muted").find_all(
                "p"
            )
            for p in div:
                if len(p.get_text()):
                    self.about["Summary"] += p.get_text()
            self.LibraryItemInstance.item_set_info()
        except Exception as error:
            logger.error(error)
            logger.debug("Scraper outdated")
            Snackbar(
                text="Scraper outdated please wait for Update..", duration=3
            ).show()
            print(traceback.format_exc())
