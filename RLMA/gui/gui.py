import logging
import pathlib

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivymd.uix.tab import MDTabsBar, MDTabsBase, MDTabsMain
from kivymd.utils import asynckivy

from core.library import Library, LibraryCategory, LibraryItem
from utils import RLMAPATH

logger = logging.getLogger("RLMA")


class RLMA(MDFloatLayout, MDApp):
    def build(self):
        self.title = "RLMA"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Red"
        # Load all .kv files from gui/kv_file
        for file in (RLMAPATH / "gui" / "kv_files").iterdir():
            # Check if the file is kv file
            if file.suffix == ".kv":
                try:
                    # try to Load file
                    if file.stem == "rlma":
                        # assign self.root
                        self.root = Builder.load_file(str(file))
                    else:
                        Builder.load_file(str(file))
                except Exception as error:
                    logger.critical("An error occured %s", error)
                    raise

    def on_start(self):
        from core.config import RlmaConfig

        Config = RlmaConfig()
        Config.run()
        RlmaConfig.Config.write()
        self.library = Library()
        self.set_RLMA()

    def set_RLMA(self):
        async def set_RLMA():
            self.library.do_library()
            await asynckivy.sleep(0)

        asynckivy.start(set_RLMA())

    def refresh_RLMA(self):
        async def set_RLMA():
            self.library.do_library(refresh=True)
            await asynckivy.sleep(0)

        asynckivy.start(set_RLMA())

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Called when switching tabs.

        :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
        :param instance_tab: <__main__.Tab object>;
        :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
        :param tab_text: text or name icon of tab;
        """
        if instance_tab.tab_alias == "edit":
            self.library.categoriesDialog.open()

    def refresh_callback(self, *args):

        logger.debug(f"-> called")

        def refresh_callback(interval):
            for obj in self.root.ids.tabs_.ids.carousel.slides:
                obj.clear_widgets()

            for obj in self.root.ids.tabs_.ids.tab_bar.walk():
                if isinstance(obj, MDGridLayout):
                    # logger.debug(i)
                    obj.clear_widgets()

            if self.x == 0:
                self.x, self.y = 15, 30
            else:
                self.x, self.y = 0, 15

            self.refresh_RLMA()

            self.root.ids.refresh_layout.refresh_done()

        Clock.schedule_once(refresh_callback, 1)

    def FloatingActionButton_callback(self, instance):
        icon = instance.icon
        if icon == "plus":
            """Call Add_item Dialog in library"""
            self.library.add_item_dialog()
        elif icon == "all-inclusive":
            """update whole library"""
            pass
        elif icon == "update":
            """update current category"""
            pass

    def multi_callback(self, instance):
        try:
            for obj in instance.walk_reverse():
                if obj == self.drop:
                    self.root.ids.drop_item.set_item(instance.text)
                    self.drop.dismiss()
        except:
            pass
