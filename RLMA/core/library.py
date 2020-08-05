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
                self.text = self.Scraper.about["Name"]
                self.source = self.source = str(RLMAPATH / "300.png")
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
        self.source = str(RLMAPATH / "300.png")
        self.init = True

    def item_get_info(self, full=True):
        return self.Scraper.info(full=full)

    def item_add_category(self, category):
        if not isinstance(category, type("string")):
            raise ValueError(
                f"{category} must be a string not {type(category).__name__}"
            )
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
        app = App.get_running_app()
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
        self.LibraryItems.clear()
        for path in self.LibraryPaths:
            base_path = pathlib.Path(path)
            # library path
            for obj in base_path.iterdir():
                # scraper folder
                if obj.is_dir():
                    # item dir
                    logger.debug(f"adding items from {str(obj)}")
                    for item_dir in obj.iterdir():
                        try:
                            with open(
                                str(item_dir / "info" / "info.json"),
                                "r",
                                encoding="utf-8",
                            ) as JSON_FILE:
                                JSON = json.load(JSON_FILE)
                                tmp_item = LibraryItem()
                                tmp_item.item_set(json_data=JSON)
                                tmp_item.item_add_category(self.categories[0])
                                self.LibraryItems.append(tmp_item)
                        except Exception as e:
                            logger.warn(e)
        tabs_root = app.root.ids.tabs_
        # add Categories
        for category in self.categories:
            tabs_root.add_widget(LibraryCategory(text=category))

        # add Item to Categories
        for tab in tabs_root.get_tab_list():
            for Item in self.LibraryItems:
                for category in Item.categories:
                    if tab.text == category:
                        tab.tab.ids.LibraryCategoryLayout.add_widget(Item)

        tabs_root.add_widget(
            LibraryCategory(
                text=f"[size=20][font={fonts[-1]['fn_regular']}]{md_icons['pencil']}[/size][/font] Edit categories",
            )
        )

        self._make_categoriesDialog()
        self._save_library()

    def add_item(self, link, type_):
        app = App.get_running_app()
        logger.debug(f"-> called {link},{type_}")
        for item in self.LibraryItems:
            if link == item.Scraper.link:
                logger.debug(f"Item with link {link} already in library")
                return -1
        tmp_LibraryItem = LibraryItem()
        tmp_LibraryItem.item_set(link=link, type_=type_, wait=True)
        tmp_LibraryItem.item_add_category(self.categories[0])
        toast("adding item ...")
        tmp_LibraryItem.item_update()
        self.LibraryItems.append(tmp_LibraryItem)
        self._save_item((len(self.LibraryItems) - 1))
        app.refresh_callback(1.0051528999999997)
        logger.debug(
            f"added {self.LibraryItems[-1].Scraper.about['Name']} to library in category {self.LibraryItems[-1].categories}"
        )
        toast(f"added to {self.LibraryItems[-1].categories[0]} category")

    def _save_item(self, index):
        for path in self.LibraryPaths:
            base_path = pathlib.Path(path)
            item = self.LibraryItems[index]
            logger.debug(f"Saving item {item.text}")
            scraper_name = item.Scraper.websitename
            item_dir = base_path / scraper_name / item.text / "info"
            item_dir.mkdir(exist_ok=True, parents=True)
            (item_dir / "info.json").touch(exist_ok=True)
            with open(str(item_dir / "info.json"), "w", encoding="utf-8") as JSON_FILE:
                JSON_FILE.write(item.item_to_json())

    def _save_library(self, dt=None):
        for path in self.LibraryPaths:
            with open(
                str(pathlib.Path(path) / "Library.json"), "w", encoding="utf-8"
            ) as JSON_FILE:
                json = self.to_json()
                logger.debug(f"saving library")
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
            root_tab = app.root.ids.tabs_
            tab_list = root_tab.get_tab_list()
            for tab in tab_list:
                if self.active_check.text == tab.text:
                    logger.debug(f"deleting {tab.text}")
                    root_tab.remove_widget(tab)
            self.categories.pop(self.categories.index(self.active_check.text))
            self._save_library()
            self._make_categoriesDialog()
            self.active_check = None

        Clock.schedule_once(self.categoriesDialog.open)

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
                    # get the Edit Category tab
                    edit_category_tab = app.root.ids.tabs_.get_tab_list()[0]

                    # remove Edit Category tab
                    app.root.ids.tabs_.remove_widget(edit_category_tab)

                    # add new tab
                    app.root.ids.tabs_.add_widget(LibraryCategory(text=text))

                    # re-add Edit Category tab
                    app.root.ids.tabs_.add_widget(
                        LibraryCategory(
                            text=f"[size=20][font={fonts[-1]['fn_regular']}]{md_icons['pencil']}[/size][/font] Edit categories",
                        )
                    )

                    self.categories.append(str(text))
                    self._make_categoriesDialog()
                    self.added_cat = True

        self._close_dialog(instance=instance)

        Clock.schedule_once(self._save_library)
        Clock.schedule_once(self.categoriesDialog.open)

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
                    if self.add_item(link=self.itemurl, type_=self.itemtype) == -1:
                        toast("Item Already in Library")
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
