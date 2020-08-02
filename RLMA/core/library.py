import json
import logging
from random import choice
import pathlib
import ast

from kivy.config import ConfigParser
from kivymd.app import App
from kivymd.uix.imagelist import SmartTileWithLabel
from kivy.uix.scrollview import ScrollView
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.font_definitions import fonts
from kivymd.icon_definitions import md_icons
from kivy.clock import Clock

from .scraper import Scraper
from utils import RLMAPATH


# Config.set("kivy", "log_level", "debug")

logger = logging.getLogger("RLMA")
Config = ConfigParser.get_configparser("RLMA")


class LibraryItem(SmartTileWithLabel):
    """class for LibraryItem """

    def __init__(self, *args, **kwargs):
        try:
            self.text_ = kwargs["label_text"]
            self.source_ = kwargs["img_source"]
            kwargs.pop("label_text")
            kwargs.pop("img_source")
        except KeyError:
            logger.info(
                "Wrong kwargs for LibraryItem  correct LibraryItem(label_text='text',img_source='path')"
            )
        super().__init__(**kwargs)
        self.text = self.text_
        self.source = self.source_
        self.size_hint = None, None
        self.height = 300
        self.width = 300
        self.mipmap = True
        self.font_style = "Subtitle1"

        # logger.debug(f"LibraryItem: {self.text},{self.source}")

        self.init = False
        self.json_data = None
        self.Scraper = None
        self.wait = True
        self.Scraper = None
        self.categories = []
        # self.update()

    def on_press(self, *args, **kwargs):
        logger.debug(f"getting {self.text}")

    def item_set(self, json_data=None, link=None, type_=None, wait=True):
        self.json_data = json_data
        try:
            if self.json_data:
                self.Scraper = Scraper(
                    link=self.json_data["link"],
                    type_=self.json_data["type_"],
                    wait=self.wait,
                ).getScraper()
                self.item_from_json(data=self.json_data)
            else:
                self.Scraper = Scraper(link=link, type_=type_, wait=wait).getScraper()
            self.init = True
        except Exception as error:
            logger.critical(f"{error}")
            logger.critical("an error occured")
            raise

    def item_update(self):
        self.Scraper.get_info()
        self.init = True

    def item_get_info(self, full=True):
        return self.Scraper.info(full=full)

    def item_add_category(self, category):
        self.categories.append(category)

    def item_to_json(self):
        return self.Scraper.to_json()

    def item_from_json(self, data=None):
        if not self.init:
            self.Scraper.from_json(data=data)
        else:
            logger.debug("already set passing")
            pass


class Library:
    def __init__(self, *args, **kwargs):

        self.LibraryPaths = ast.literal_eval(
            Config.get("LocationPaths", "LibraryPaths")
        )
        logger.debug(self.LibraryPaths)
        self.json = None
        self.LibraryItems = []
        self.categories = []
        self.tabs = {}
        self.categoriesDialog = None
        self.added_cat = False
        self.active_check = None
        for path in self.LibraryPaths:
            logger.debug(path)
            json_file = pathlib.Path(path) / "Library.json"
            logger.debug(str(json_file))
            if json_file.exists():
                logger.debug(f"Json file exists")
                with open(str(json_file), "r", encoding="utf-8") as JSON_FILE:
                    self.json = json.load(JSON_FILE)
            else:
                json_file.touch()
                if not "Default" in self.categories:
                    self.categories.append("Default")

    def do_library(self, refresh=False):
        logger.info(f"Building Library")
        if self.json:
            logger.debug("setting from JSON file")
            for key, value in self.json.items():
                logger.debug(f"{key}, {value}")
                if key == "categories":
                    if len(value) < 1:
                        value.append("Default")
                    logger.debug(f"setting {key}")
                    self.categories = value
        self.tabs.clear()
        self.LibraryItems.clear()

        self.tabs = {
            tab_label: LibraryCategory(text=tab_label) for tab_label in self.categories
        }
        self.tabs["edit"] = LibraryCategory(
            text=f"[size=20][font={fonts[-1]['fn_regular']}]{md_icons['pencil']}[/size][/font] Edit categories",
        )
        img_path = str(RLMAPATH / "300.png")

        for i in range(50):
            item = LibraryItem(label_text=str(i), img_source=img_path)
            item.item_add_category(choice(self.categories))
            self.LibraryItems.append(item)

        for LibraryItem_ in self.LibraryItems:
            for category in LibraryItem_.categories:
                if category in self.tabs.keys():
                    self.tabs[category].ids.LibraryCategoryLayout.add_widget(
                        LibraryItem_
                    )
        self._make_categoriesDialog()
        self._save_library()

    def add_category(self, *args, **kwargs):
        logger.debug("-> called")
        app = App.get_running_app()
        dialog = MDDialog(
            title="Add New Category",
            content_cls=DialogMDTextField(),
            type="custom",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    text_color=app.theme_cls.primary_color,
                    on_release=self._close_dialog,
                ),
                MDFlatButton(
                    text="OK",
                    text_color=app.theme_cls.primary_color,
                    on_release=self._ok_add_category_dialog,
                ),
            ],
        )
        dialog.set_normal_height()
        dialog.open()

    def add_item(self, link, type_):
        for item in self.LibraryItems:
            if link == item.Scraper.link:
                logger.debug(f"Item with link {link} already in library")
                return -1
            else:
                tmp_LibraryItem = LibraryItem()
                tmp_LibraryItem.item_set(link=link, type_=type_)

    def _save_library(self):
        for path in self.LibraryPaths:
            with open(
                str(pathlib.Path(path) / "Library.json"), "w", encoding="utf-8"
            ) as JSON_FILE:
                json = self.to_json()
                logger.debug(f"saving json {json}")
                JSON_FILE.write(json)

    def to_json(self):
        return json.dumps({"categories": self.categories})

    def _close_dialog(self, instance):
        # logger.debug(" -> Called")
        for obj in instance.walk_reverse():
            if isinstance(obj, MDDialog):
                obj.dismiss()
        self.added_cat = False

    def _ok_categoriesDialog(self, instance):
        for obj in self.categoriesDialog.items:
            logger.debug(obj.text)
        self._close_dialog(instance=self.categoriesDialog)

    def _ok_add_category_dialog(self, instance):
        app = App.get_running_app()
        Clock.schedule_once(self.categoriesDialog.dismiss)
        for obj in instance.walk_reverse():
            if isinstance(obj, MDDialog):
                text = obj.content_cls.ids.textfield.text
                if text in self.categories:
                    pass
                else:
                    logger.debug(f"adding {text}")
                    self.categories.append(str(text))
                    self._make_categoriesDialog()
                    self.added_cat = True

        self._close_dialog(instance=instance)
        Clock.schedule_once(self.categoriesDialog.open)
        self._save_library()
        app.refresh_callback(1.0051528999999997)

    def open_categoriesDialog(self):
        self.categoriesDialog.open()

    def _make_categoriesDialog(self):
        logger.debug("-> called")
        app = App.get_running_app()
        self.categoriesDialog = MDDialog(
            title="Choose Category",
            type="confirmation",
            items=[
                LibraryCategoryDialogItem(text=category) for category in self.categories
            ],
            buttons=[
                MDRectangleFlatButton(
                    text="CANCEL",
                    text_color=app.theme_cls.primary_color,
                    md_bg_color=app.theme_cls.accent_color,
                    on_release=self._close_dialog,
                ),
                MDRectangleFlatButton(
                    text="Add Category",
                    text_color=app.theme_cls.primary_dark,
                    md_bg_color=app.theme_cls.primary_light,
                    on_release=self.add_category,
                ),
                MDRectangleFlatButton(
                    text="Delete Selected",
                    text_color=app.theme_cls.primary_dark,
                    md_bg_color=app.theme_cls.primary_light,
                    on_release=self.del_category,
                ),
                MDRaisedButton(
                    text="OK",
                    text_color=app.theme_cls.accent_color,
                    md_bg_color=[
                        i - j
                        for i, j in zip(app.theme_cls.primary_light, [0, 0, 0, 0.5])
                    ],
                    on_release=self._ok_categoriesDialog,
                ),
            ],
        )
        self.categoriesDialog.set_normal_height()

    def del_category(self, instance):
        logger.debug("-> called")
        app = App.get_running_app()
        Clock.schedule_once(self.categoriesDialog.dismiss)
        if self.active_check != None:
            logger.debug(f"deleting {self.active_check.text}")
            self.categories.pop(self.categories.index(self.active_check.text))
            self._save_library()
            self._make_categoriesDialog()
            self.active_check = None

        Clock.schedule_once(self.categoriesDialog.open, 1)
        app.refresh_callback(1.0051528999999997)

    def LibraryCategoryDialogItemCallback(self, instance):
        logger.debug("-> called")
        if self.active_check == instance:
            self.active_check = None
        else:
            self.active_check = instance


class LibraryCategory(ScrollView, MDTabsBase):
    """category class for Library"""


class LibraryCategoryDialogItem(OneLineAvatarIconListItem):
    """Category Chosser panel"""

    divider = None

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False


class DialogMDTextField(BoxLayout):
    """DialogMDTextField"""

