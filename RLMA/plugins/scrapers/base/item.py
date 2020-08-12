"""Base class for light novel scrapers"""

import json
import logging
import pathlib
from math import ceil

from bs4 import BeautifulSoup
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.snackbar import Snackbar

from utils import request_headers

logger = logging.getLogger("RLMA")


class NotInitializedError(Exception):
    """when info is called before get_info"""

    def __init__(self, message="info() is called before calling get_info('link')"):
        self.message = message
        super().__init__(self.message)


class about_dict(object):
    def __init__(self):
        self.dict_ = {
            "CoverImage": None,
            "Name": None,
            "Chapters": None,
            "Author": None,
            "Status": None,
            "Release": None,
            "Updated": None,
            "Summary": None,
            "extra": None,
        }

    def __str__(self):
        return self.dict_.__str__()

    def __setitem__(self, key, value):
        if key not in self.dict_.keys():
            raise KeyError("no New key Allowed")

        self.dict_[key] = value

    def __getitem__(self, key):
        return self.dict_[key]

    def __len__(self):
        return len(self.dict_)

    def keys(self):
        return self.dict_.keys()

    def update(self, *args, **kwargs):
        raise NotImplementedError("use 'dict['key'] = value' instead")

    def items(self):
        return self.dict_.items()

    def for_json(self):
        return self.dict_

    def from_json(self, data=None):
        if not data:
            raise ValueError("No data provided")
        try:
            raw_json = data
        except Exception as error:
            logger.critical(f"{error}")
            raise

        for key, value in raw_json.items():
            logger.debug(f"\tsetting up {key}")
            self.dict_[key] = value


class chapter_dict(object):
    """{chapter_number:{chapter_name:chapter_link}}"""

    def __init__(self):
        self.dict_ = {}

    def __str__(self):
        return self.dict_.__str__()

    def __setitem__(self, key, value):
        if type(value) == dict:
            if len(value) == 1:
                if key not in self.dict_.keys():

                    if len(value[next(iter(value.keys()))]) > 0:
                        self.dict_[key] = value
                    else:
                        raise ValueError("link cannot be empty")

                else:

                    if len(value[next(iter(value.keys()))]) > 0:
                        for k in value.keys():
                            self.dict_[key][k] = "".join(value[k])
                    else:
                        raise ValueError("link cannot be empty")
            else:
                raise ValueError(
                    (
                        "\ncannot assign multiple keys to a single key "
                        + f"({{{key}:{value}}}"
                        + f"\ncorrect format {{chapter_number:{{chapter_name:chapter_link}}}}"
                    )
                )
        else:
            raise ValueError(
                f"expected dict got {type(value).__name__} \n use dict['key'] = {{'key':'value'}}"
            )

    def __getitem__(self, key):
        if key not in self.dict_.keys():
            raise KeyError(f"{key} not defined")
        return self.dict_[key]

    def __len__(self):
        return len(self.dict_)

    def keys(self):
        return self.dict_.keys()

    def items(self):
        return self.dict_.items()

    def for_json(self):
        return self.dict_

    def from_json(self, data=None):
        try:
            raw_json = data
        except Exception as error:
            logger.critical(f"{error}")
            raise
        logger.debug("setting up Chapter List")
        for key, value in raw_json.items():
            self.dict_[key] = value


class Base:
    def __init__(self, LibraryItemInstance=None, link=None, wait=False, _log_level=0):

        if link:
            self.initialized = True
        else:
            self.initialized = False
        self._log_level = _log_level
        self.type_ = None
        self.webpage = None
        self.prased_webpage = None
        self.temp0 = None
        self.temp = None
        self.link = link
        self.chapter_link = None
        self.about = about_dict()
        self.chapter_list = chapter_dict()
        self.final_link = None
        logger.debug(type(LibraryItemInstance))
        self.LibraryItemInstance = LibraryItemInstance
        self.wait = wait

    def _get_webpage(self, wait=False):
        if not self.initialized:
            logger.error("class not Initialised")
            raise NotInitializedError(
                "class not Initialised Try calling get_info('link')"
            )
        else:
            try:
                logger.debug("getting webpage (%s)", self.link)
                self.webpage = UrlRequest(
                    self.link,
                    debug=True,
                    on_success=self.UrlRequest_success,
                    on_progress=self.UrlRequest_progress,
                    req_headers=request_headers,
                )
                if not wait:
                    if self.wait:
                        self.webpage.wait()
                else:
                    self.webpage.wait()
            except Exception as error:
                logger.error(error)
                logger.warning(
                    "There was some Problem in getting the webpage (%s)", self.link
                )
            finally:
                if self.wait:
                    logger.debug(
                        "Status Code Returned by %s is %s",
                        self.link,
                        self.webpage.resp_status,
                    )

    def _parse_webpage(self, req, result):
        if not self.initialized:
            logger.error("class not Initialised")
            raise NotInitializedError(
                "class not Initialised Try calling get_info('link')"
            )
        else:
            try:
                logger.debug("prasing webpage (%s)", self.link)
                self.prased_webpage = BeautifulSoup(result, "lxml")
                logger.debug("prased webpage")
                self._set_info()
            except Exception as error:
                logger.error(error)
                logger.error("unable to prase webpage")
                raise

    def _set_info(self):
        logger.debug("settings up vars")
        pass

    def get_info(self, link=None):
        if not self.initialized:
            if not link:
                logger.critical("Link is needed aborting....")
                raise ValueError
            self.link = link
            self.initialized = True

        logger.info("getting info of (%s)", self.link)
        try:
            self._get_webpage()

        except Exception as error:
            logger.error(error)
            logger.error("unable to retrive info of (%s)", self.link)
            raise

    def _get_chapter(self):
        tmp_link = self.link
        try:
            logger.info(f"getting chapter {self.chapter_link}")
            self.link = self.chapter_link
            self._get_webpage()
            self.link = tmp_link
        except Exception as error:
            self.link = tmp_link
            logger.error(error)
            raise

    def info(self, full=False):
        if not self.initialized:
            raise NotInitializedError()
        else:
            if full:
                return json.dumps(
                    {
                        "type_": self.type_,
                        "link": self.link,
                        "about": self.about.for_json(),
                        "chapter_list": self.chapter_list.for_json(),
                    }
                )
            else:
                return json.dumps(
                    {
                        "type_": self.type_,
                        "link": self.link,
                        "about": self.about.for_json(),
                    }
                )

    def chapters(self):
        if not self.initialized:
            raise NotInitializedError(
                "Chapters() called before calling get_info('link')"
            )
        else:
            return json.dumps({**self.chapter_list})

    def chapter(self, chapter_number=None, chapter_name=None, chapter_link=None):
        if not self.initialized:
            raise NotInitializedError("Called chapter() before calling get_info()")
        try:
            if chapter_number == None and chapter_name == None and chapter_link == None:
                raise ValueError(
                    "At least one of (chapter_number or chapter_name or chapter_link) must be provided"
                )
            else:
                if chapter_number != None:
                    if chapter_number in self.chapter_list.keys():
                        self.chapter_link = self.chapter_list[chapter_number][
                            next(iter(self.chapter_list[chapter_number]))
                        ]
                    else:
                        raise KeyError(f"{chapter_number} does not exists")
                elif chapter_name != None:
                    found = False
                    for k, v in self.chapter_list.items():
                        if chapter_name == next(iter(v.keys())):
                            self.chapter_link = self.chapter_list[k][chapter_name]
                            found = True
                    if not found:
                        raise KeyError(
                            f"No chapter by the name {chapter_name} in {self.about['Name']}"
                        )
                else:
                    found = False
                    for k, v in self.chapter_list.items():
                        if chapter_link == v[next(iter(v.keys()))]:
                            self.chapter_link = self.chapter_list[k][
                                next(iter(v.keys()))
                            ]
                            found = True
                    if not found:
                        raise KeyError(
                            f"No chapter by the name {chapter_name} in {self.about['Name']}"
                        )
            return json.dumps(self._get_chapter())
        except ValueError as error:
            logger.error(error)
        except KeyError as error:
            logger.error(error)

    def to_json(self, update=False):
        if update:
            self.get_info()
        return self.info(full=True)

    def from_json(self, data=None):
        logger.info(f"setting up using JSON")
        if data == None:
            logger.critical(f"pass data=")
            raise ValueError
        if data:
            try:
                logger.info(f"setting up using JSON data")
                raw_json = data
            except Exception as error:
                logger.critical(f"{error}")
                raise

        for key in raw_json.keys():
            if key == "link":
                self.link = raw_json[key]
            elif key == "about":
                self.about.from_json(raw_json[key])
            elif key == "chapter_list":
                self.chapter_list.from_json(raw_json[key])

    # Callbacks are defined here

    def UrlRequest_success(self, req, result):
        self._parse_webpage(req=req, result=result)

    def UrlRequest_progress(self, req, current_size, total_size):
        logger.debug("getting %s ....", self.link)
