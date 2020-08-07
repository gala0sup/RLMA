import logging

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

logger = logging.getLogger("RLMA")


root_kv = """
Screen:
    BoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: app.title
            elevation: 10
            md_bg_color: app.theme_cls.primary_color

        MDScrollViewRefreshLayout:
            id : refresh_layout
            refresh_callback: app.refresh_callback
            root_layout : app
            MDTabs:
                id: tabs_
                lock_swiping : True
                on_tab_switch: app.on_tab_switch(*args)


    MDFloatingActionButtonSpeedDial:
        id : FloatingDial
        data : app.data
        callback : app.FloatingActionButton_callback
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
        hint_text: root.hint_text
        mode : "rectangle"
        color_mode : "custom"
        line_color_focus: app.theme_cls.primary_dark

<AddItemDialog>
    orientation: "vertical"
    MDTextField:
        id : textfield
        hint_text: root.hint_text
        mode : "rectangle"
        color_mode : "custom"
        line_color_focus: app.theme_cls.primary_dark

    MDDropDownItem:
        id: drop_item
        text: 'LN'
        on_release: app.library.typedialog.open()

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
        padding : dp(10), dp(10)
        spacing : dp(10)
<LibraryItem>
    id : Item
    elevation: 12
    size_hint: None,None
    size: "150dp", "200dp"
    radius: [(15 / self.width) * 100, ]
    RelativeLayout:
        FitImage:
            id : item_image
            source: root.source
            size_hint: None, None
            size: Item.size
            radius: Item.radius

        FitImage:
            source: root.shadow
            size_hint_y: None
            height: "250dp"
            radius: Item.radius
        MDLabel:
            font_style : "Button"
            text: root.text
            size_hint_y: None
            height: self.texture_size[1]
            x: "5dp"
            y: "10dp"
            theme_text_color : "Custom"
            text_color : [1,1,1,1]

"""


class RLMA(MDFloatLayout, MDApp):
    data = {
        "update": "Update Category",
        "all-inclusive": "Update Library",
        "plus": "Add Item",
    }

    def build(self):
        self.title = "RLMA"
        self.theme_cls.primary_palette = "Gray"
        self.theme_cls.accent_palette = "Red"
        self.root = Builder.load_string(root_kv)

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
