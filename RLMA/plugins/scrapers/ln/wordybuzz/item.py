import logging
from math import ceil
from pathlib import Path
import json

from plugins.scrapers.base.item import Base
from bs4 import Tag

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
                                        self.about["CoverImage"] = value.strip()
                                    elif key == "name":
                                        self.about["Name"] = value.strip()
                                    elif key == "numberOfPages":
                                        self.about["Chapters"] = int(value.strip())
                                    elif key == "description":
                                        self.about["extra"] = value.strip()
                        break
                    else:
                        pass
                except:
                    raise
            div = self.prased_webpage.find("div", class_="summary text-muted").find_all(
                "p"
            )
            summary = ""
            for p in div:
                if len(p.get_text()):
                    summary += p.get_text()

            self.about["Summary"] = summary

            trs = self.prased_webpage.find(
                "table", class_="table table-bordered"
            ).find_all("tr")
            for tr in trs:
                if tr.find("th").get_text().lower() == "status":
                    self.about["Status"] = tr.find("td").find("a").get_text()

            self.LibraryItemInstance.item_set_info()
        except Exception as error:
            logger.error(error)
            logger.debug("Scraper outdated")
            raise

        def _set_chapter_list(self):
            try:
                chapter_list_div = self.prased_webpage.find("div", class_="row pt-2")
                for chapter_div in chapter_list_div:
                    if isinstance(chapter_div, Tag):
                        chapter_number = chapter_div.find("span").get_text()
                        chapter_link = chapter_div.find("a")["href"]
                        chapter_name = chapter_div.find("a").get_text()
                        self.chapter_list[int(chapter_number)] = {
                            chapter_name: chapter_link
                        }
            except:
                logger.error(error)
                logger.debug("Scraper outdated")
                raise
