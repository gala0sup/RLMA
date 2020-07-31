import importlib
import logging
import tldextract as tld

log = logging.getLogger("RLMA")


class Scraper:
    def __init__(self, link, type_, wait):
        log.debug(f"got values {link} , {type_} , {wait}")
        self.link = link
        self.wait = wait
        if type_ not in ["ln", "manga", "anime"]:
            raise ValueError(f"Invalid type_ value {type_}")
        self.type_ = type_
        try:
            self.websitename = tld.extract(link).domain.lower()
            log.debug(f"website name {self.websitename}")
        except Exception as error:
            log.error(error)
            raise

    def getScraper(self):
        try:
            return getattr(
                importlib.import_module(
                    f"...plugins.scrapers.{self.type_}.{self.websitename}.item",
                    package=".core.scraper",
                ),
                "Scraper",
            )(link=self.link, wait=self.wait)
        except ImportError as error:
            log.critical(f"no Scraper for website {{{self.websitename}}}")
            log.error(error)

