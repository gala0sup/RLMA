import logging
from math import ceil
from pathlib import Path


from plugins.scrapers.ln.base.item import Base


WEBSITE = Path(__file__).parent.parts[-1]

logger = logging.getLogger("RLMA")


class Scraper(Base):
    def __init__(self, link=None, wait=False):
        super().__init__(link=link, wait=wait)

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
                        if "author" in div.find("span").string.lower():
                            self.about["Author"] = (
                                div.find("strong").find("a").string.strip()
                            )

                        if "status" in div.find("span").string.lower():
                            self.about["Status"] = div.find("strong").string.strip()

                        if "release" in div.find("span").string.lower():
                            self.about["Release"] = div.find("strong").string.strip()

                        if "update" in div.find("span").string.lower():
                            self.about["Updated"] = div.find("strong").string.strip()
            div = (
                self.prased_webpage.find_all("div", class_="summary")[0]
                .find_all(class_="content")[0]
                .find_all("p")
            )
            for p in div:
                if len(p.string) > 1:
                    self.about["Summary"] = p.string.strip()
            cur = self.about["Chapters"]

            li = (
                self.prased_webpage.find("section", id="chapter")
                .find("ul", class_="chapter-list")
                .find_all("li")
            )
            for a in li:
                self.chapter_list[cur] = {
                    f"{a.find('a')['title']}": f"https://www.{WEBSITE}.com{a.find('a')['href']}"
                }
                cur -= 1

            link_copy = self.link
            pagination = (
                self.prased_webpage.find("section", id="chapter")
                .find_all("div", class_="pagination-container")[0]
                .find_all("a")[0:-1]
            )

            for a in pagination:
                self.link = f"https://www.{WEBSITE}.com{a['href']}"
                self._get_webpage()
                li = (
                    self.prased_webpage.find("section", id="chapter")
                    .find("ul", class_="chapter-list")
                    .find_all("li")
                )

                for a in li:
                    self.chapter_list[cur] = {
                        f"{a.find('a')['title']}": f"https://www.{WEBSITE}.com{a.find('a')['href']}"
                    }
                    cur -= 1
            self.link = link_copy
            # logging.debug("%s ------- %s",len(a),a)
            # logging.debug("%s ------- %s",len(a),a)
        except Exception as error:
            logger.error(error)

    def _get_chapter(self):
        super()._get_chapter()
        content = []
        div = self.prased_webpage.find(class_="chapter-content").find_all("p")
        for p in div:
            content.append(p.string)
        return content
