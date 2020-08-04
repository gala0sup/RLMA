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
from kivymd.toast import toast
from kivy.properties import StringProperty
from kivymd.uix.menu import MDDropdownMenu
from kivy.factory import Factory

from validator_collection import checkers


from .scraper import Scraper
from utils import RLMAPATH


# Config.set("kivy", "log_level", "debug")

logger = logging.getLogger("RLMA")


class LibraryItem(SmartTileWithLabel):
    """class for LibraryItem """

    def __init__(self, *args, **kwargs):
        # try:
        #     self.text_ = kwargs["label_text"]
        #     self.source_ = kwargs["img_source"]
        #     kwargs.pop("label_text")
        #     kwargs.pop("img_source")
        # except KeyError:
        #     logger.info(
        #         "Wrong kwargs for LibraryItem  correct LibraryItem(label_text='text',img_source='path')"
        #     )
        super().__init__(**kwargs)
        # self.text = self.text_
        # self.source = self.source_
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
        logger.debug("-> called")
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
        logger.debug("-> called")
        self.Scraper.get_info()
        self.text = self.Scraper.about["Name"]
        self.source = self.Scraper.about["CoverImage"]
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
        Config = ConfigParser.get_configparser("RLMA")

        self.LibraryPaths = ast.literal_eval(
            Config.get("LocationPaths", "LibraryPaths")
        )
        logger.debug(self.LibraryPaths)
        self.json = None
        self.ItemTypes = ["ln", "manga", "anime"]
        self.LibraryItems = []
        self.categories = []
        self.tabs = {}
        self.categoriesDialog = None
        self.added_cat = False
        self.active_check = None
        self.typedialog = None
        self.itemtype = None
        self.itemurl = None
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
        # from JSON
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

        for LibraryItem_ in self.LibraryItems:
            for category in LibraryItem_.categories:
                if category in self.tabs.keys():
                    self.tabs[category].ids.LibraryCategoryLayout.add_widget(
                        LibraryItem_
                    )

        self._make_categoriesDialog()
        self._save_library()

    def add_item(self, link, type_):
        logger.debug(f"-> called {link},{type_}")
        for item in self.LibraryItems:
            if link == item.Scraper.link:
                logger.debug(f"Item with link {link} already in library")
                return -1
        tmp_LibraryItem = LibraryItem()
        tmp_LibraryItem.item_set(link=link, type_=type_)
        tmp_LibraryItem.item_add_category("Default")
        tmp_LibraryItem.item_update()
        self.LibraryItems.append(tmp_LibraryItem)

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

    # Dialogs GUI functions from here

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

    def _ok_categoriesDialog(self, instance):
        logger.debug("-> called")
        # for obj in self.categoriesDialog.items:
        #     logger.debug(obj.text)
        self.categoriesDialog.dismiss()

    def LibraryCategoryDialogItemCallback(self, instance):
        logger.debug("-> called")
        if self.active_check == instance:
            self.active_check = None
        else:
            self.active_check = instance

    def open_categoriesDialog(self):
        self.categoriesDialog.open()

    def add_category(self, *args, **kwargs):
        logger.debug("-> called")
        app = App.get_running_app()
        dialog = MDDialog(
            title="Add New Category",
            content_cls=DialogMDTextField(hint_text="Enter New Category"),
            type="custom",
            buttons=[
                MDRectangleFlatButton(
                    text="CANCEL",
                    text_color=app.theme_cls.primary_color,
                    md_bg_color=app.theme_cls.accent_color,
                    on_release=self._close_dialog,
                ),
                MDRectangleFlatButton(
                    text="OK",
                    text_color=app.theme_cls.accent_color,
                    md_bg_color=[
                        i - j
                        for i, j in zip(app.theme_cls.primary_light, [0, 0, 0, 0.5])
                    ],
                    on_release=self._ok_add_category_dialog,
                ),
            ],
        )
        dialog.set_normal_height()
        dialog.open()

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

        Clock.schedule_once(self.categoriesDialog.open)
        app.refresh_callback(1.0051528999999997)

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

    def add_item_dialog(self):
        app = App.get_running_app()
        menu_items = [
            {"icon": "book-alphabet", "text": "LN"},
            {"icon": "book", "text": "Manga"},
            {"icon": "video", "text": "Anime"},
        ]
        dialog = MDDialog(
            title="Add New Item",
            content_cls=AddItemDialog(hint_text="Enter New Item Link"),
            type="custom",
            buttons=[
                MDRectangleFlatButton(
                    text="CANCEL",
                    text_color=app.theme_cls.primary_color,
                    md_bg_color=app.theme_cls.accent_color,
                    on_release=self._close_dialog,
                ),
                MDRectangleFlatButton(
                    text="OK",
                    text_color=app.theme_cls.accent_color,
                    md_bg_color=[
                        i - j
                        for i, j in zip(app.theme_cls.primary_light, [0, 0, 0, 0.5])
                    ],
                    on_release=self._ok_add_item_dialog,
                ),
            ],
        )
        a = Factory.AddItemDialog()

        self.typedialog = MDDropdownMenu(
            caller=a.ids.drop_item,
            items=menu_items,
            callback=self._ok_add_item_dialog,
            width_mult=4,
        )

        dialog.set_normal_height()
        dialog.open()

    def _ok_add_item_dialog(self, instance):
        logger.debug("-> called")

        for obj in instance.walk_reverse():
            if isinstance(obj, MDDialog):
                url = obj.content_cls.ids.textfield.text
                if checkers.is_url(url):
                    self.itemurl = url
                    if self.itemtype not in self.ItemTypes:
                        self.itemtype = "ln"
                    self.add_item(link=self.itemurl, type_=self.itemtype)
                    self._close_dialog(instance=instance)
                else:
                    toast("Please Enter a vaild URL")
            elif obj == self.typedialog:
                a = Factory.AddItemDialog()
                a.ids.drop_item.set_item(instance.text)
                if a.ids.drop_item.current_item not in self.ItemTypes:
                    self.itemtype = "ln"
                    logger.debug(self.itemtype)
                else:
                    self.itemtype = (a.ids.drop_item.current_item).lower()
                    logger.debug(self.itemtype)
                self.typedialog.dismiss()

    def _close_dialog(self, instance):
        # logger.debug(" -> Called")
        for obj in instance.walk_reverse():
            if isinstance(obj, MDDialog):
                obj.dismiss()
        self.added_cat = False


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

    hint_text = StringProperty("")


class AddItemDialog(BoxLayout):
    hint_text = StringProperty("")
