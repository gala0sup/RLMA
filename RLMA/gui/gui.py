from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from core.library import LibraryCategory
from core.library import LibraryItem
from core.library import Library
from kivy.metrics import dp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivy.lang import Builder

import logging

logger = logging.getLogger("RLMA")


root_kv = """

BoxLayout:
    orientation: "vertical"

    MDToolbar:
        title: app.title
        elevation: 10
        left_action_items: [["menu", lambda x: x]]
        md_bg_color: app.theme_cls.primary_color

    MDScrollViewRefreshLayout:
        id : refresh_layout
        refresh_callback: app.refresh_callback
        root_layout : app.root
        MDTabs:
            id: tabs_
            lock_swiping : True
            on_tab_switch: app.on_tab_switch(*args)

<LibraryCategoryDialogItem>
    on_release: root.set_icon(check)

    CheckboxLeftWidget:
        id: check
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
    def build(self):
        self.title = "RLMA"
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Red"
        self.root = Builder.load_string(root_kv)
        # self.refresh_layout = MDScrollViewRefreshLayout()

        # self.refresh_layout.refresh_callback = self.refresh_callback
        # self.refresh_layout.root_layout = self.root

        self.library = Library()
        # self.root.add_widget(self.refresh_layout)

        # self.library_layout = MDGridLayout(adaptive_height=True,
        #                                    padding=(dp(4), dp(4)),
        #                                    spacing=dp(4)
        #                                    )

    def on_start(self):

        self.library.do_library()
        logger.debug(self.root.ids)
        for tab_lable, tab_instance in self.library.tabs.items():
            logger.debug(f"adding {tab_lable} <======> {tab_instance}")
            self.root.ids.tabs_.add_widget(tab_instance)

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
        pass
