from kivy.clock import Clock
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from core.library import LibraryCategory
from core.library import LibraryItem
from core.library import Library
from kivy.metrics import dp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.tab import MDTabsBar
from kivymd.uix.tab import MDTabsMain
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivy.lang import Builder
from kivymd.utils import asynckivy

import logging

logger = logging.getLogger("RLMA")


root_kv = """
BoxLayout:
    orientation: "vertical"

    MDToolbar:
        title: app.title
        elevation: 10
        md_bg_color: app.theme_cls.primary_color

    MDFloatLayout:
        MDScrollViewRefreshLayout:
            id : refresh_layout
            refresh_callback: app.refresh_callback
            root_layout : app
            MDTabs:
                id: tabs_
                lock_swiping : True
                on_tab_switch: app.on_tab_switch(*args)


        MDFloatingActionButtonSpeedDial:
            data : app.data
            rotation_root_button: True



<LibraryCategoryDialogItem>
    on_release: root.set_icon(check)

    CheckboxLeftWidget:
        id: check
        on_active : app.library.LibraryCategoryDialogItemCallback(root)
        group: "check" 

<DialogMDTextField>
    MDTextField:
        id : textfield
        hint_text: "Enter New Category"
        mode : "rectangle"
        color_mode : "custom"
        line_color_focus: app.theme_cls.primary_dark


<LibraryCategory>:
    id : tab_
    do_scroll_x: False
    effect_cls : "OpacityScrollEffect"
    scroll_type : ["bars", "content"]
    bar_pos_y : "right"    
    bar_color : app.theme_cls.primary_dark
    bar_inactive_color : app.theme_cls.primary_color
    bar_width : 10
    MDStackLayout:
        id : LibraryCategoryLayout
        adaptive_height : True
        padding : dp(4), dp(4)
        spacing : dp(4)
"""


class RLMA(MDFloatLayout, MDApp):
    data = {"update": "Update Category", "all-inclusive": "Update Library"}

    def build(self):
        self.title = "RLMA"
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Red"
        self.root = Builder.load_string(root_kv)
        # self.refresh_layout = MDScrollViewRefreshLayout()

        # self.refresh_layout.refresh_callback = self.refresh_callback
        # self.refresh_layout.root_layout = self.root

        # self.root.add_widget(self.refresh_layout)

        # self.library_layout = MDGridLayout(adaptive_height=True,
        #                                    padding=(dp(4), dp(4)),
        #                                    spacing=dp(4)
        #                                    )

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
            for tab_lable, tab_instance in self.library.tabs.items():
                logger.debug(f"adding {tab_lable} <======> {tab_instance}")
                self.root.ids.tabs_.add_widget(tab_instance)

        asynckivy.start(set_RLMA())

    def refresh_RLMA(self):
        async def set_RLMA():
            self.library.do_library(refresh=True)
            await asynckivy.sleep(0)
            for tab_lable, tab_instance in self.library.tabs.items():
                logger.debug(f"adding {tab_lable} <======> {tab_instance}")
                self.root.ids.tabs_.add_widget(tab_instance)

        asynckivy.start(set_RLMA())

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Called when switching tabs.

        :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
        :param instance_tab: <__main__.Tab object>;
        :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
        :param tab_text: text or name icon of tab;
        """
        # if instance_tabinstance_tabs.ids.carousel.slides:
        #     logger.debug(obj)
        #     if obj == instance_tab:
        #         logger.debug("got it")
        #         self.library.add_category()

        if instance_tabs.ids.carousel.slides.index(instance_tab) == (
            len(instance_tabs.ids.carousel.slides) - 1
        ):
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
