import logging
from math import ceil
from pathlib import Path

from kivymd.uix.snackbar import Snackbar

from plugins.scrapers.base.item import Base


WEBSITE = Path(__file__).parent.parts[-1]

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
        self.websitename = WEBSITE

    def _set_info(self):

        try:
            self.about[
                "CoverImage"
            ] = f"https://www.{WEBSITE}.com{self.prased_webpage.find_all('figure',class_='cover')[0].find('img')['data-src']}"
            self.about["Name"] = self.prased_webpage.find_all(
                "h1", class_="novel-title text2row"
            )[0].text.strip()
            self.about["Chapters"] = int(
                self.prased_webpage.find_all("span", class_="chapter-count")[0]
                .text.strip()
                .split(" ")[0]
            )

            wrapper = self.prased_webpage.find_all("div", class_="wrapper")
            for s in wrapper:
                divs = s.find_all("div", class_="inline")
                if len(divs):

                    for div in divs:
                        item = div.find("span").get_text().lower()
                        if "author" in item:
                            self.about["Author"] = (
                                div.find("strong").find("a").string.strip()
                            )
                            logger.debug(self.about["Author"])

                        elif "status" in item:
                            self.about["Status"] = div.find("strong").string.strip()
                            logger.debug(self.about["Status"])

                        elif "release" in item:
                            self.about["Release"] = div.find("strong").string.strip()
                            logger.debug(self.about["Release"])

                        elif "update" in item:
                            self.about["Updated"] = div.find("strong").string.strip()
                            logger.debug(self.about["Updated"])
            div = (
                self.prased_webpage.find_all("div", class_="summary")[0]
                .find_all(class_="content")[0]
                .find_all("p")
            )
            for p in div:
                summary = ""
                summary += p.get_text()
                if self._log_level < 1:
                    logger.debug(f"{summary}")
            if len(summary) > 1:
                self.about["Summary"] = summary

            self.LibraryItemInstance.item_set_info()

        except Exception as error:
            logger.error(error)
            raise

    def _get_chapter(self):
        super()._get_chapter()
        content = []
        div = self.prased_webpage.find(class_="chapter-content").find_all("p")
        for p in div:
            content.append(p.string)
        return content

    def _set_chapter_list(self):
        li = self.prased_webpage.find("ul", class_="chapter-list").find_all("li")

        for a in li:
            self.chapter_list[int(a["data-volumeno"])] = {
                f"{a.find('a')['title']}": f"https://www.{WEBSITE}.com{a.find('a')['href']}"
            }

        pagination = self.prased_webpage.find("ul", class_="pagination").find_all("li")[
            1:-1
        ]

        link_copy = self.link

        for li in pagination:
            a = li.find("a")
            self.link = f"https://www.{WEBSITE}.com{a['href']}"
            self._get_webpage(wait=True)
            li = self.prased_webpage.find("ul", class_="chapter-list").find_all("li")

            for a in li:
                self.chapter_list[int(a["data-volumeno"])] = {
                    f"{a.find('a')['title']}": f"https://www.{WEBSITE}.com{a.find('a')['href']}"
                }
        self.link = link_copy
